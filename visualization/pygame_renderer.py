import pygame
import math

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.position = [0, 0]
        self.filtered_scale = 1

    def update(self, player):
        total_size = player["total_size"]
        scale = math.pow(min(64 / total_size, 1), 0.4)
        self.filtered_scale = (9 * self.filtered_scale + scale) / 10

        self.position[0] = player['x'] - self.width / (2* self.filtered_scale)
        self.position[1] = player['y'] - self.height / (2* self.filtered_scale)

class PygameRenderer:
    def __init__(self, game_config):
        pygame.init()
        self.width = game_config.WIDTH
        self.height = game_config.HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))

        self.game_width = game_config.GAME_WIDTH
        self.game_height = game_config.GAME_HEIGHT
        self.grid_spacing = game_config.GRID_SPACING
        
        pygame.display.set_caption("Agar.io")
        self.camera = Camera(self.width, self.height)
        self.font = pygame.font.Font(None, 24)

    def draw_grid(self, grid_spacing):
        start_x = max(0, int(self.camera.position[0] // grid_spacing) * grid_spacing)
        start_y = max(0, int(self.camera.position[1] // grid_spacing) * grid_spacing)
        end_x = min(self.game_width, int(start_x + self.width / self.camera.filtered_scale) + grid_spacing)
        end_y = min(self.game_height, int(start_y + self.height / self.camera.filtered_scale) + grid_spacing)

        for x in range(start_x, end_x, grid_spacing):
            start = self.world_to_screen((x, start_y))
            end = self.world_to_screen((x, end_y))
            pygame.draw.line(self.screen, (200, 200, 200), start, end)

        for y in range(start_y, end_y, grid_spacing):
            start = self.world_to_screen((start_x, y))
            end = self.world_to_screen((end_x, y))
            pygame.draw.line(self.screen, (200, 200, 200), start, end)

    def draw_game_border(self):
        top_left = self.world_to_screen((0, 0))
        top_right = self.world_to_screen((self.game_width, 0))
        bottom_left = self.world_to_screen((0, self.game_height))
        bottom_right = self.world_to_screen((self.game_width, self.game_height))

        pygame.draw.line(self.screen, (0, 0, 0), top_left, top_right, 2)
        pygame.draw.line(self.screen, (0, 0, 0), top_right, bottom_right, 2)
        pygame.draw.line(self.screen, (0, 0, 0), bottom_right, bottom_left, 2)
        pygame.draw.line(self.screen, (0, 0, 0), bottom_left, top_left, 2)

    def world_to_screen(self, pos):
        x = (pos[0] - self.camera.position[0]) * self.camera.filtered_scale
        y = (pos[1] - self.camera.position[1]) * self.camera.filtered_scale
        return (int(x), int(y))
    
    def screen_to_world(self, xy):
        pos_0 = xy[0]/self.camera.filtered_scale + self.camera.position[0]
        pos_1 = xy[1]/self.camera.filtered_scale + self.camera.position[1]
        return (pos_0, pos_1)
    
    def draw_cell(self, cell_state):
        pos = self.world_to_screen((cell_state['x'], cell_state['y']))
        radius = int(cell_state['radius'] * self.camera.filtered_scale)
        pygame.draw.circle(self.screen, cell_state['color'], pos, radius)
        
        name_surface = self.font.render(cell_state['name'], True, (0, 0, 0))
        name_rect = name_surface.get_rect(center=pos)
        self.screen.blit(name_surface, name_rect)



    def draw_player(self, player_state):
        for cell_state in player_state["cells"]:
            self.draw_cell(cell_state)

    def draw_food(self, food):
        for f in food:
            pos = self.world_to_screen((f['x'], f['y']))
            radius = int(f['radius'] * self.camera.filtered_scale)
            pygame.draw.circle(self.screen, f['color'], pos, max(1, radius))

    def render(self, game_state):
        self.screen.fill((255, 255, 255))  # White background

        players = game_state['players']
        food = game_state['food']

        # Update camera based on the first player
        if players:
            self.camera.update(players[0])

        self.draw_grid(self.grid_spacing)
        self.draw_game_border()
        self.draw_food(food)

        for player in players:
            self.draw_player(player)

        pygame.display.flip()

    def close(self):
        pygame.quit()