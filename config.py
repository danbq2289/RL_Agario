class GameConfig:
    def __init__(self):
        # Game window dimensions
        self.WIDTH = 1440
        self.HEIGHT = 900

        # Game graphics
        self.FPS = 60
        self.BACKGROUND_COLOR = (240, 240, 240)
        self.GRID_COLOR = (230, 230, 230)
        self.GRID_SPACING = 50

        self.GAME_WIDTH = 6000
        self.GAME_HEIGHT = 6000

        self.GRID_SPACING = 50
        self.RADIUS_FROM_MASS = lambda mass: 10 * mass ** 0.5
        self.SPEED_FROM_RADIUS = lambda radius: 30 * radius ** -0.439

        # Game rules
        self.MAX_PLAYERS = 30
        self.INITIAL_SEPARATION_MIN = 1000  # assuming 20 players or less

        self.INITIAL_PLAYER_MASS = 100

        self.PELLET_MASS = 1
        self.INITIAL_FOOD_COUNT = int(self.GAME_HEIGHT * self.GAME_WIDTH/18000)
        self.MAX_FOOD_COUNT = self.INITIAL_FOOD_COUNT
        self.FOOD_SPAWN_RATE = 5  # New food particles per frame

        self.VIRUS_INITIAL_MASS = 110
        self.INITIAL_VIRUS_COUNT = int(self.INITIAL_FOOD_COUNT/200)
        self.MAX_VIRUS_COUNT_GENERATED = self.INITIAL_VIRUS_COUNT
        self.MAX_VIRUS_COUNT_SEPARATION = 2*self.INITIAL_VIRUS_COUNT
        self.VIRUS_SPAWN_RATE = 1

        self.EJECTED_MASS = 16
        self.EJECTION_SPEED = 30

        self.VIRUS_AMOUNT_FEED_TO_SEPARATE = 7
        self.VIRUS_SEPARATION_MASS = self.VIRUS_INITIAL_MASS + self.VIRUS_AMOUNT_FEED_TO_SEPARATE * self.EJECTED_MASS
        self.VIRUS_MAX_MASS = self.VIRUS_SEPARATION_MASS * 1.05

        self.MIN_PLAYER_MASS = 9
        self.MAX_PLAYER_MASS = 20000
        self.MASS_LOSS_RATE = 0.002

        self.MAX_AMOUNT_CELLS = 16

        # Game mechanics
        self.SPLIT_MASS_THRESHOLD = 35
        self.SPLIT_SPEED = 30
        self.VIRUS_SPLIT_SPEED = 40
        self.EXPLODE_SPEED = 50
        self.SPLIT_COOLDOWN = 0.2  # Seconds
        self.MERGE_TIME_FROM_MASS = lambda mass: 30 + (7/300)*mass  # Seconds before split cells can merge

        self.MASS_FACTOR_EAT_ANOTHER = 1.2
        self.CLOSENESS_FACTOR = 0.25

        # Optimization
        self.SPATIAL_GRID_CELL = 70
        self.CELL_RANGE_FROM_RADIUS = lambda r: int(r // self.SPATIAL_GRID_CELL) + 1
        self.VIRUS_CELL_RANGE = self.CELL_RANGE_FROM_RADIUS(self.RADIUS_FROM_MASS(self.VIRUS_MAX_MASS))

        # RL training
        self.TOTAL_DIRECTIONS = 16
        self.DISCRETE_FACTOR_DISTANCE = 2.5

        self.ACTION_SPACE = 2 * self.TOTAL_DIRECTIONS + 1
        self.OBSERVATION_SIZE = (16 + 30 + 100 + 10) * 3

        self.MAX_STEPS = 10000  # Maximum steps per episode
        self.REWARD_FOOD = 1
        self.REWARD_PLAYER = 10
        self.REWARD_DEATH = -50


    def get_action_space(self):
        return self.ACTION_SPACE

    def get_reward_range(self):
        min_reward = self.REWARD_DEATH
        max_reward = max(self.REWARD_FOOD, self.REWARD_PLAYER) * self.MAX_FOOD_COUNT
        return (min_reward, max_reward)