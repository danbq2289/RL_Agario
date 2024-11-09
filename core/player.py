import math
import config
game_config = config.GameConfig()

player_initial_mass = 10
class Cell:
    def __init__(self, x, y, color, name, mass):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.mass = mass

        self.radius = game_config.RADIUS_FROM_MASS(self.mass)
        self.speed = game_config.SPEED_FROM_RADIUS(self.radius)

    def move(self, px, py):
        """Move the cell towards the point px, py."""
        dx = px - self.x
        dy = py - self.y
        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            new_x = self.x + (dx/magnitude) * self.speed
            new_y = self.y + (dy/magnitude) * self.speed

            self.x = max(self.radius/2, min(new_x, game_config.GAME_WIDTH - self.radius/2))
            self.y = max(self.radius/2, min(new_y, game_config.GAME_HEIGHT - self.radius/2))

        # Passive mass loss
        self.mass = max(game_config.MIN_PLAYER_MASS, self.mass*(1 - game_config.MASS_LOSS_RATE / game_config.FPS))
    def grow(self, amount):
        """Increase the cell's size and mass."""
        self.mass += amount
        self.mass = min(self.mass, 22500)

        self.radius = game_config.RADIUS_FROM_MASS(self.mass)
        self.speed = game_config.SPEED_FROM_RADIUS(self.radius)
        # print(self.mass)
        # print(self.radius)    
    def can_eat(self, other):
        """Check if this player can eat another player or food item."""
        return self.mass > other.mass * 1.2

    def distance_to(self, other):
        """Calculate the distance to another object."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def intersects_with(self, other):
        """Check if this player is strongly intersecting/covering another object, so it can eat it if big enough"""
        return self.distance_to(other) < self.radius - other.radius * 0.4

    def get_state(self):
        """Return the current state of the cell."""
        return {
            'x': self.x,
            'y': self.y,
            'color': self.color,
            'name': self.name,
            'mass': self.mass,
            'radius': self.radius,
        }


class Player:
    def __init__(self, x, y, color, name, mass=game_config.INITIAL_PLAYER_MASS):
        # self.color = color
        # self.name = name
        self.cells = [Cell(x, y, color, name, mass)]

    def move(self, px, py):
        """Move the player's cells towards the point px, py."""
        for cell in self.cells:
            cell.move(px, py)

    def eat(self, other):
        """Attempt to eat another object (food or player cell)."""
        for cell in self.cells:
            if cell.can_eat(other) and cell.intersects_with(other):
                cell.grow(other.mass)
                return True
        return False

    def can_eat(self, other):
        """Check if any of the player's cells can eat the other object."""
        return any(cell.can_eat(other) for cell in self.cells)

    def get_state(self):
        """Return the current state of the player."""
        cell_states = [cell.get_state() for cell in self.cells]
        # weighted average
        center_x = 0
        center_y = 0
        for cell in cell_states:
            center_x += cell["x"] * cell["mass"]
            center_y += cell["y"] * cell["mass"]

        total_mass = sum([cell['mass'] for cell in cell_states])
        center_x, center_y = center_x/total_mass, center_y/total_mass
        return {
            "total_size": sum([cell['radius'] for cell in cell_states]),
            "total_mass": sum([cell['mass'] for cell in cell_states]),
            "x": center_x,
            "y": center_y,
            "cells": cell_states
        }

    # def __repr__(self):
    #     return f"Player(id={self.id}, x={self.x:.2f}, y={self.y:.2f}, radius={self.radius:.2f}, score={self.score})"
    
