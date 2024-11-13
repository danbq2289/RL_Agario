# virus.py
import math
import random
import config

game_config = config.GameConfig()

class Virus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.mass = game_config.VIRUS_MASS/2
        self.radius = game_config.RADIUS_FROM_MASS(self.mass)
        self.color = (30, 225, 30)  # Green color for viruses
        self.spikes = int(self.radius/2)

    def get_state(self):
        return {
            'x': self.x,
            'y': self.y,
            'mass': self.mass,
            'radius': self.radius,
            'color': self.color,
            'spikes': self.spikes
        }
