Installation instructions:

1. conda create -n HRL python=3.12
2. conda activate HRL
3. pip install pygame

so far there's the option to play with dummy bots:
python main.py --mode human_with_dummies --num_dummies 3

TODO:
- viruses
- feeding others
- duplicating viruses

- defining a better, non dummy bot

- set up environment

- train a basic RL bot.

- Use DQN.


optional:
- more order in config: pass params to game, player instead of creating a config (might not be good)
- the action right now is (mouse pos, do_splitting), might change to either mouse_pos or do_splitting, but this is harder to work with

- the movement equations are done per frame, so if FPS is changed then the equations change a lot. maybe correct this. not necessary.