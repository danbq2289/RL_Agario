import random
import math
import config

game_config = config.GameConfig()

"""
At level 1:
This dummy bot goes in roughly straight lines, regardless of what's ahead. 
Changes directions periodically.

At level 2:
In addition, if player with big mass is nearby, it runs away, and splits to escape if needed.

At level 3:
In addition, if player with small mass is nearby, chases it and splits to capture if it's possible.
"""
class DummyBot:
    def __init__(self, name, lvl=3):
        self.name = name
        self.counter = 0
        self.target = (0, 0)
        self.lvl = lvl

    def get_action(self, game_state):
        # Extract the bot's position from the game state
        bot_state = next((player for player in game_state['players'] if player['name'] == self.name), None)
        if not bot_state:
            raise Exception("bot name not found in game")
        
        if self.lvl >= 2:
            # If player with big mass is nearby, run away / split
            for cell in sorted(bot_state['cells'], key=lambda c: c['mass'], reverse=True):
                for player in game_state['players']:
                    if player['name'] == self.name:
                        continue
                    for other_cell in player['cells']:
                        distance_sq = (cell['x'] - other_cell['x'])**2 + (cell['y'] - other_cell['y'])**2
                        if distance_sq < 500000:
                            if other_cell['mass'] > game_config.MASS_FACTOR_EAT_ANOTHER*cell['mass']:
                                # Run away
                                self.target = (2*cell['x'] - other_cell['x'], 2*cell['y'] - other_cell['y'])
                                return (*self.target, other_cell['mass'] > 2*game_config.MASS_FACTOR_EAT_ANOTHER*cell['mass'] and distance_sq < 360000, False)

        if self.lvl >= 3:        
            # If player with small mass is nearby, chase/split
            for cell in sorted(bot_state['cells'], key=lambda c: c['mass'], reverse=True):
                for player in game_state['players']:
                    if player['name'] == self.name:
                        continue
                    for other_cell in player['cells']:
                        distance_sq = (cell['x'] - other_cell['x'])**2 + (cell['y'] - other_cell['y'])**2
                        if distance_sq < 500000: # 500^2
                            if cell['mass'] > game_config.MASS_FACTOR_EAT_ANOTHER*other_cell['mass']:
                                # Chase
                                self.target = (other_cell['x'], other_cell['y'])
                                return (*self.target, cell['mass'] > 2*game_config.MASS_FACTOR_EAT_ANOTHER*other_cell['mass'] and distance_sq < 250000, False)


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

        split = False # random.random() < 0.0005
        feed = False # random.random() < 0.001

        return (target_x, target_y, split, feed)