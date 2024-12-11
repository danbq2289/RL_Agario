This repo uses an implementation of FeUdal Networks by lweitkamp:
https://github.com/lweitkamp/feudalnets-pytorch

Installation instructions:

1. conda create -n HRL python=3.10
2. conda activate HRL
3. conda install pytorch pygame gym matplotlib tensorboard

Play with dummy bots:
python main.py --mode human_with_dummies --num_dummies 30

Running simulations:
python main.py --mode basic_bot_test --num_dummies 20 --high 4 --low 1 --num_games 400 --frames_per_game 1000 --spatialgrid_size 70

Benchmarking bots:
python main.py --mode basic_bot_benchmarking --num_dummies 20 --num_games 3 --frames_per_game 50000

Training DQN bot:
python main.py --mode train_double_dqn --num_dummies 100 --dummy_lvl 0 --num_episodes 600 --episodes_to_save 200 --batch_size 32 --update_target_every 100 --max_frames_per_episode 3600 --checkpoint_path "checkpoints/double_dqn_model_lvl0_episode_400.pth"

Testing DQN bot against dummies:
python main.py --mode dqn_vs_dummies --num_dummies 40 --dummy_lvl 1 --visualize --checkpoint_path "checkpoints/ddqn_800eps_lvl1.pth"

python main.py --mode dqn_vs_dummies --num_dummies 30 --dummy_lvl 2 --visualize --checkpoint_path "checkpoints/ddqn_1280eps_lvl2.pth"

Training FeUdal Bot:
python main_feudal.py --max-steps 1280000 --num-steps 2000
(16*num_steps before checking if saving (every tenth of max-steps))

Testing Feudal Bot against dummies:
python main.py --mode feudal_vs_dummies --num_dummies 30 --dummy_lvl 3 --visualize --checkpoint_path "feudal_checkpoints/Agario_baseline_steps=1920000.pt"