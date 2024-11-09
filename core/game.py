# core/game.py
from core.player import Player
from core.food import Pellet
import random

class Game:
    def __init__(self, player_names, config, mode):
        self.config = config
        if mode == "human_with_dummies":
            first_player = Player(100, 100, (250, 150, 0), player_names[0])

            # dummy bots
            self.players = [first_player] + [Player(
                random.randint(0, self.config.GAME_WIDTH),
                random.randint(0, self.config.GAME_HEIGHT),
                (100 + random.randint(0, 155), 100 + random.randint(0, 155), 100 + random.randint(0, 155)),
                name, mass=random.randint(200, 500)) for name in player_names[1:]]
            
            self.food = self.generate_food(self.config.INITIAL_FOOD_COUNT)
        else:
            raise Exception("mode not supported")

    def update(self, actions):
        for player, action in zip(self.players, actions):
            player.update(action)  # Handles self collisions
        self.handle_collisions()  # Collisions with food and player to player
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
        for i, player in enumerate(self.players):
            # Check for food collisions
            self.food = [f for f in self.food if not player.eat(f)]
            
            # Check for player collisions
            for j, other_player in enumerate(self.players):
                if i != j:
                    for other_cell in other_player.cells:
                        if player.eat(other_cell):
                            other_player.cells.remove(other_cell)
                            if len(other_player.cells) == 0:
                                other_player.reset()
    