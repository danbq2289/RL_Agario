import argparse
import time
import pygame
from core.game import Game
# from environment import AgarEnvironment
from visualization.pygame_renderer import PygameRenderer
from bots.basic_bots import DummyBot
# from bots.rl_bot import RLBot
import config
game_config = config.GameConfig()

def human_play_with_dummies(n_dummies):
    if n_dummies > game_config.MAX_PLAYERS:
        raise Exception("might lag. bypass if you want (config.py), but you have been warned")
    renderer = PygameRenderer(game_config)
    dummy_names = [f"dum{i}" for i in range(1, n_dummies+1)]
    
    game = Game(["Human"] + dummy_names, non_dummy_players=1)
    game_state = game.get_state() # initial game state

    dummy_bots = [DummyBot(name) for name in dummy_names]

    clock = pygame.time.Clock()

    running = True
    split_key_pressed = False
    feed_key_pressed = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # for splitting
            elif event.type == pygame.KEYDOWN:  
                split_key_pressed = event.key == pygame.K_SPACE
                feed_key_pressed = event.key == pygame.K_w
                    
        mouse_x, mouse_y = pygame.mouse.get_pos()
        action_x, action_y = renderer.screen_to_world((mouse_x, mouse_y))

        # for splitting
        if split_key_pressed:
            do_split = True
            split_key_pressed = False  # Reset the flag
        else:
            do_split = False

        # for feeding
        if feed_key_pressed:
            do_feed = True
            feed_key_pressed = False  # Reset the flag
        else:
            do_feed = False

        
        game.update([(action_x, action_y, do_split, do_feed)] + [dummy_bot.get_action(game) for dummy_bot in dummy_bots])
        game_state = game.get_state()
        renderer.render(game_state)
        clock.tick(game_config.FPS)
    renderer.close()

def basic_bot_test(n_dummies, visualize):
    # For benchmarking the bots.
    dummy_names = [f"dum{i}" for i in range(n_dummies)]
    dummy_bots = [DummyBot(name) for name in dummy_names]
    
    time_intervals = []
    for i in range(100):
        game = Game(dummy_names, non_dummy_players=0)
        max_steps = 1000

        if visualize:
            renderer = PygameRenderer(game_config)
            clock = pygame.time.Clock()
            running = True
            st = time.time()
            while running and max_steps > 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                game.update([dummy_bot.get_action(game) for dummy_bot in dummy_bots])
                game_state = game.get_state()
                renderer.render(game_state)
                clock.tick(game_config.FPS)
                max_steps -= 1
            renderer.close()
            end = time.time()
            print(f"Ran in {end - st} seconds")

        else:
            st = time.time()
            while max_steps > 0:
                game.update([dummy_bot.get_action(game) for dummy_bot in dummy_bots])
                max_steps -= 1
            end = time.time()
            print(f"Ran in {end - st} seconds")

        time_intervals.append(end - st)

    print(time_intervals)


def train_rl(num_episodes=1000, visualize=False):
    # rl_bot = RLBot()
    # env = AgarEnvironment(game_config, [rl_bot], visualize=visualize)

    # for episode in range(num_episodes):
    #     state = env.reset()
    #     done = False
    #     total_reward = 0

    #     while not done:
    #         action = rl_bot.get_action(state)
    #         next_state, reward, done, _ = env.step(action)
    #         rl_bot.learn(state, action, reward, next_state, done)
    #         state = next_state
    #         total_reward += reward

    #         if visualize:
    #             env.render()

    #     print(f"Episode {episode + 1}/{num_episodes}, Total Reward: {total_reward}")

    # env.close()
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agar.io RL Environment")
    parser.add_argument("--mode", choices=["human_with_dummies", "basic_bot_test", "train"], default="human_with_dummies", help="Mode of operation")
    parser.add_argument("--num_dummies")
    parser.add_argument("--visualize", action="store_true", help="Enable visualization for bot_test and train modes")
    args = parser.parse_args()

    if args.mode == "human_with_dummies":
        human_play_with_dummies(int(args.num_dummies))
    elif args.mode == "basic_bot_test":
        basic_bot_test(int(args.num_dummies), visualize=args.visualize)
    # elif args.mode == "train":
    #     train_rl(visualize=args.visualize)