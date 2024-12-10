This repo uses an implementation of FeUdal Networks by lweitkamp:
https://github.com/lweitkamp/feudalnets-pytorch

Installation instructions:

1. conda create -n HRL python=3.10
2. conda activate HRL
3. conda install pytorch pygame gym matplotlib tensorboard

Play with dummy bots:
python main.py --mode human_with_dummies --num_dummies 5

Running simulations:
python main.py --mode basic_bot_test --num_dummies 20 --high 4 --low 1 --num_games 400 --frames_per_game 1000 --spatialgrid_size 70

Benchmarking bots:
python main.py --mode basic_bot_benchmarking --num_dummies 20 --num_games 3 --frames_per_game 50000

Training DQN bot:
python main.py --mode train_double_dqn --num_dummies 100 --dummy_lvl 0 --num_episodes 600 --episodes_to_save 200 --batch_size 32 --update_target_every 100 --max_frames_per_episode 3600 --checkpoint_path "checkpoints/double_dqn_model_lvl0_episode_400.pth"

python main.py --mode train_double_dqn --num_dummies 40 --dummy_lvl 1 --num_episodes 600 --episodes_to_save 100 --batch_size 32 --update_target_every 100 --max_frames_per_episode 3000 --checkpoint_path "checkpoints/double_dqn_model_lvl0_episode_400.pth"


Testing DQN bot against dummies:
python main.py --mode dqn_vs_dummies --num_dummies 100 --dummy_lvl 0 --visualize --checkpoint_path "checkpoints/ddqn_400eps_lvl0.pth"

Training FeUdal Bot:
python main_feudal.py --max-steps 6400 --num-steps 20
(16*num_steps before checking if saving (every tenth of max-steps))
python main_feudal.py --max-steps 1280000 --num-steps 2000
(16 episodes: 32000, so 64 episodes 128000 and it finally saves)

(Change so that it takes the lvl0 bot)

Testing Feudal Bot against dummies:
python main.py --mode feudal_vs_dummies --num_dummies 100 --dummy_lvl 0 --visualize --checkpoint_path "feudal_checkpoints/Agario_baseline_steps=1280000.pt"

TODO:

- Applying DQN
   - Fix the epsilon: mostly high for easy env, mid for mid env, mid-low for hard env
   - Multithreading (work for Colab?)
   - Train all night (3 settings)

- Applying Feudal Networks
   - Figure out the environment replacement
   - Fix any bugs
   - Figure out benchmarking

- Write the report 
   - Do this at the same time as the experiments
   - Record videos of the bots playing against each other
-----------------------------------------

Done already:
- added player's capability to get discrete actions
- deleted food ejecting (or just ignored it, the bots can't food eject for now)
- Change game to not receive mode. Doesn't matter. (game, main) Now it receives how many non-dummy players.
  Sets the initial mass of dummies to rand(50, 200) and non-dummies to 100.
- Improve the part of code that resets players. Just build a set and take them down

- Think about how you will test this with many controllers (simple enough. initialize the game, the networks, 
     take the function for every player, plug in, get actions, put actions)

- Add parameters.
- Import repo in Satori. Run all experiments to determine optimal spatial cell size (went terribly, satori is so slow)

- Multi player preparation: 
   
   - Add a mode to return information respect to a player. (game get observation, player index i)
      a. How to get the normalizing? What dimensions are the agents seeing?
      b. Once this is done, will the game be slow?

- Build environment:
   - Design it in paper. 
      - Define rewards
      - Define actions: include 0 for no op, and make sure it makes sense if it's the center
      - Think about how to make two bots compete with each other:
         a. The environment passes as first 16 arguments the locations/masses of the cells. (12 by default)
         b. So for different players, just reformat the space. Include the self player first.
   - Tradeoff: fixed players or not?
      a. Actions: 0-15 for directions, 16-31 for splitting, 32 for no op.
      b. Rewards: Let it be the size difference between frames.
      c. Observation space: 
         - Cells (with masses) inside the frame, max 20-30. Ask what to do if not max. Set them inside the circle?
         - Food inside the frame as well. 
         - Viruses inside the frame as well.

- Benchmarking
   - Logging each player's mass through time
   - Log each player's average size, max size. (Check how the players are indexed in Game)

---------------------------------
optional:

- Prepare the repo
   - Rewrite the README
   - Clean the code: replace get_state with get_state_for_drawing
   - Add game parameters where possible

   - Parameters for the location of the checkpoint

- the movement equations are done per frame, so if FPS is changed then the equations change a lot. maybe correct this. not necessary.
- How to multitrain? Create two (or many) environments. Covering a game object. Augment the previous scores for the rewards. (This is hard. Maybe later)