# virus.py
import math
import random
import config

game_config = config.GameConfig()

class Virus:
    def __init__(self, x, y, mass=game_config.VIRUS_INITIAL_MASS, vx=0, vy=0):
        self.x = x
        self.y = y
        self.mass = mass
        self.update_radius_spikes()
        
        self.color = (30, 225, 30)  # Green color for viruses
        
        self.vx = vx
        self.vy = vy

        self.last_fed_direction = None

    def update_radius_spikes(self):
        self.radius = game_config.RADIUS_FROM_MASS(self.mass)
        self.spikes = int(self.radius/2)

    def grow(self, amount):
        self.mass += amount
        self.mass = min(self.mass, game_config.VIRUS_MAX_MASS)
        self.update_radius_spikes()

    def can_eat(self, other):
        """Check if this player can eat another player or food item."""
        return self.mass > other.mass * game_config.MASS_FACTOR_EAT_ANOTHER

    def distance_to(self, other):
        """Calculate the distance to another object."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def intersects_with(self, other):
        """Check if this player is strongly intersecting/covering another object, so it can eat it if big enough"""
        return self.radius >= other.radius and self.distance_to(other) < self.radius - other.radius * game_config.CLOSENESS_FACTOR

    def eat(self, thrown_food):
        """Attempt to eat a thrown food"""
        if self.can_eat(thrown_food) and self.intersects_with(thrown_food):
            self.grow(thrown_food.mass)
            self.last_fed_direction = (thrown_food.vx, thrown_food.vy)
            if self.last_fed_direction == (0., 0.):
                self.last_fed_direction = (self.x - thrown_food.x, self.y - thrown_food.y)
            return True
        return False
    
    def separate(self):
        if self.mass < game_config.VIRUS_SEPARATION_MASS:
            return None
        if self.last_fed_direction is None:
            raise Exception("Virus is bigger than the separation theshold without having been fed")
        
        self.mass = game_config.VIRUS_INITIAL_MASS
        self.update_radius_spikes()

        dx, dy = self.last_fed_direction
        
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude == 0:
            raise Exception("virus is separating but somehow has last_fed_direction as (0, 0)")
            # # default to splitting to the right
            # dx, dy, magnitude = 1, 0, 1
        
        split_speed = game_config.VIRUS_SPLIT_SPEED
        vx = (dx / magnitude) * split_speed
        vy = (dy / magnitude) * split_speed
        new_virus = Virus(self.x, self.y, vx=vx, vy=vy)
        return new_virus

    def get_state(self):
        return {
            'x': self.x,
            'y': self.y,
            'mass': self.mass,
            'radius': self.radius,
            'color': self.color,
            'spikes': self.spikes
        }
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.93
        self.vy *= 0.93
