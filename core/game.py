# core/game.py
from core.player import Player
from core.food import Pellet
from core.virus import Virus
import random

class Game:
    def __init__(self, player_names, config, mode):
        self.config = config
        self.frame_counter = 0
        if mode == "human_with_dummies":
            first_player = Player(3000, 3000, (250, 150, 0), player_names[0])

            # dummy bots
            self.players = [first_player] + [Player(
                random.randint(0, self.config.GAME_WIDTH), 
                random.randint(0, self.config.GAME_HEIGHT),
                (100 + random.randint(0, 155), 100 + random.randint(0, 155), 100 + random.randint(0, 155)),
                name, mass=random.randint(200, 500)) for name in player_names[1:]]
        else:
            raise Exception("mode not supported")
        
        self.food = self.generate_food(self.config.INITIAL_FOOD_COUNT)
        self.viruses = self.generate_viruses(self.config.INITIAL_VIRUS_COUNT)
        self.ejected_food = []

    def ejected_food_update(self):
        for ejected in self.ejected_food:
            ejected.update()

    def virus_update(self):
        """Checks for separation, separates, and then calls update for every virus"""
        new_viruses = []
        for virus in sorted(self.viruses, key=lambda c: c.mass, reverse=True):
            if len(self.viruses) + len(new_viruses) >= self.config.MAX_VIRUS_COUNT_SEPARATION:
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
        self.frame_counter = (self.frame_counter + 1) % self.config.FPS
        for player, action in zip(self.players, actions):
            ejected_food_player = player.update(action)  # Handles self collisions
            self.ejected_food.extend(ejected_food_player)
        
        self.ejected_food_update()
        self.virus_update()
        self.handle_collisions()  # Collisions with food and player to player
        if self.frame_counter == 0:
            self.spawn_food()
            self.spawn_viruses()

    def get_state(self):
        return {
            'players': [p.get_state() for p in self.players],
            'food': [f.get_state() for f in self.food],
            'viruses': [v.get_state() for v in self.viruses],
            'ejected_food': [e.get_state() for e in self.ejected_food]
        }
    
    def generate_food(self, amount):
        return [Pellet(random.randint(0, self.config.GAME_WIDTH),
                    random.randint(0, self.config.GAME_HEIGHT),
                    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), self.config.PELLET_MASS)
            for _ in range(amount)]
    
    def spawn_food(self):
        if len(self.food) < self.config.MAX_FOOD_COUNT:
            new_food_count = min(self.config.FOOD_SPAWN_RATE, self.config.MAX_FOOD_COUNT - len(self.food))
            self.food.extend(self.generate_food(new_food_count))

    def generate_viruses(self, amount):
        return [Virus(random.randint(0, self.config.GAME_WIDTH),
                    random.randint(0, self.config.GAME_HEIGHT)) for _ in range(amount)]
    
    def spawn_viruses(self):
        if len(self.viruses) < self.config.MAX_VIRUS_COUNT_GENERATED:
            new_viruses_count = min(self.config.VIRUS_SPAWN_RATE, self.config.MAX_VIRUS_COUNT_GENERATED - len(self.viruses))
            self.viruses.extend(self.generate_viruses(new_viruses_count))

    def handle_collisions(self):
        for virus in self.viruses:
            self.ejected_food = [e for e in self.ejected_food if not virus.eat(e)]

        for i, player in enumerate(self.players):
            # Check for food collisions
            self.food = [f for f in self.food if not player.eat(f)]

            # Ejected food can be eaten by players
            self.ejected_food = [e for e in self.ejected_food if not player.eat(e)]
        
            # Check for virus collisions
            self.viruses = [v for v in self.viruses if not player.eat(v, virus=True)]

            # Check for player collisions
            for j, other_player in enumerate(self.players):
                if i != j:
                    for other_cell in other_player.cells:
                        if player.eat(other_cell):
                            other_player.cells.remove(other_cell)
                            if len(other_player.cells) == 0:
                                other_player.reset()
    