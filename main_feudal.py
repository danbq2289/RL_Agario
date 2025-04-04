import argparse
import torch

from utils import take_action
from feudalnet import FeudalNetwork, feudal_loss
from storage import Storage
# from logger import Logger
import config
from agar_env import AgarEnv
game_config = config.GameConfig()
import numpy as np
import pickle

import threading
from queue import Queue

parser = argparse.ArgumentParser(description='Feudal Nets')
# GENERIC RL/MODEL PARAMETERS
parser.add_argument('--lr', type=float, default=0.0005,
                    help='learning rate')
parser.add_argument('--env-name', type=str, default='Agario',
                    help='gym environment name')
parser.add_argument('--num-workers', type=int, default=16,
                    help='number of parallel environments to run')
parser.add_argument('--num-steps', type=int, default=400,
                    help='number of steps the agent takes before updating')
parser.add_argument('--max-steps', type=int, default=int(1e8),
                    help='maximum number of training steps in total')
parser.add_argument('--cuda', type=bool, default=True,
                    help='Add cuda')
parser.add_argument('--grad-clip', type=float, default=5.,
                    help='Gradient clipping (recommended).')
parser.add_argument('--entropy-coef', type=float, default=0.01,
                    help='Entropy coefficient to encourage exploration.')
parser.add_argument('--mlp', type=int, default=1,
                    help='toggle to feedforward ML architecture')

# SPECIFIC FEUDALNET PARAMETERS
parser.add_argument('--time-horizon', type=int, default=10,
                    help='Manager horizon (c)')
parser.add_argument('--hidden-dim-manager', type=int, default=256,
                    help='Hidden dim (d)')
parser.add_argument('--hidden-dim-worker', type=int, default=16,
                    help='Hidden dim for worker (k)')
parser.add_argument('--gamma-w', type=float, default=0.99,
                    help="discount factor worker")
parser.add_argument('--gamma-m', type=float, default=0.999,
                    help="discount factor manager")
parser.add_argument('--alpha', type=float, default=0.5,
                    help='Intrinsic reward coefficient in [0, 1]')
parser.add_argument('--eps', type=float, default=int(1e-5),
                    help='Random Gausian goal for exploration')
parser.add_argument('--dilation', type=int, default=10,
                    help='Dilation parameter for manager LSTM.')

# EXPERIMENT RELATED PARAMS
parser.add_argument('--run-name', type=str, default='baseline',
                    help='run name for the logger.')
parser.add_argument('--seed', type=int, default=0,
                    help='reproducibility seed.')

args = parser.parse_args()

def worker(env, action, result_queue):
    result = env.step(action)
    result_queue.put(result)

