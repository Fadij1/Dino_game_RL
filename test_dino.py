import datetime
import os
import random
import pygame
import numpy as np

from brain import QLearningAgent

pygame.init()

# ==========================================
# CONSTANTS & SETUP
# ==========================================
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Dino AI - TESTING MODE")

# Assets Loading
try:
    Ico = pygame.image.load("assets/DinoWallpaper.png")
    pygame.display.set_icon(Ico)

    RUNNING = [
        pygame.image.load(os.path.join("assets/Dino", "DinoRun1.png")),
        pygame.image.load(os.path.join("assets/Dino", "DinoRun2.png")),
    ]
    JUMPING = pygame.image.load(os.path.join("assets/Dino", "DinoJump.png"))
    DUCKING = [
        pygame.image.load(os.path.join("assets/Dino", "DinoDuck1.png")),
        pygame.image.load(os.path.join("assets/Dino", "DinoDuck2.png")),
    ]

    SMALL_CACTUS = [
        pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")),
        pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")),
        pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png")),
    ]
    LARGE_CACTUS = [
        pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")),
        pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")),
        pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png")),
    ]

    BIRD = [
        pygame.image.load(os.path.join("assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("assets/Bird", "Bird2.png")),
    ]

    CLOUD = pygame.image.load(os.path.join("assets/Other", "Cloud.png"))
    BG = pygame.image.load(os.path.join("assets/Other", "Track.png"))
except Exception as e:
    print(f"Error loading assets: {e}")
    exit()

FONT_COLOR = (0, 0, 0)
game_speed = 20
x_pos_bg = 0
y_pos_bg = 380
points = 0
obstacles = []

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        # AI Control logic handled in main loop, here we just update physics
        pass

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    BIRD_HEIGHTS = [250, 290, 320]

    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = random.choice(self.BIRD_HEIGHTS)
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1


def background():
    global x_pos_bg, y_pos_bg
    image_width = BG.get_width()
    SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
    SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
    if x_pos_bg <= -image_width:
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        x_pos_bg = 0
    x_pos_bg -= game_speed


def test(agent):
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font("freesansbold.ttf", 20)
    obstacles = []
    
    # Force epsilon to 0 so the agent strictly uses what it learned
    agent.epsilon = 0.0

    print("--- TESTING MODE STARTED ---")
    print("Exploration (Randomness) disabled.")
    print(f"Loaded Brain Size: {len(agent.q_table)} states")

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        # 1. GET STATE
        if len(obstacles) > 0:
            distance = obstacles[0].rect.x - player.dino_rect.x
            obs_y = obstacles[0].rect.y
        else:
            distance = 1000 
            obs_y = 325

        current_state = agent.get_state(distance, obs_y, game_speed)

        # 2. CHOOSE ACTION (Greedy, because epsilon is 0)
        action = agent.choose_action(current_state)

        # 3. EXECUTE ACTION
        # 0 = Run, 1 = Jump, 2 = Duck
        if action == 1: 
            if not player.dino_jump:
                player.dino_duck = False
                player.dino_run = False
                player.dino_jump = True
        elif action == 2:
            if not player.dino_jump:
                player.dino_duck = True
                player.dino_run = False
                player.dino_jump = False
        else: # Action 0
            player.dino_duck = False
            player.dino_run = True
            player.dino_jump = False

        # NOTE: No agent.learn() here! We are just testing.

        # Draw Environment
        SCREEN.fill((255, 255, 255))
        player.draw(SCREEN)
        player.update(pygame.key.get_pressed())

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            
            # COLLISION
            if player.dino_rect.colliderect(obstacle.rect):
                print(f"GAME OVER. Final Score: {points}")
                pygame.time.delay(1000)
                # Restart automatically for testing
                test(agent)
                return

        background()
        cloud.draw(SCREEN)
        cloud.update()

        # Score Display
        points += 1
        if points % 100 == 0:
            game_speed += 1
        text = font.render(f"TESTING SCORE: {points}", True, (0, 0, 0))
        SCREEN.blit(text, (800, 40))

        # IMPORTANT: Run at normal human speed
        clock.tick(30)
        pygame.display.update()

if __name__ == "__main__":
    # Initialize agent and load the brain file
    agent = QLearningAgent()
    agent.load_brain()
    
    # Run the test loop
    test(agent)