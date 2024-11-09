class Pellet:
    def __init__(self, x, y, color, mass, radius):
        self.x = x
        self.y = y
        self.color = color
        self.mass = mass
        self.radius = radius

    def get_state(self):
        """Return the current state of the cell."""
        return {
            'x': self.x,
            'y': self.y,
            'color': self.color,
            'mass': self.mass,
            'radius': self.radius
        }
