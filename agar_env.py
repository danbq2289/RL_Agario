import gym
from gym import spaces
import numpy as np
from core.game import Game
from bots.basic_bots import DummyBot
import config

game_config = config.GameConfig()

class AgarEnv(gym.Env):
    def __init__(self, num_dummy_bots=12):
        super(AgarEnv, self).__init__()
        self.num_dummy_bots = num_dummy_bots
        self.game = None
        self.player_idx = 0  # Assuming the main player is always at index 0
        self.dummy_bots = None

        # Define action and observation space
        self.action_space = spaces.Discrete(33)  # 16 directions, 16 directions plus split, one for "center"
        self.observation_space = spaces.Box(low=0, high=1, shape=(game_config.OBSERVATION_SIZE,), dtype=np.float32)

    def step(self, action):
        # Convert action to game format
        main_player_action = self._action_to_game_format(action)
        
        # Get actions for dummy bots
        dummy_actions = [bot.get_action(self.game) for bot in self.dummy_bots]
        
        # Combine main player action with dummy bot actions
        all_actions = [main_player_action] + dummy_actions
        
        # Update game state
        reset_players = self.game.update(all_actions)
        
        # Get new state, reward, and done flag
        state = self.game.get_RL_state(self.player_idx)
        reward = self._calculate_reward()
        done = self._is_episode_done(reset_players)
        
        return state, reward, done, {}

    def reset(self):
        player_names = ["MainPlayer"] + [f"DummyBot{i}" for i in range(self.num_dummy_bots)]
        self.game = Game(player_names, non_dummy_players=1)
        self.dummy_bots = [DummyBot(name) for name in player_names[1:]]
        return self.game.get_RL_state(self.player_idx)

    def _action_to_game_format(self, action):
        # Convert discrete action to game format (px, py, do_split, do_feed)
        biggest_cell = max(self.game.players[self.player_idx].cells, key=lambda c: c.radius)
        if action == 32:  # "Center" action
            return (biggest_cell.x, biggest_cell.y, False, False)
        else:
            angle = 2 * np.pi * (action % 16) / 16
            offset = game_config.DISCRETE_FACTOR_DISTANCE * biggest_cell.radius
            px = biggest_cell.x + offset * np.cos(angle)
            py = biggest_cell.y + offset * np.sin(angle)
            do_split = action >= 16
            return (px, py, do_split, False)

    def _calculate_reward(self):
        return sum(cell.mass for cell in self.game.players[self.player_idx].cells)

    def _is_episode_done(self, reset_players):
        return self.game.players[self.player_idx].name in reset_players