def experiment(args):

    save_steps = list(torch.arange(0, int(args.max_steps),
                                   int(args.max_steps) // 10).numpy())

    # logger = Logger(args.run_name, args)
    cuda_is_available = torch.cuda.is_available() and args.cuda
    device = torch.device("cuda" if cuda_is_available else "cpu")
    args.device = device

    torch.manual_seed(args.seed)
    if cuda_is_available:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

    # envs = make_envs('Agar', args.num_workers)
    envs = [AgarEnv(num_dummy_bots=30, dummy_lvl=3, max_frames_per_episode=None) 
            for _ in range(args.num_workers)]
    feudalnet = FeudalNetwork(
        num_workers=args.num_workers,
        input_dim=(game_config.OBSERVATION_SIZE,),
        hidden_dim_manager=args.hidden_dim_manager,
        hidden_dim_worker=args.hidden_dim_worker,
        n_actions=game_config.ACTION_SPACE,
        time_horizon=args.time_horizon,
        dilation=args.dilation,
        device=device,
        mlp=args.mlp,
        args=args)
    
    checkpoint_path = "feudal_checkpoints/feudal_botlv2.pt"
    checkpoint = torch.load(checkpoint_path)
    feudalnet.load_state_dict(checkpoint['model'], strict=True)

    optimizer = torch.optim.RMSprop(feudalnet.parameters(), lr=args.lr,
                                    alpha=0.99, eps=1e-5)
    goals, states, masks = feudalnet.init_obj()

    x = np.array([env.reset() for env in envs])
    step = 0

    total_rewards = []
    while step < args.max_steps:

        # Detaching LSTMs and goals
        feudalnet.repackage_hidden()
        goals = [g.detach() for g in goals]
        storage = Storage(size=args.num_steps,
                          keys=['r', 'r_i', 'v_w', 'v_m', 'logp', 'entropy',
                                's_goal_cos', 'mask', 'ret_w', 'ret_m',
                                'adv_m', 'adv_w'])
        episode_reward = np.zeros(args.num_workers)
        for _ in range(args.num_steps):
            action_dist, goals, states, value_m, value_w \
                 = feudalnet(x, goals, states, masks[-1])

            # Take a step, log the info, get the next state
            action, logp, entropy = take_action(action_dist)

            # Create threads and result queue
            threads = []
            result_queue = Queue()
            for env, action_singular in zip(envs, action):
                thread = threading.Thread(target=worker, args=(env, action_singular, result_queue))
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Collect results
            data = [result_queue.get() for _ in range(args.num_workers)]
            x = np.array([datapoint[0] for datapoint in data])
            reward = np.array([datapoint[1] for datapoint in data])
            done = np.array([datapoint[2] for datapoint in data])

            episode_reward += reward

            # print(x)
            # print(reward)
            # print(done)
            # raise Exception("stop here")
            # x, reward, done, info = envs.step(action)
            # logger.log_episode(info, step)

            mask = torch.FloatTensor(1 - done).unsqueeze(-1).to(args.device)
            masks.pop(0)
            masks.append(mask)

            storage.add({
                'r': torch.FloatTensor(reward).unsqueeze(-1).to(device),
                'r_i': feudalnet.intrinsic_reward(states, goals, masks),
                'v_w': value_w,
                'v_m': value_m,
                'logp': logp.unsqueeze(-1),
                'entropy': entropy.unsqueeze(-1),
                's_goal_cos': feudalnet.state_goal_cosine(states, goals, masks),
                'm': mask
            })

            step += args.num_workers

        total_rewards += episode_reward.tolist()
        with torch.no_grad():
            *_, next_v_m, next_v_w = feudalnet(
                x, goals, states, mask, save=False)
            next_v_m = next_v_m.detach()
            next_v_w = next_v_w.detach()

        print(f"16 episodes have completed, step: {step}")
        optimizer.zero_grad()
        loss, loss_dict = feudal_loss(storage, next_v_m, next_v_w, args)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(feudalnet.parameters(), args.grad_clip)
        optimizer.step()
        # logger.log_scalars(loss_dict, step)
        # print(save_steps)
        if len(save_steps) > 0 and step > save_steps[0]:
            print(f"Saving. step: {step}")
            print(save_steps)
            torch.save({
                'model': feudalnet.state_dict(),
                'args': args,
                'processor_mean': feudalnet.preprocessor.rms.mean,
                'optim': optimizer.state_dict()},
                f'feudal_checkpoints/{args.env_name}_{args.run_name}_step={step}.pt')
            save_steps.pop(0)

            # Save total rewards as pickle file
            with open(f"feudal_rewards/{args.env_name}_{args.run_name}_rewards_step={step}.pkl", "wb") as f:
                pickle.dump(total_rewards, f)

    for env in envs:
        env.close()
    torch.save({
        'model': feudalnet.state_dict(),
        'args': args,
        'processor_mean': feudalnet.preprocessor.rms.mean,
        'optim': optimizer.state_dict()},
        f'feudal_checkpoints/{args.env_name}_{args.run_name}_steps={step}.pt')
    
    with open(f"feudal_rewards/{args.env_name}_{args.run_name}_rewards_final.pkl", "wb") as f:
        pickle.dump(total_rewards, f)


def main(args):
    args.seed = 0
    experiment(args)


if __name__ == '__main__':
    main(args)
