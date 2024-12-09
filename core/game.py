# core/game.py
from core.player import Player
from core.food import Pellet
from core.virus import Virus
import math
import random
import config
game_config = config.GameConfig()

def generate_points(rect_width, rect_height, min_distance, num_points):
    points = []
    attempts = 0
    max_attempts = num_points * 10  # Limit total attempts to avoid infinite loop

    while len(points) < num_points and attempts < max_attempts:
        x = random.uniform(0, rect_width)
        y = random.uniform(0, rect_height)
        new_point = (x, y)

        if all(math.dist(new_point, p) >= min_distance for p in points):
            points.append(new_point)
        
        attempts += 1

    while len(points) < num_points:
        x = random.uniform(0, rect_width)
        y = random.uniform(0, rect_height)
        points.append((x, y))

    return points

class SpatialGrid:
    # For optimization.
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.grid = {}

    def add_object(self, obj):
        cell_x = int(obj.x // self.cell_size)
        cell_y = int(obj.y // self.cell_size)
        key = (cell_x, cell_y)
        if key not in self.grid:
            self.grid[key] = []
        self.grid[key].append(obj)

    def get_nearby_objects(self, obj, range_cells=1):
        cell_x = int(obj.x // self.cell_size)
        cell_y = int(obj.y // self.cell_size)
        nearby = []
        for dx in range(-range_cells, range_cells + 1):
            for dy in range(-range_cells, range_cells + 1):
                key = (cell_x + dx, cell_y + dy)
                if key in self.grid:
                    nearby.extend(self.grid[key])
        return nearby
    
class Game:
    def __init__(self, player_names, non_dummy_players):
        self.frame_counter = 0

        assert 0 <= non_dummy_players <= len(player_names)

        points = generate_points(game_config.GAME_WIDTH, game_config.GAME_HEIGHT, 
                                 game_config.INITIAL_SEPARATION_MIN, len(player_names))
        
        # Non dummy players 
        non_dummy_players_list = [Player(point[0], point[1],
            (100 + random.randint(0, 155), 100 + random.randint(0, 155), 100 + random.randint(0, 155)),
            name) for name, point in zip(player_names[:non_dummy_players], points[:non_dummy_players])]

        # dummy bots
        self.players = non_dummy_players_list + [Player(point[0], point[1],
            (100 + random.randint(0, 155), 100 + random.randint(0, 155), 100 + random.randint(0, 155)),
            name, mass=random.randint(50, 200)) for name, point in zip(player_names[non_dummy_players:], points[non_dummy_players:])]

        
        self.food = self.generate_food(game_config.INITIAL_FOOD_COUNT)
        self.viruses = self.generate_viruses(game_config.INITIAL_VIRUS_COUNT)
        self.ejected_food = []

    def update_spatial_grid(self):
        self.spatial_grid = SpatialGrid(game_config.SPATIAL_GRID_CELL)
        for player in self.players:
            for cell in player.cells:
                self.spatial_grid.add_object(cell)
        for food in self.food:
            self.spatial_grid.add_object(food)
        for virus in self.viruses:
            self.spatial_grid.add_object(virus)
        for ejected in self.ejected_food:
            self.spatial_grid.add_object(ejected)

    def ejected_food_update(self):
        for ejected in self.ejected_food:
            ejected.update()

    def virus_update(self):
        """Checks for separation, separates, and then calls update for every virus"""
        new_viruses = []
        for virus in sorted(self.viruses, key=lambda c: c.mass, reverse=True):
            if len(self.viruses) + len(new_viruses) >= game_config.MAX_VIRUS_COUNT_SEPARATION:
                break
            new_virus = virus.separate()
            if new_virus:
                new_viruses.append(new_virus)
                # print("game.py 40, new virus coords", new_virus.x, new_virus.y, self.players[0].cells[0].x, self.players[0].cells[0].y)
                # print("game.py 40, new virus coords", new_virus.x, new_virus.y, new_virus.vx, new_virus.vy)

        self.viruses.extend(new_viruses)

        # move the viruses
        for virus in self.viruses:
            virus.update()

    def update(self, actions):
        self.frame_counter = (self.frame_counter + 1) % game_config.FPS
        for player, action in zip(self.players, actions):
            ejected_food_player = player.update(action)  # Handles self collisions
            self.ejected_food.extend(ejected_food_player)
        
        self.ejected_food_update()
        self.virus_update()
        reset_player_names = self.handle_collisions()  # Collisions with food and player to player
        if self.frame_counter == 0:
            self.spawn_food()
            self.spawn_viruses()

        return reset_player_names

    def get_RL_state(self, player_index):
        obs = []
        player = self.players[player_index]
        total_size = sum([cell.radius for cell in player.cells])
        
        # Calculate visible area
        view_width = game_config.WIDTH / math.pow(min(64 / total_size, 1), 0.4)
        view_height = game_config.HEIGHT / math.pow(min(64 / total_size, 1), 0.4)
        view_left = player.cells[0].x - view_width / 2
        view_top = player.cells[0].y - view_height / 2
        
        # Player's own cells (max 16)
        for i in range(16):
            if i < len(player.cells):
                cell = player.cells[i]
                norm_x = (cell.x - view_left) / view_width
                norm_y = (cell.y - view_top) / view_height
                obs.extend([norm_x, norm_y,
                            cell.mass / game_config.MAX_PLAYER_MASS])
            else:
                obs.extend([norm_x, norm_y, 0])  # Padding
        
        # Other visible cells (max 30)
        visible_cells = []
        for i, p in enumerate(self.players):
            if i != player_index:
                for cell in p.cells:
                    if (view_left <= cell.x <= view_left + view_width and
                        view_top <= cell.y <= view_top + view_height):
                        visible_cells.append((cell.x, cell.y, cell.mass))
        
        visible_cells.sort(key=lambda c: c[2], reverse=True)  # Sort by mass
        for i in range(30):
            if i < len(visible_cells):
                x, y, mass = visible_cells[i]
                norm_x, norm_y = (x - view_left) / view_width, (y - view_top) / view_height
                obs.extend([norm_x, norm_y, mass / game_config.MAX_PLAYER_MASS])
            else:
                obs.extend([norm_x, norm_y, 0])  # Padding
        
        # Food (max 100)
        visible_food = [f for f in self.food + self.ejected_food if (view_left <= f.x <= view_left + view_width and
                                                view_top <= f.y <= view_top + view_height)]
        for i in range(100):
            if i < len(visible_food):
                norm_x, norm_y = (visible_food[i].x - view_left) / view_width, (visible_food[i].y - view_top) / view_height
                obs.extend([norm_x, norm_y, visible_food[i].mass])
            else:
                obs.extend([norm_x, norm_y, 0])  # Padding
        
        # Viruses (max 10)
        visible_viruses = [v for v in self.viruses if (view_left <= v.x <= view_left + view_width and
                                                    view_top <= v.y <= view_top + view_height)]
        for i in range(10):
            if i < len(visible_viruses):
                norm_x, norm_y = (visible_viruses[i].x - view_left) / view_width, (visible_viruses[i].y - view_top) / view_height
                obs.extend([norm_x, norm_y, visible_viruses[i].mass])
            else:
                obs.extend([norm_x, norm_y, 0])  # Padding
        
        return obs


    def get_state(self):
        return {
            'players': [p.get_state() for p in self.players],
            'food': [f.get_state() for f in self.food],
            'viruses': [v.get_state() for v in self.viruses],
            'ejected_food': [e.get_state() for e in self.ejected_food]
        }
    
    def generate_food(self, amount):
        return [Pellet(random.randint(0, game_config.GAME_WIDTH),
                    random.randint(0, game_config.GAME_HEIGHT),
                    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), game_config.PELLET_MASS)
            for _ in range(amount)]
    
    def spawn_food(self):
        if len(self.food) < game_config.MAX_FOOD_COUNT:
            new_food_count = min(game_config.FOOD_SPAWN_RATE, game_config.MAX_FOOD_COUNT - len(self.food))
            self.food.extend(self.generate_food(new_food_count))

    def generate_viruses(self, amount):
        return [Virus(random.randint(0, game_config.GAME_WIDTH),
                    random.randint(0, game_config.GAME_HEIGHT)) for _ in range(amount)]
    
    def spawn_viruses(self):
        if len(self.viruses) < game_config.MAX_VIRUS_COUNT_GENERATED:
            new_viruses_count = min(game_config.VIRUS_SPAWN_RATE, game_config.MAX_VIRUS_COUNT_GENERATED - len(self.viruses))
            self.viruses.extend(self.generate_viruses(new_viruses_count))

    def handle_collisions(self):
        self.update_spatial_grid()
        reset_players = set()

        for virus in self.viruses:
            nearby_objects = self.spatial_grid.get_nearby_objects(virus, range_cells=game_config.VIRUS_CELL_RANGE)
            self.ejected_food = [e for e in self.ejected_food if not (e in nearby_objects and virus.eat(e))]
        
        for i, player in enumerate(self.players):
            if player.name in reset_players:
                continue

            for cell in player.cells:
                range_cells = max(1, int(cell.radius // game_config.SPATIAL_GRID_CELL) + 1)
                nearby_objects = self.spatial_grid.get_nearby_objects(cell, range_cells=range_cells)


                # Check for food collisions
                self.food = [f for f in self.food if not (f in nearby_objects and player.eat(f, cell=cell))]

                # Ejected food can be eaten by players
                self.ejected_food = [e for e in self.ejected_food if not (e in nearby_objects and player.eat(e, cell=cell))]
            
                # Check for virus collisions
                self.viruses = [v for v in self.viruses if not (v in nearby_objects and player.eat(v, virus=True, cell=cell))]

                # Check for player collisions
                for j, other_player in enumerate(self.players):
                    if i != j and other_player.name not in reset_players:
                        for other_cell in other_player.cells[:]:  # Iterate over a copy to avoid issues with modification
                            if other_cell in nearby_objects and player.eat(other_cell, cell=cell):

                                other_player.mass_lost_this_frame += other_cell.mass
                                other_player.cells.remove(other_cell)
                                if len(other_player.cells) == 0:
                                    # Don't check that player anymore and schedule for resetting
                                    reset_players.add(other_player.name)

        for player in self.players:
            if len(player.cells) == 0:
                player.reset()
        return reset_players
    