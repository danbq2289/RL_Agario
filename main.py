import argparse
import time
import matplotlib
import matplotlib.pyplot as plt
import pygame
from core.game import Game
from visualization.pygame_renderer import PygameRenderer
from bots.basic_bots import DummyBot
import pickle
from collections import defaultdict
import config
import numpy as np
from agar_env import AgarEnv
from training.ddqn import DoubleDQNAgent
from feudalnet import FeudalNetwork
import torch
from argparse import Namespace
import multiprocessing as mp
from functools import partial

game_config = config.GameConfig()
matplotlib.use('Agg')  # Non-interactive backend

def human_play_with_dummies(n_dummies):
    if n_dummies > game_config.MAX_PLAYERS:
        raise Exception("might lag. bypass if you want (config.py line 21), but you have been warned")
    renderer = PygameRenderer(game_config)
    dummy_names = [f"dum{i}" for i in range(1, n_dummies+1)]
    
    game = Game(["Human"] + dummy_names, non_dummy_players=1)
    game_state = game.get_state() # initial game state

    dummy_bots = [DummyBot(name) for name in dummy_names]

    clock = pygame.time.Clock()

    running = True
    split_key_pressed = False
    feed_key_pressed = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # for splitting
            elif event.type == pygame.KEYDOWN:  
                split_key_pressed = event.key == pygame.K_SPACE
                feed_key_pressed = event.key == pygame.K_w
                    
        mouse_x, mouse_y = pygame.mouse.get_pos()
        action_x, action_y = renderer.screen_to_world((mouse_x, mouse_y))

        # for splitting
        if split_key_pressed:
            do_split = True
            split_key_pressed = False  # Reset the flag
        else:
            do_split = False

        # for feeding
        if feed_key_pressed:
            do_feed = True
            feed_key_pressed = False  # Reset the flag
        else:
            do_feed = False

        
        game.update([(action_x, action_y, do_split, do_feed)] + [dummy_bot.get_action(game) for dummy_bot in dummy_bots])
        game_state = game.get_state()
        renderer.render(game_state)
        clock.tick(game_config.FPS)
    renderer.close()

def basic_bot_test(n_dummies, visualize, high, low, frames_per_game, num_games, spatialgrid_size):
    # For testing the bots and measuring the processing speed.
    dummy_names = [f"dum{i}" for i in range(n_dummies)]
    dummy_bots = [DummyBot(name) for name in dummy_names]

    game_config.SPATIAL_GRID_CELL = spatialgrid_size

    time_intervals = []
    for _ in range(num_games):
        game = Game(dummy_names, non_dummy_players=0)
        max_steps = frames_per_game

        if visualize:
            renderer = PygameRenderer(game_config)
            clock = pygame.time.Clock()
            running = True
            st = time.time()
            while running and max_steps > 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                game.update([dummy_bot.get_action(game) for dummy_bot in dummy_bots])
                game_state = game.get_state()
                renderer.render(game_state)
                clock.tick(game_config.FPS)
                max_steps -= 1
            renderer.close()
            end = time.time()
            print(f"Ran in {end - st} seconds")

        else:
            st = time.time()
            while max_steps > 0:
                game.update([dummy_bot.get_action(game) for dummy_bot in dummy_bots])
                max_steps -= 1
            end = time.time()
            print(f"Ran in {end - st} seconds")

        time_intervals.append(end - st)

        
    plt.hist(time_intervals, bins=50, range=(low, high), color='blue', edgecolor='black')

    # Add labels and title
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title(f"games: {num_games} , gridsize:{game_config.SPATIAL_GRID_CELL}, mean:{sum(time_intervals)/len(time_intervals):.4f}, <{low}: {len([x for x in time_intervals if x < low])}, >{high}: {len([x for x in time_intervals if x > high])}")

    # Show the plot
    print(f"Amount of values less than {low}: {len([x for x in time_intervals if x < low])}")
    print(f"Amount of values more than {high}: {len([x for x in time_intervals if x > high])}")
    print(f"Grid size used:{game_config.SPATIAL_GRID_CELL}")
    
    plt.savefig(f'timetest_gridsize{game_config.SPATIAL_GRID_CELL}_{low}_{high}.png')

