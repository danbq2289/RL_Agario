Installation instructions:

1. conda create -n HRL python=3.12
2. conda activate HRL
3. pip install pygame

so far there's the option to play with dummy bots:
python main.py --mode human_with_dummies --num_dummies 5

TODO:
- use a config in game
- add the player modality to get discrete actions
- delete food ejecting

- set up environment

- define get_env_state, augment it with velocity of every cell (is this necessary tho? it might as well be the Markovian property. Include value function computing for other cells?)

- train a basic RL bot:

- DQN

- A2C/Policy gradient:

- Feudal:


What kind of insight do you seek -- about the algorithms or about the environments?
Do you simply want to know if FeUdal Networks outperforms DQN / policy gradient on Agar.io?

Want to know:
- What kind of strategies the bots get with FeUdal networks. How to parse the Manager's goals?
- See if statistically it's better.
- See what works/doesn't work for DQN and A2C.


optional:
- more order in config: pass params to game, player instead of creating a config (might not be good)
- the action right now is (mouse pos, do_splitting), might change to either mouse_pos or do_splitting, but this is harder to work with

- the movement equations are done per frame, so if FPS is changed then the equations change a lot. maybe correct this. not necessary.
- clean config, ask how to best do it