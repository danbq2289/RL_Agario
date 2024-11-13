import config
game_config = config.GameConfig()

class Pellet:
    def __init__(self, x, y, color, mass):
        self.x = x
        self.y = y
        self.color = color
        self.mass = mass
        self.radius = game_config.RADIUS_FROM_MASS(mass)

    def get_state(self):
        """Return the current state of the cell."""
        return {
            'x': self.x,
            'y': self.y,
            'color': self.color,
            'mass': self.mass,
            'radius': self.radius
        }