def basic_bot_benchmarking(n_dummies, frames_per_game, num_games):
    dummy_names = [f"dum{i}" for i in range(n_dummies)]
    dummy_bots = [DummyBot(name) for name in dummy_names]
    
    player_size_evolution = defaultdict(list)
    
    
    for game_num in range(1, num_games+1):
        game = Game(dummy_names, non_dummy_players=0)
        current_sizes = defaultdict(list)
        player_death_flags = {f"dum{i}": False for i in range(n_dummies)}

        for frame in range(1, frames_per_game+1):
            if frame % 10000 == 0:
                print(f"Game {game_num}/{num_games}, Frame {frame}/{frames_per_game}")
            
            for player in game.players:
                total_size = sum(cell.mass for cell in player.cells)
                current_sizes[player.name].append(total_size)
            
            reset_players = game.handle_collisions()
            # if reset_players:
            #     print(f"Dead: {reset_players}")
            
            for reset_player in reset_players:
                player_size_evolution[reset_player].append(current_sizes[reset_player])
                current_sizes[reset_player] = []
                player_death_flags[reset_player] = True

            game.update([dummy_bot.get_action(game) for dummy_bot in dummy_bots])
        
        # Append remaining sizes and mark as incomplete if necessary
        for player_name, sizes in current_sizes.items():
            if sizes:
                if len(sizes) < frames_per_game:
                    sizes.append(None)  # Mark as incomplete
                player_size_evolution[player_name].append(sizes)

        dead_player_idxs = [i for i in range(n_dummies) if player_death_flags[f"dum{i}"]]
        
        print(f"Dead players for game {game_num}: {len(dead_player_idxs)}")
    
    # Save the dictionary to a pickle file
    filename = f'benchmarking/dummies_benchmrk_{n_dummies}_frames{frames_per_game}_games{num_games}.pkl'
    with open(filename, 'wb') as f:
        pickle.dump(dict(player_size_evolution), f)

    print(f"Player size evolution data saved to {filename}")

    
def train_episode(agent, num_dummies, dummy_lvl, max_frames_per_episode, episode):
    env = AgarEnv(num_dummy_bots=num_dummies, dummy_lvl=dummy_lvl, max_frames_per_episode=max_frames_per_episode)
    state = env.reset()
    total_reward = 0
    done = False
    frames = 0
    experiences = []
    
    while not done:
        frames += 1
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        experiences.append((state, action, reward, next_state, done))
        state = next_state
        total_reward += reward
    
    env.close()
    return episode, total_reward, frames, experiences

def train_double_dqn(num_dummies, dummy_lvl, num_episodes=1000, batch_size=32, update_target_every=100, max_frames_per_episode=3600, checkpoint_path=None):
    print("Training with the args:")
    print(f"num_dummies: {num_dummies}")
    print(f"dummy_lvl: {dummy_lvl}")
    print(f"num_episodes: {num_episodes}")
    print(f"max_frames_per_episode: {max_frames_per_episode}")
    print(f"batch_size: {batch_size}")
    print(f"update_target_every: {update_target_every}")

    env = AgarEnv(num_dummy_bots=num_dummies, dummy_lvl=dummy_lvl, max_frames_per_episode=max_frames_per_episode)
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    agent = DoubleDQNAgent(state_size, action_size)
    if checkpoint_path is not None:
        agent.load(checkpoint_path)

    # Create a pool of workers
    num_processes = mp.cpu_count() * 2 // 3
    pool = mp.Pool(processes=num_processes)

    # Partial function for multiprocessing
    train_func = partial(train_episode, agent, num_dummies, dummy_lvl, max_frames_per_episode)

    total_rewards = []
    for i in range(0, num_episodes, num_processes):
        episodes_to_run = min(num_processes, num_episodes - i)
        results = pool.map(train_func, range(i, i + episodes_to_run))

        for episode, total_reward, frames, experiences in results:
            total_rewards.append(total_reward)

            for exp in experiences:
                agent.remember(*exp)

            if len(agent.memory) > batch_size:
                agent.replay(batch_size)

            agent.decay_epsilon()

            if episode % update_target_every == 0:
                agent.update_target_model()

            print(f"Episode: {episode+1}/{num_episodes}, Frames: {frames}, Total Reward: {total_reward}, Epsilon: {agent.epsilon:.2f}")

        if (i + episodes_to_run) % 20 == 0:
            agent.save(f"checkpoints/ddqn_{i+episodes_to_run}eps_lvl{dummy_lvl}.pth")
            # Save total rewards as pickle file
            with open(f"rewards/ddqn_rewards_{i+episodes_to_run}eps_lvl{dummy_lvl}.pkl", "wb") as f:
                pickle.dump(total_rewards, f)

    # Save final total rewards
    with open(f"rewards/ddqn_rewards_final_{num_episodes}eps_lvl{dummy_lvl}.pkl", "wb") as f:
        pickle.dump(total_rewards, f)

    pool.close()
    pool.join()
    env.close()

