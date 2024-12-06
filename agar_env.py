import gym
from gym import spaces
import numpy as np
from core.game import Game
import config

OBSERVATION_SIZE = 100  # set this in config
class AgarEnv(gym.Env):
    def __init__(self):
        super(AgarEnv, self).__init__()
        self.game_config = config.GameConfig()
        self.game = Game(["DQN_Agent"], self.game_config, mode="single_with_dummies")
        
        # Define action and observation space
        self.action_space = spaces.Discrete(32)  # 16 directions, 16 directions plus split
        
        # Observation space will be a flattened array of normalized values
        self.observation_space = spaces.Box(low=0, high=1, shape=(OBSERVATION_SIZE,), dtype=np.float32)

    def step(self, action):
        # Convert action to game format
        game_action = self._action_to_game_format(action)
        
        # Update game state
        self.game.update([game_action])
        
        # Get new state, reward, and done flag
        state = self._get_observation()
        reward = self._calculate_reward()
        done = self._is_episode_done()
        
        return state, reward, done, {}

    def reset(self):
        self.game = Game(["DQN_Agent"], self.game_config, mode="human_with_dummies")
        return self._get_observation()

    def _action_to_game_format(self, action):
        # Convert discrete action to game action format
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        if action < 8:
            dx, dy = directions[action]
            player = self.game.players[0]
            px = player.cells[0].x + dx * 100
            py = player.cells[0].y + dy * 100
            return (px, py, False, False)
        else:
            return (player.cells[0].x, player.cells[0].y, True, False)

    def _get_observation(self):
        # Convert game state to normalized observation
        player = self.game.players[0]
        state = self.game.get_state()
        
        obs = []
        # Normalize player position
        obs.extend([player.cells[0].x / self.game_config.GAME_WIDTH, 
                    player.cells[0].y / self.game_config.GAME_HEIGHT])
        
        # Add normalized information about nearby food, viruses, and other players
        # This part needs to be implemented based on your specific requirements
        
        return np.array(obs, dtype=np.float32)

    def _calculate_reward(self):
        # Implement reward calculation
        # For example, reward could be based on mass gained or lost
        return 0

    def _is_episode_done(self):
        # Implement episode termination condition
        return False