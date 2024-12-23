import math
import config
import random
from core.food import ThrownPellet

game_config = config.GameConfig()

class Cell:
    def __init__(self, x, y, color, name, mass, vx=0, vy=0):
        self.x = x
        self.y = y
        self.color = color
        self.name = name
        self.mass = mass
        self.update_radius_speed_merge(reset_merge=True)

        self.external_vx = vx
        self.external_vy = vy

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
        
        self.external_vx *= 0.93  # Decay velocity
        self.external_vy *= 0.93
        
        if magnitude > 0:
            new_x += (dx/magnitude) * self.speed
            new_y += (dy/magnitude) * self.speed

            self.x = max(self.radius/2, min(new_x, game_config.GAME_WIDTH - self.radius/2))
            self.y = max(self.radius/2, min(new_y, game_config.GAME_HEIGHT - self.radius/2))

        # Passive mass loss
        self.mass = max(game_config.MIN_PLAYER_MASS, self.mass*(1 - game_config.MASS_LOSS_RATE / game_config.FPS))
        self.update_radius_speed_merge()

        # Reduce cooldowns
        self.merge_time = max(0, self.merge_time - 1/game_config.FPS)

    def grow(self, amount):
        self.mass += amount
        self.update_radius_speed_merge()

    def update_radius_speed_merge(self, reset_merge=False):
        self.radius = game_config.RADIUS_FROM_MASS(self.mass)
        self.speed = game_config.SPEED_FROM_RADIUS(self.radius)
        if reset_merge:
            self.merge_time = game_config.MERGE_TIME_FROM_MASS(self.mass)

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
            self.update_radius_speed_merge(reset_merge=True)

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
            return new_cell
        return None
    
    def explode(self, max_new_cells):
        if max_new_cells <= 0:
            return []
        
        new_cells = []

        # Calculate the number of new cells we can create
        num_new_cells = min(max_new_cells, int(self.mass / game_config.MIN_PLAYER_MASS) - 1)

        # Calculate the mass for each new cell
        new_cell_mass = self.mass / (num_new_cells + 1)

        # Update the original cell's mass and properties
        self.mass = new_cell_mass
        self.update_radius_speed_merge(reset_merge=True)

        # Create new cells
        for _ in range(num_new_cells):
            # Generate a random angle for the new cell's direction
            angle = random.uniform(0, 2 * math.pi)
            
            # Calculate the velocity components
            split_speed = game_config.EXPLODE_SPEED
            vx = math.cos(angle) * split_speed
            vy = math.sin(angle) * split_speed

            # Create the new cell
            new_cell = Cell(self.x, self.y, self.color, self.name, new_cell_mass, vx, vy)
            new_cell.merge_time = game_config.MERGE_TIME_FROM_MASS(new_cell_mass)
            new_cells.append(new_cell)

        return new_cells
    
    def eject_food(self, px, py):

        dx = px - self.x
        dy = py - self.y

        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude == 0:
            # default to ejecting to the right
            dx, dy, magnitude = 1, 0, 1

        if self.mass >= game_config.MIN_PLAYER_MASS + game_config.EJECTED_MASS:

            angle = math.atan2(dy, dx) + random.uniform(-math.pi, math.pi)/12

            # Calculate velocity based on direction
            vx = math.cos(angle) * game_config.EJECTION_SPEED
            vy = math.sin(angle) * game_config.EJECTION_SPEED
            
            # Reduce cell mass
            self.mass -= game_config.EJECTED_MASS
            self.update_radius_speed_merge()

            return ThrownPellet(self.x + (dx/magnitude)*self.radius , self.y + (dy/magnitude)*self.radius, vx, vy, self.color, game_config.EJECTED_MASS)
        
        return None


class Player:
    def __init__(self, x, y, color, name, mass=game_config.INITIAL_PLAYER_MASS):
        self.name = name
        self.color = color
        self.cells = [Cell(x, y, color, name, mass)]
        self.split_cooldown = 0

        # These parameters don't take in account the pssive mass loss.
        self.mass_eaten_this_frame = 0
        self.mass_lost_this_frame = 0
        self.mass_ejected_this_frame = 0

    def reset(self):
        """Use this function to respawn the player"""
        self.cells = [Cell(random.randint(0, game_config.GAME_WIDTH), random.randint(0, game_config.GAME_HEIGHT), self.color, self.name, game_config.INITIAL_PLAYER_MASS)]

    def move(self, px, py):
        """Move the player's cells towards the point px, py,
        """
        for cell in self.cells:
            cell.move(px, py)

    def eat(self, other, virus=False, cell=None):
        """Attempt to eat another object (food or player cell). If virus, explode if eaten."""
        # Sometimes we have already a candidate cell.
        if cell is not None:
            if cell.can_eat(other) and cell.intersects_with(other):
                cell.grow(other.mass)
                self.regulate_cell_masses()
                if virus:
                    self.explode_cell(cell)
                
                self.mass_eaten_this_frame += other.mass
                return True
            return False
        
        for cell in self.cells:
            if cell.can_eat(other) and cell.intersects_with(other):
                cell.grow(other.mass)
                self.regulate_cell_masses()
                if virus:
                    self.explode_cell(cell)

                self.mass_eaten_this_frame += other.mass
                return True
        return False
    
    def explode_cell(self, cell):
        new_cells = cell.explode(max_new_cells=game_config.MAX_AMOUNT_CELLS - len(self.cells))
        self.cells.extend(new_cells)
        if new_cells:
            self.split_cooldown = game_config.SPLIT_COOLDOWN
    
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
                cell.update_radius_speed_merge(reset_merge=False)
            return True
        return False


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
        # print("Player.py line 202: MASS:", total_mass)
        center_x, center_y = center_x/total_mass, center_y/total_mass
        return {
            "name": self.name,
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

    def eject_food(self, px, py):
        ejected_cells = []
        for cell in self.cells:
            thrown_pellet = cell.eject_food(px, py)
            if thrown_pellet is not None:
                ejected_cells.append(thrown_pellet)
        return ejected_cells

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
        self.mass_eaten_this_frame = 0
        self.mass_lost_this_frame = 0
        self.mass_ejected_this_frame = 0

        px, py, do_split, do_feed = action

        if do_split:
            self.try_split(px, py)

        ejected_food = []
        if do_feed:
            for cell in self.cells:
                ejected = cell.eject_food(px, py)
                if ejected:
                    self.mass_ejected_this_frame += ejected.mass
                    ejected_food.append(ejected)

        self.split_cooldown = max(0, self.split_cooldown - 1/game_config.FPS)
        self.move(px, py)
        self.handle_self_collisions()
        return ejected_food
    
    def reward_after_update(self):
        return self.mass_eaten_this_frame - self.mass_lost_this_frame - self.mass_ejected_this_frame
    