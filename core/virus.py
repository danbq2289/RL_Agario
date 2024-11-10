# virus.py
import math
import random
import config

game_config = config.GameConfig()

class Virus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.mass = game_config.VIRUS_MASS
        self.radius = game_config.RADIUS_FROM_MASS(self.mass)
        self.color = (30, 225, 30)  # Green color for viruses
        self.spikes = 20  # Number of spikes on the virus

    def get_state(self):
        return {
            'x': self.x,
            'y': self.y,
            'mass': self.mass,
            'radius': self.radius,
            'color': self.color,
            'spikes': self.spikes
        }

    def draw_points(self):
        points = []
        for i in range(self.spikes * 2):
            angle = i * math.pi / self.spikes
            r = self.radius * (0.9 if i % 2 == 0 else 1.1)
            x = self.x + r * math.cos(angle)
            y = self.y + r * math.sin(angle)
            points.append((x, y))
        return points