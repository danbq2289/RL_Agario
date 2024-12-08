Installation instructions:

1. conda create -n HRL python=3.12
2. conda activate HRL
3. pip install pygame

so far there's the option to play with dummy bots:
python main.py --mode human_with_dummies --num_dummies 5

done so far:
- added player's capability to get discrete actions
- deleted food ejecting (or just ignored it, the bots can't food eject for now)
- Change game to not receive mode. Doesn't matter. (game, main) Now it receives how many non-dummy players.
  Sets the initial mass of dummies to rand(50, 200) and non-dummies to 100.
- Improve the part of code that resets players. Just build a set and take them down

- Think about how you will test this with many controllers (simple enough. initialize the game, the networks, 
     take the function for every player, plug in, get actions, put actions)

TODO:
- Benchmarking preparation:

   - With or without visualization, find how many frames you can run per second/minute. Try:
         a. Using game state normally (done)
         b. Modifying the basic bots to use game only

         f. Compare

         c. Further modifications
            - TODO: Optimize basic bot code (index of dummy, for example)
      
   - basic_bot_test (with and without visualization), and plot the total size.

   

   - Plot the size evolution. Try:
      a. All frames
      b. Skipped frames
      c. First episode
      d. Max size in each episode

   - Then, formalize this in an object augmented to the game that appends the total size.

- Multi player preparation: 
   
   - Add a mode to return information respect to a player. (game get observation, player index i)
      a. How to get the normalizing? What dimensions are the agents seeing?
      b. Once this is done, will the game be slow?

- Build environment:
   - Design it in paper. 
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

- Applying DQN
   - See if you can train multiple bots at the same time. That would be awesome.
   - See if you need a buffer, or how you should implement it.
   - See how long the training will be. If too long, just reduce the epochs or something.


- Applying Feudal Networks
   - Figure out the environment replacement
   - Fix any bugs
   - Figure out benchmarking


- Write the report 
   - Do this at the same time as the experiments
   - Record videos of the bots playing against each other

- Prepare the repo
   - Cite the guy that implemented FUN
   - Rewrite the README
   - Clean the code: replace get_state with get_state_for_drawing




- Define rewards
- Define actions: include 0 for no op, and make sure it makes sense if it's the center
- Think about how to make two bots compete with each other:
   a. The environment passes as first 16 arguments the locations/masses of the cells. (12 by default)
   b. So for different players, just reformat the space. Include the self player first.


optional:
- the movement equations are done per frame, so if FPS is changed then the equations change a lot. maybe correct this. not necessary.
- How to multitrain? Create two (or many) environments. Covering a game object. Augment the previous scores for the rewards. (This is hard. Maybe later)