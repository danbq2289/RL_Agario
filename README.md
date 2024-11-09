Installation instructions:

1. conda create -n HRL python=3.12
2. conda activate HRL
3. pip install pygame


TODO:

iteration 0 (done):
- create MVP: something that runs

- visualize pipeline

iteration 1: (done)
- create camera, pass in to game state

iteration 2: actually design the game.

- move with mouse (done)
- speed issues (done)

- square limits, collision with it (done)

- food (done)
- passive mass loss(done)


- get speed, initial size, food mass, etc. from config. (done)
- weighted average position in player (done)

- player with multiple cells (done)
- splitting (done)


- self-collission (done)

- multiple players
- eating other players

- viruses
- W foods
- duplicating viruses


optional:
- more order in config: pass params to game, player instead of creating a config (might not be good)
- the action right now is (mouse pos, do_splitting), might change to either mouse_pos or do_splitting, but this is harder to work with

- the movement equations are done per frame, so if FPS is changed then the equations change a lot. maybe correct this. not necessary.