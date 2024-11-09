import argparse
import pygame
from core.game import Game
# from environment import AgarEnvironment
from visualization.pygame_renderer import PygameRenderer
# from bots.random_bot import RandomBot
# from bots.rl_bot import RLBot
import config

def human_play(game_config):
    renderer = PygameRenderer(game_config)
    game = Game(["Human"], game_config)
    clock = pygame.time.Clock()

    running = True
    i = 0
    # counter = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        mouse_x, mouse_y = pygame.mouse.get_pos()
        action = renderer.screen_to_world((mouse_x, mouse_y))
        # print(mouse_x, mouse_y)
        game.update([action])
        game_state = game.get_state()
        renderer.render(game_state)
        # if i%5 == 0:
        #     print(mouse_x, mouse_y)
        #     print(action[0], action[1])

        #     print(game_config.WIDTH/2, game_config.HEIGHT/2)
        #     action_c = renderer.world_to_screen((game_config.WIDTH/2, game_config.HEIGHT/2))
        #     print(action_c[0], action_c[1])
        # print(game_state['players'][0]['x'], game_state['players'][0]['y'])
            
        # i += 1
        clock.tick(game_config.FPS)
        # print(game_state["players"][0]["total_mass"])
        
        # if counter > 2:
        #     if i%5 == 0:
        #         print("i =", i)
        #     i = i+1
        #     counter = 0
        # counter += 1
        

    renderer.close()

def bot_test(game_config, num_bots=3, visualize=True):
    # bots = [RandomBot() for _ in range(num_bots)]
    # env = AgarEnvironment(game_config, bots, visualize=visualize)
    
    # for _ in range(game_config.MAX_STEPS):
    #     actions = [bot.get_action(env.game.get_state()) for bot in bots]
    #     _, _, done, _ = env.step(actions)
    #     env.render()
        
    #     if done:
    #         break
    
    # env.close()
    pass

def train_rl(game_config, num_episodes=1000, visualize=False):
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
    # parser = argparse.ArgumentParser(description="Agar.io RL Environment")
    # parser.add_argument("--mode", choices=["human", "bot_test", "train"], default="human", help="Mode of operation")
    # parser.add_argument("--visualize", action="store_true", help="Enable visualization for bot_test and train modes")
    # args = parser.parse_args()

    game_config = config.GameConfig()

    # if args.mode == "human":
    #     human_play(game_config)
    # elif args.mode == "bot_test":
    #     bot_test(game_config, visualize=args.visualize)
    # elif args.mode == "train":
    #     train_rl(game_config, visualize=args.visualize)

    human_play(game_config)