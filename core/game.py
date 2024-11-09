# core/game.py
from core.player import Player
from core.food import Pellet
import random

class Game:
    def __init__(self, player_names, config):

        self.players = [Player(100, 100, (100, 150, 50), player_names[0])]  # todo: multiple players
        self.config = config
        self.food = self.generate_food(self.config.INITIAL_FOOD_COUNT)

    def update(self, actions):
        for player, action in zip(self.players, actions):
            player.move(*action)
        self.handle_collisions()
        self.spawn_food()

    def get_state(self):
        return {
            'players': [p.get_state() for p in self.players],
            'food': [f.get_state() for f in self.food]
        }
    
    def generate_food(self, amount):
        return [Pellet(random.randint(0, self.config.GAME_WIDTH),
                    random.randint(0, self.config.GAME_HEIGHT),
                    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), self.config.PELLET_MASS, self.config.PELLET_RADIUS)
            for _ in range(amount)]
    def spawn_food(self):
        if len(self.food) < self.config.MAX_FOOD_COUNT:
            new_food_count = min(self.config.FOOD_SPAWN_RATE, self.config.MAX_FOOD_COUNT - len(self.food))
            self.food.extend(self.generate_food(new_food_count))

    def handle_collisions(self):
        for player in self.players:
            # Check for food collisions
            self.food = [f for f in self.food if not player.eat(f)]
            
            # Check for player collisions (if implementing player-player interactions)
            # for other_player in self.players:
            #     if other_player != player:
            #         for other_cell in other_player.cells:
            #             if player.can_eat(other_cell):
            #                 player.eat(other_cell)
            #                 other_player.cells.remove(other_cell)
    