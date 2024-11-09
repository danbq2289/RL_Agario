import random
import math

class DummyBot:
    def __init__(self, name):
        self.name = name

    def get_action(self, game_state):
        # Extract the bot's position from the game state
        bot_state = next((player for player in game_state['players'] if player['cells'][0]['name'] == self.name), None)
        
        if not bot_state:
            raise Exception("bot name not found in game")

        bot_x, bot_y = bot_state['x'], bot_state['y']

        # Generate a random target point within a certain radius
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, 200)  # Random radius up to 200 pixels
        target_x = bot_x + radius * math.cos(angle)
        target_y = bot_y + radius * math.sin(angle)

        # Decide whether to split (0.05% chance per frame)
        split = random.random() < 0.0005

        return (target_x, target_y, split)