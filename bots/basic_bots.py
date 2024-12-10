import random
import math
import config

game_config = config.GameConfig()

"""
At level 1:
This dummy bot goes in roughly straight lines, regardless of what's ahead. 
Changes directions periodically.

At level 2:
In addition, if player with big mass is nearby, it runs away, and splits to escape if needed.

At level 3:
In addition, if player with small mass is nearby, chases it and splits to capture if it's possible.
"""
class DummyBot:
    def __init__(self, name, lvl=3):
        self.name = name
        self.counter = 0
        self.target = (0, 0)
        self.lvl = lvl

    def get_action(self, game):
        # Extract the bot's position from the game state
        bot_player = next((player for player in game.players if player.name == self.name), None)
        if not bot_player:
            raise Exception("bot name not found in game")
        
        if self.lvl >= 2:
            # If player with big mass is nearby, run away / split
            for cell in sorted(bot_player.cells, key=lambda c: c.mass, reverse=True):
                for player in game.players:
                    if player.name == self.name:  # can just check if index is different
                        continue
                    for other_cell in player.cells:
                        distance_sq = (cell.x - other_cell.x)**2 + (cell.y - other_cell.y)**2
                        if distance_sq < 500000:
                            if self.lvl >= 3:
                                # Check if smaller cell first. (lvl3 should be aggressive)
                                critical_mass_other = game_config.MASS_FACTOR_EAT_ANOTHER*other_cell.mass
                                if cell.mass > critical_mass_other:
                                    # Chase
                                    self.target = (other_cell.x, other_cell.y)
                                    potential_kill = 6*critical_mass_other > cell.mass > 2*critical_mass_other and distance_sq < 360000
                                    return (*self.target, potential_kill, False)
                            
                            critical_mass = game_config.MASS_FACTOR_EAT_ANOTHER*cell.mass
                            if other_cell.mass > critical_mass:
                                # Run away
                                self.target = (2*cell.x - other_cell.x, 2*cell.y - other_cell.y)
                                potential_death = 6*critical_mass > other_cell.mass > 2*critical_mass and distance_sq < 360000
                                return (*self.target, potential_death, False)

        max_cell = max(bot_player.cells, key=lambda c: c.radius)
        bot_x, bot_y = max_cell.x, max_cell.y

        if self.lvl == 0:
            return (bot_x, bot_y, False, False)

        if self.counter <= 0:
            # Choose new point target
            self.target = (random.randint(0, game_config.GAME_WIDTH), random.randint(0, game_config.GAME_HEIGHT))
            self.counter = 420  # changes goal every 7 seconds
        self.counter -= 1

        # Generate a random target point within a certain radius
        dx = self.target[0] - bot_x
        dy = self.target[1] - bot_y

        angle = math.atan2(dy, dx) + random.uniform(-math.pi, math.pi)/18

        target_x = bot_x + 1000 * math.cos(angle)
        target_y = bot_y + 1000 * math.sin(angle)

        split = False # random.random() < 0.0005
        feed = False # random.random() < 0.001

        return (target_x, target_y, split, feed)