def dqn_vs_dummies(num_dummies, dummy_lvl, visualize, checkpoint_path):
    # Set up the environment
    env = AgarEnv(num_dummy_bots=num_dummies, dummy_lvl=dummy_lvl, max_frames_per_episode=None)
    env.reset()
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n

    # Load the trained DQN model
    agent = DoubleDQNAgent(state_size, action_size)
    agent.load(checkpoint_path)
    agent.epsilon = 0  # Set epsilon to 0 for deterministic actions

    # Set up visualization if enabled
    if visualize:
        renderer = PygameRenderer(game_config)
        clock = pygame.time.Clock()

    # Set up the game
    game = env.game
    dummy_bots = env.dummy_bots

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get DQN action
        state = env.game.get_RL_state(env.player_idx)
        action = agent.act(state)
        
        # Convert DQN action to game format
        dqn_action = env._action_to_game_format(action)

        # Get actions for dummy bots
        dummy_actions = [bot.get_action(game) for bot in dummy_bots]

        # Combine DQN action with dummy bot actions
        all_actions = [dqn_action] + dummy_actions

        # Update game state
        reset_players = game.update(all_actions)

        # Render the game if visualization is enabled
        if visualize:
            game_state = game.get_state()
            renderer.render(game_state)
            clock.tick(game_config.FPS)

        # Check if the episode is done
        if env._is_episode_done(reset_players):
            break

    if visualize:
        renderer.close()

    
