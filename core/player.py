import math
import config
import random

game_config = config.GameConfig()

player_initial_mass = 10
class Cell:
    def __init__(self, x, y, color, name, mass, vx=0, vy=0):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.mass = mass
        self.update_radius_and_speed()

        self.external_vx = vx
        self.external_vy = vy

        self.merge_time = game_config.MERGE_TIME_FROM_MASS(mass)

    def move(self, px, py):
        """
        Move the cell towards the point px, py,
        being influenced by the external velocities
        """
        dx = px - self.x
        dy = py - self.y
        magnitude = math.sqrt(dx**2 + dy**2)

        # Apply external velocity
        new_x = self.x + self.external_vx
        new_y = self.y + self.external_vy
        
        self.external_vx *= 0.9  # Decay velocity
        self.external_vy *= 0.9
        
        if magnitude > 0:
            new_x += (dx/magnitude) * self.speed
            new_y += (dy/magnitude) * self.speed

            self.x = max(self.radius/2, min(new_x, game_config.GAME_WIDTH - self.radius/2))
            self.y = max(self.radius/2, min(new_y, game_config.GAME_HEIGHT - self.radius/2))

        # Passive mass loss
        self.mass = max(game_config.MIN_PLAYER_MASS, self.mass*(1 - game_config.MASS_LOSS_RATE / game_config.FPS))

        # Reduce cooldowns
        self.merge_time = max(0, self.merge_time - 1/game_config.FPS)

    def grow(self, amount):
        """Increase the cell's size and mass."""
        self.mass += amount
        self.update_radius_and_speed()

    def update_radius_and_speed(self):
        self.radius = game_config.RADIUS_FROM_MASS(self.mass)
        self.speed = game_config.SPEED_FROM_RADIUS(self.radius)

    def can_eat(self, other):
        """Check if this player can eat another player or food item."""
        return self.mass > other.mass * game_config.MASS_FACTOR_EAT_ANOTHER

    def distance_to(self, other):
        """Calculate the distance to another object."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def intersects_with(self, other):
        """Check if this player is strongly intersecting/covering another object, so it can eat it if big enough"""
        return self.radius >= other.radius and self.distance_to(other) < self.radius - other.radius * game_config.CLOSENESS_FACTOR

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
    
    def split(self, px, py):
        if self.mass >= game_config.SPLIT_MASS_THRESHOLD:
            new_mass = self.mass / 2
            self.mass = new_mass
            self.radius = game_config.RADIUS_FROM_MASS(self.mass)
            self.speed = game_config.SPEED_FROM_RADIUS(self.radius)

            dx = px - self.x
            dy = py - self.y
            
            magnitude = math.sqrt(dx**2 + dy**2)
            if magnitude == 0:
                # default to splitting to the right
                dx, dy, magnitude = 1, 0, 1
            split_speed = game_config.SPLIT_SPEED
            vx = (dx / magnitude) * split_speed
            vy = (dy / magnitude) * split_speed
            new_cell = Cell(self.x, self.y, self.color, self.name, new_mass, vx, vy)
            self.merge_time = game_config.MERGE_TIME_FROM_MASS(self.mass)
            return new_cell
        return None


class Player:
    def __init__(self, x, y, color, name, mass=game_config.INITIAL_PLAYER_MASS):
        self.name = name
        self.color = color
        self.cells = [Cell(x, y, color, name, mass)]
        self.split_cooldown = 0

    def reset(self):
        """Use this function to respawn the player"""
        self.cells = [Cell(random.randint(0, game_config.GAME_WIDTH), random.randint(0, game_config.GAME_HEIGHT), self.color, self.name, game_config.INITIAL_PLAYER_MASS)]

    def move(self, px, py):
        """Move the player's cells towards the point px, py,
        """
        for cell in self.cells:
            cell.move(px, py)

    def eat(self, other):
        """Attempt to eat another object (food or player cell)."""
        for cell in self.cells:
            if cell.can_eat(other) and cell.intersects_with(other):
                cell.grow(other.mass)
                self.regulate_cell_masses()
                return True
        return False
    
    def regulate_cell_masses(self):
        """Regulates masses so that the total mass doesn't exceed the maximum.
        Modifies cells masses, so it is crucial that we call cell.update_radius_and_speed().
        """
        total_mass = sum([cell.mass for cell in self.cells])
        if total_mass > game_config.MAX_PLAYER_MASS:
            mass_to_regulate = total_mass - game_config.MIN_PLAYER_MASS * len(self.cells)
            mass_goal = game_config.MAX_PLAYER_MASS - game_config.MIN_PLAYER_MASS * len(self.cells)
            if mass_goal <= 0:
                raise Exception("It seems that MAX_PLAYER_MASS <= MIN_PLAYER_MASS * MAX_AMOUNT_CELLS, which is nonsensical. Please correct this.")
            for cell in self.cells:
                cell.mass = game_config.MIN_PLAYER_MASS + (cell.mass - game_config.MIN_PLAYER_MASS) * mass_goal/mass_to_regulate
                cell.update_radius_and_speed()
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
    
    def try_split(self, px, py):
        if self.split_cooldown > 0:
            return

        new_cells = []
        for cell in sorted(self.cells, key=lambda c: c.mass, reverse=True):
            if len(self.cells) + len(new_cells) >= game_config.MAX_AMOUNT_CELLS:
                break
            new_cell = cell.split(px, py)
            if new_cell:
                new_cells.append(new_cell)

        self.cells.extend(new_cells)
        if new_cells:
            self.split_cooldown = game_config.SPLIT_COOLDOWN

    def handle_self_collisions(self):
        for i, cell1 in enumerate(self.cells):
            for cell2 in self.cells[i+1:]:
                dx = cell2.x - cell1.x
                dy = cell2.y - cell1.y
                distance = math.sqrt(dx**2 + dy**2)
                touching_distance = cell1.radius + cell2.radius - min(cell1.radius, cell2.radius)*0.05
                if distance < touching_distance:
                    if cell1.merge_time == 0 and cell2.merge_time == 0: 
                        if (cell1.intersects_with(cell2) or cell2.intersects_with(cell1)):
                            # Merge cells
                            cell1.mass += cell2.mass
                            cell1.radius = game_config.RADIUS_FROM_MASS(cell1.mass)
                            cell1.speed = game_config.SPEED_FROM_RADIUS(cell1.radius)
                            self.cells.remove(cell2)
                    else:
                        # Push cells apart
                        if distance > 0:
                            overlap = touching_distance - distance
                            angle = math.atan2(dy, dx)
                            cell1.x -= math.cos(angle) * overlap / 2
                            cell1.y -= math.sin(angle) * overlap / 2
                            cell2.x += math.cos(angle) * overlap / 2
                            cell2.y += math.sin(angle) * overlap / 2

    def update(self, action):
        px, py, do_split = action
        if do_split:
            self.try_split(px, py)

        self.split_cooldown = max(0, self.split_cooldown - 1/game_config.FPS)
        self.move(px, py)
        self.handle_self_collisions()