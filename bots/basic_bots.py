import random
import math
import config

game_config = config.GameConfig()

"""
This dummy bot goes in roughly straight lines, regardless of who's ahead. 
Changes directions periodically.
"""
class DummyBot:
    def __init__(self, name):
        self.name = name
        self.counter = 0
        self.target = (0, 0)

    def get_action(self, game_state):
        # Extract the bot's position from the game state
        bot_state = next((player for player in game_state['players'] if player['name'] == self.name), None)
        players_cells_pos_and_masses = []
        for player in game_state['players']:
            if player['name'] == self.name:
                continue
            for cell in player['cells']:
                pass

        
        if not bot_state:
            raise Exception("bot name not found in game")

        bot_x, bot_y = bot_state['x'], bot_state['y']

        if self.counter <= 0:
            # Choose new point target
            self.target = (random.randint(0, game_config.GAME_WIDTH), random.randint(0, game_config.GAME_HEIGHT))
            self.counter = 420  # changes goal every 7 seconds
        self.counter -= 1

        # Generate a random target point within a certain radius
        dx = self.target[0] - bot_x
        dy = self.target[1] - bot_y

        angle = math.atan2(dy, dx) + random.uniform(-math.pi, math.pi)/18

        target_x = bot_x + 1000 * math.cos(angle)
        target_y = bot_y + 1000 * math.sin(angle)

        split = random.random() < 0.0005
        feed = random.random() < 0.001

        return (target_x, target_y, split, feed)