def feudal_vs_dummies(num_dummies, dummy_lvl, visualize, checkpoint_path):
    # Set up the environment
    env = AgarEnv(num_dummy_bots=num_dummies, dummy_lvl=dummy_lvl, max_frames_per_episode=None)
    env.reset()
    
    # Get state size and action size
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    
    dummy_args = Namespace(
    lr=0.0005,
    env_name='Agario',
    num_workers=1,  # We only need one worker for evaluation
    num_steps=400,
    max_steps=int(1e8),
    cuda=True,
    grad_clip=5.,
    entropy_coef=0.01,
    mlp=1,
    time_horizon=10,
    hidden_dim_manager=256,
    hidden_dim_worker=16,
    gamma_w=0.99,
    gamma_m=0.999,
    alpha=0.5,
    eps=int(1e-5),
    dilation=10,
    run_name='baseline',
    seed=0,
    device='cuda' if torch.cuda.is_available() else 'cpu'
    )
    
    # Load the trained Feudal Network
    feudal_net = FeudalNetwork(
        num_workers=1,  # We only need one worker for evaluation
        input_dim=(state_size,),
        hidden_dim_manager=256,  # Adjust as needed
        hidden_dim_worker=16,  # Adjust as needed
        n_actions=action_size,
        time_horizon=10,  # Adjust as needed
        dilation=10,  # Adjust as needed
        device='cuda' if torch.cuda.is_available() else 'cpu',
        mlp=1,  # Adjust based on your model architecture
        args=dummy_args  # You might need to create a dummy args object
    )
    
    checkpoint = torch.load(checkpoint_path)
    feudal_net.load_state_dict(checkpoint['model'], strict=True)
    feudal_net.eval()
    
    # Initialize goals, states, and masks
    goals, states, masks = feudal_net.init_obj()
    
    # Set up visualization if enabled
    if visualize:
        renderer = PygameRenderer(game_config)
        clock = pygame.time.Clock()
    
    # Set up the game
    game = env.game
    dummy_bots = env.dummy_bots
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Get Feudal Network action
        state = env.game.get_RL_state(env.player_idx)
        state = torch.FloatTensor(state).unsqueeze(0).to("cpu")
        
        with torch.no_grad():
            action_dist, goals, states, _, _ = feudal_net(state, goals, states, masks[-1])
        
        # Sample action from the distribution
        action = torch.multinomial(action_dist, 1).item()
        
        # Convert Feudal Network action to game format
        feudal_action = env._action_to_game_format(action)
        
        # Get actions for dummy bots
        dummy_actions = [bot.get_action(game) for bot in dummy_bots]
        
        # Combine Feudal Network action with dummy bot actions
        all_actions = [feudal_action] + dummy_actions
        
        # Update game state
        reset_players = game.update(all_actions)
        
        # Render the game if visualization is enabled
        if visualize:
            game_state = game.get_state()
            renderer.render(game_state)
            clock.tick(game_config.FPS)
        
        # Check if the episode is done
        if env._is_episode_done(reset_players):
            break
    
    if visualize:
        renderer.close()
    

if __name__ == "__main__":
    mp.set_start_method('spawn', force=True)
    parser = argparse.ArgumentParser(description="Agar.io RL Environment")
    parser.add_argument("--mode", default="human_with_dummies")
    parser.add_argument("--num_dummies", type=int)
    parser.add_argument("--visualize", action="store_true")
    parser.add_argument("--high")
    parser.add_argument("--low")
    parser.add_argument("--frames_per_game")
    parser.add_argument("--num_games")
    parser.add_argument("--spatialgrid_size")

    # Training
    parser.add_argument("--num_episodes", type=int, default=1000)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--update_target_every", type=int, default=100, help="Update target network every n episodes")
    parser.add_argument("--dummy_lvl", type=int)
    parser.add_argument("--max_frames_per_episode", type=int)
    parser.add_argument("--checkpoint_path")
    
    args = parser.parse_args()

    if args.mode == "human_with_dummies":
        human_play_with_dummies(args.num_dummies)
    elif args.mode == "basic_bot_test":
        basic_bot_test(args.num_dummies, visualize=args.visualize,
                       high=int(args.high), low=int(args.low), frames_per_game=int(args.frames_per_game),
                       num_games=int(args.num_games), spatialgrid_size=int(args.spatialgrid_size))
    elif args.mode == "basic_bot_benchmarking":
        basic_bot_benchmarking(args.num_dummies, frames_per_game=int(args.frames_per_game),
                       num_games=int(args.num_games))

    elif args.mode == "train_double_dqn":
        train_double_dqn(num_dummies=args.num_dummies, 
                        dummy_lvl=args.dummy_lvl,
                        num_episodes=args.num_episodes, 
                        batch_size=args.batch_size, 
                        update_target_every=args.update_target_every,
                        max_frames_per_episode=args.max_frames_per_episode,
                        checkpoint_path=args.checkpoint_path)
        
    elif args.mode == "dqn_vs_dummies":
        dqn_vs_dummies(num_dummies=args.num_dummies, dummy_lvl=args.dummy_lvl, 
                        visualize=args.visualize, checkpoint_path=args.checkpoint_path)

    elif args.mode == "feudal_vs_dummies":
        feudal_vs_dummies(num_dummies=args.num_dummies, dummy_lvl=args.dummy_lvl, 
                        visualize=args.visualize, checkpoint_path=args.checkpoint_path)
    else:
        raise Exception("Mode not supported")