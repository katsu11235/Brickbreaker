import pygame
import sys
import pygame_menu
from pygame.locals import *

# Colors
white = (255, 255, 255)
purple = (91, 44, 111)
turquoise = (3, 155, 229)
red = (255, 0, 0)
yellow = (255, 255, 0)
shadow_color = (50, 50, 50)

# States
state_ballinpaddle = 0
state_inplay = 1
state_won = 2
state_gameover = 3

# Frame rate and ball speed levels
fps_levels = [60, 120, 144, 165, 180, 240]
ball_speed_levels = [240, 480, 720, 960, 1280, 1440, 1920]

class BrickBreaker:

    def __init__(self):
        pygame.init()
        self.screen_size = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("BrickBreaker")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont('Lucida Sans Roman', 20)
        self.init_game()
        
    def init_game(self):
        self.lives = 3
        self.score = 0
        self.state = state_ballinpaddle

        self.paddle_width = self.screen_size[0] // 7
        self.paddle_height = self.screen_size[1] // 24
        self.ball_diameter = self.screen_size[1] // 20
        self.ball_radius = self.ball_diameter // 2

        self.max_paddlex = self.screen_size[0] - self.paddle_width
        self.max_ballx = self.screen_size[0] - self.ball_diameter
        self.max_bally = self.screen_size[1] - self.ball_diameter

        self.paddley = self.screen_size[1] - self.paddle_height - 10

        self.paddle = pygame.Rect(self.screen_size[0] // 2 - self.paddle_width // 2, self.paddley, self.paddle_width, self.paddle_height)
        self.ball = pygame.Rect(self.screen_size[0] // 2 - self.ball_radius, self.paddley - self.ball_diameter, self.ball_diameter, self.ball_diameter)
        self.fps = 60
        self.speed = 240
        self.update_ball_velocity()
        self.update_paddle_speed()
        self.menu_enabled = True
        self.mudeki = False

        self.menu = pygame_menu.Menu('Settings', 400, 300, theme=pygame_menu.themes.THEME_DARK)
        self.menu.add.selector('FPS: ', [(str(fps), fps) for fps in fps_levels], onchange=self.set_fps)
        self.menu.add.selector('Ball Speed: ', [(str(speed), speed) for speed in ball_speed_levels], onchange=self.set_ball_speed)
        self.menu.add.button('Play', self.start_game)

        self.create_bricks()
    
    def reset_menu(self):
        self.menu_enabled = True

    def create_bricks(self):
        y_brick = 30
        self.bricks = []

        brick_width = self.screen_size[0] // 10
        brick_height = self.screen_size[1] // 24

        for i in range(7):
            x_brick = 30
            for j in range(9):
                self.bricks.append(pygame.Rect(x_brick, y_brick, brick_width, brick_height))
                x_brick += brick_width + 8
            y_brick += brick_height + 6

    def draw_bricks(self):
        for brick in self.bricks:
            self.add_shadow(brick,shadow_color,1)
            pygame.draw.rect(self.screen, red, brick)

    def check_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.paddle.left -= self.paddle_speed  # Use the updated paddle speed
            if self.paddle.left < 0:
                self.paddle.left = 0

        if keys[pygame.K_RIGHT]:
            self.paddle.left += self.paddle_speed  # Use the updated paddle speed
            if self.paddle.left > self.max_paddlex:
                self.paddle.left = self.max_paddlex

        if keys[pygame.K_SPACE] and self.state == state_ballinpaddle:
            self.state = state_inplay

        if keys[pygame.K_q] and (self.state == state_gameover or self.state == state_won):
            pygame.display.quit()
            pygame.quit()
            sys.exit()

        if keys[pygame.K_RETURN] and (self.state == state_gameover or self.state == state_won):
            self.init_game()
            self.state = state_ballinpaddle

        if keys[pygame.K_k]:
            self.init_game()

        if keys[pygame.K_o]:
            self.mudeki = not self.mudeki

    def move_ball(self):
        self.ball.left += self.ballvel[0]
        self.ball.top += self.ballvel[1]

        if self.ball.left <= 0:
            self.ball.left = 0
            self.ballvel[0] = -self.ballvel[0]

        elif self.ball.left >= self.max_ballx:
            self.ball.left = self.max_ballx
            self.ballvel[0] = -self.ballvel[0]

        if self.ball.top < 0:
            self.ballvel[1] = -self.ballvel[1]
            self.ball.top = 0

    def add_shadow(self, rect, color,shadow_offset=5):
        shadow_rect = rect.move(shadow_offset, shadow_offset)
        pygame.draw.rect(self.screen, color, shadow_rect)

    def draw_with_shadow(self):
        # Draw paddle shadow
        self.add_shadow(self.paddle, shadow_color)
        pygame.draw.rect(self.screen, purple, self.paddle)

        # Draw ball shadow
        ball_shadow = pygame.Rect(self.ball.left + 5, self.ball.top + 5, self.ball_diameter, self.ball_diameter)
        pygame.draw.circle(self.screen, shadow_color, (ball_shadow.left + self.ball_radius, ball_shadow.top + self.ball_radius), self.ball_radius)
        pygame.draw.circle(self.screen, yellow, (self.ball.left + self.ball_radius, self.ball.top + self.ball_radius), self.ball_radius)

    def handle_coll(self):
        for brick in self.bricks:
            if self.ball.colliderect(brick):
                self.score += 1
                self.ballvel[1] = -self.ballvel[1]
                self.bricks.remove(brick)
                break

        if len(self.bricks) == 0:
            self.state = state_won

        if self.ball.colliderect(self.paddle):
            self.ball.top = self.paddley - self.ball_diameter
            self.ballvel[1] = -self.ballvel[1]

        elif self.ball.top > self.paddle.top:
            if self.mudeki:
                self.ball.top = self.paddley - self.ball_diameter
                self.ballvel[1] = -self.ballvel[1]
            else:
                self.lives -= 1
                if self.lives > 0:
                    self.state = state_ballinpaddle
                else:
                    self.state = state_gameover

    def show_stats(self):
        font_surface = self.font.render(f"SCORE: {self.score}  LIVES: {self.lives}  FPS: {self.fps}  BALL SPEED: {self.speed} pixels per second", False, white)
        self.screen.blit(font_surface, (self.screen_size[0] - 800, 5))

    def show_message(self, message):
        size = self.font.size(message)
        font_surface = self.font.render(message, False, white)
        x = (self.screen_size[0] - size[0]) / 2
        y = (self.screen_size[1] - size[1]) / 2
        self.screen.blit(font_surface, (x, y))

    def run(self):
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
            
            if self.menu_enabled:
                self.menu.update(events)
                self.menu.draw(self.screen)

            else:
                self.screen.fill(turquoise)
                self.check_input()

                if self.state == state_ballinpaddle:
                    self.ball.left = self.paddle.left + self.paddle_width / 2 - self.ball_radius
                    self.ball.top = self.paddle.top - self.ball_diameter
                    self.show_message("Press Space to launch the ball")

                elif self.state == state_gameover:
                    self.show_message("Game Over, Press Enter to Play again or Q to quit")

                elif self.state == state_won:
                    self.show_message("You Won! Press Enter to play again or Q to quit")

                elif self.state == state_inplay:
                    self.move_ball()
                    self.handle_coll()

                self.draw_with_shadow()
                self.draw_bricks()
                self.show_stats()
            pygame.display.update()
            self.clock.tick(self.fps)

    def set_fps(self, value, fps):
        self.fps = fps
        self.update_ball_velocity()
        self.update_paddle_speed()

    def set_ball_speed(self, value, speed):
        self.speed = speed
        self.update_ball_velocity()
    
    def update_paddle_speed(self):
        """Adjust paddle speed based on the current FPS."""
        # self.paddle_speed = 10 * (self.fps / 60)  # Scale the paddle speed based on FPS
        self.paddle_speed = 25 * (60/self.fps)

    def update_ball_velocity(self):
        speed_per_frame = self.speed / self.fps
        self.ballvel = [speed_per_frame / 1.414, -speed_per_frame / 1.414]

    def start_game(self):
        self.menu_enabled = False

game = BrickBreaker()
game.run()