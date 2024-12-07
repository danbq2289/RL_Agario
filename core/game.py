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

class Game:
    def __init__(self, player_names, non_dummy_players):
        self.frame_counter = 0

        assert non_dummy_players <= len(player_names)

        # What is the initial mass and radius of non-dummy players? 100, 100
        # What is a reasonable minimum distance? 1000 (from 6000x6000)

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

    def get_RL_state(self, player_index):
        obs = []
        player = self.players[player_index]


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
        for virus in self.viruses:
            self.ejected_food = [e for e in self.ejected_food if not virus.eat(e)]

        reset_players = set()
        for i, player in enumerate(self.players):
            if player.name in reset_players:
                continue
            # Check for food collisions
            self.food = [f for f in self.food if not player.eat(f)]

            # Ejected food can be eaten by players
            self.ejected_food = [e for e in self.ejected_food if not player.eat(e)]
        
            # Check for virus collisions
            self.viruses = [v for v in self.viruses if not player.eat(v, virus=True)]

            # Check for player collisions
            for j, other_player in enumerate(self.players):
                if i != j and other_player.name not in reset_players:
                    for other_cell in other_player.cells[:]:  # Iterate over a copy to avoid issues with modification
                        if player.eat(other_cell):
                            other_player.cells.remove(other_cell)
                            if len(other_player.cells) == 0:
                                # Don't check that player anymore and schedule for resetting
                                reset_players.add(other_player.name)

        for player in self.players:
            if len(player.cells) == 0:
                if player.name not in reset_players:
                    raise Exception("Something went wrong with the resetting")
                player.reset()
            elif player.name in reset_players:
                raise Exception("Something went wrong with the resetting")
        return reset_players
    