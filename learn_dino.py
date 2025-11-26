import os
import random
import pygame
import sys
from brain import QLearningAgent, TRAINING_EPISODES

pygame.init()

# GLOBAL SETTINGS
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Training Mode (Fast - No GUI)")

# ASSET LOADING
try:
    RUNNING = [pygame.image.load(os.path.join("assets/Dino", "DinoRun1.png")), pygame.image.load(os.path.join("assets/Dino", "DinoRun2.png"))]
    JUMPING = pygame.image.load(os.path.join("assets/Dino", "DinoJump.png"))
    DUCKING = [pygame.image.load(os.path.join("assets/Dino", "DinoDuck1.png")), pygame.image.load(os.path.join("assets/Dino", "DinoDuck2.png"))]
    SMALL_CACTUS = [pygame.image.load(os.path.join("assets/Cactus", "SmallCactus1.png")), pygame.image.load(os.path.join("assets/Cactus", "SmallCactus2.png")), pygame.image.load(os.path.join("assets/Cactus", "SmallCactus3.png"))]
    LARGE_CACTUS = [pygame.image.load(os.path.join("assets/Cactus", "LargeCactus1.png")), pygame.image.load(os.path.join("assets/Cactus", "LargeCactus2.png")), pygame.image.load(os.path.join("assets/Cactus", "LargeCactus3.png"))]
    BIRD = [pygame.image.load(os.path.join("assets/Bird", "Bird1.png")), pygame.image.load(os.path.join("assets/Bird", "Bird2.png"))]
    CLOUD = pygame.image.load(os.path.join("assets/Other", "Cloud.png"))
    BG = pygame.image.load(os.path.join("assets/Other", "Track.png"))
except Exception as e:
    print(f"Error loading assets: {e}")
    sys.exit()

class Dinosaur:
    X_POS = 80; Y_POS = 310; Y_POS_DUCK = 340; JUMP_VEL = 8.5
    def __init__(self):
        self.duck_img = DUCKING; self.run_img = RUNNING; self.jump_img = JUMPING
        self.dino_duck = False; self.dino_run = True; self.dino_jump = False
        self.step_index = 0; self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect(); self.dino_rect.x = self.X_POS; self.dino_rect.y = self.Y_POS
    def update(self, userInput):
        if self.dino_duck: self.duck()
        if self.dino_run: self.run()
        if self.dino_jump: self.jump()
        if self.step_index >= 10: self.step_index = 0
        # Simulating key presses
        if (userInput["UP"]) and not self.dino_jump:
            self.dino_duck = False; self.dino_run = False; self.dino_jump = True
        elif userInput["DOWN"] and not self.dino_jump:
            self.dino_duck = True; self.dino_run = False; self.dino_jump = False
        elif not (self.dino_jump or userInput["DOWN"]):
            self.dino_duck = False; self.dino_run = True; self.dino_jump = False
    def duck(self):
        self.image = self.duck_img[self.step_index // 5]; self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS; self.dino_rect.y = self.Y_POS_DUCK; self.step_index += 1
    def run(self):
        self.image = self.run_img[self.step_index // 5]; self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS; self.dino_rect.y = self.Y_POS; self.step_index += 1
    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4; self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.dino_jump = False; self.jump_vel = self.JUMP_VEL

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000); self.y = random.randint(50, 100)
        self.image = CLOUD; self.width = self.image.get_width()
    def update(self, game_speed):
        self.x -= game_speed
        if self.x < -self.width: self.x = SCREEN_WIDTH + random.randint(2500, 3000); self.y = random.randint(50, 100)

class Obstacle:
    def __init__(self, image, type):
        self.image = image; self.type = type
        self.rect = self.image[self.type].get_rect(); self.rect.x = SCREEN_WIDTH
    def update(self, game_speed, obstacles):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width: obstacles.pop(0)

class SmallCactus(Obstacle):
    def __init__(self, image): super().__init__(image, random.randint(0, 2)); self.rect.y = 325
class LargeCactus(Obstacle):
    def __init__(self, image): super().__init__(image, random.randint(0, 2)); self.rect.y = 300
class Bird(Obstacle):
    def __init__(self, image): super().__init__(image, 0); self.rect.y = random.choice([250, 290, 320]); self.index = 0

def train():
    agent = QLearningAgent()
    print("--- STARTING TRAINING FROM SCRATCH (FRESH BRAIN) ---")
    
    for episode in range(1, TRAINING_EPISODES + 1):
        player = Dinosaur(); cloud = Cloud(); game_speed = 20
        x_pos_bg = 0; points = 0; obstacles = []
        last_state = (3, 0, 0, 0) # Initial state
        last_action = 0; run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: agent.save_brain(); pygame.quit(); sys.exit()

            # 1. GET STATE
            obs_type = 0 # Default Cactus
            if len(obstacles) > 0:
                distance = obstacles[0].rect.x - player.dino_rect.x
                obs_y = obstacles[0].rect.y
                # IDENTIFY BIRD
                if isinstance(obstacles[0], Bird):
                    obs_type = 1
            else:
                distance = 1000; obs_y = 325

            current_state = agent.get_state(distance, obs_y, game_speed, obs_type)

            # 2. AI ACTION
            agent.learn(last_state, last_action, 1, current_state)
            action = agent.choose_action(current_state)

            ai_input = {"UP": False, "DOWN": False}
            if action == 1: ai_input["UP"] = True
            elif action == 2: ai_input["DOWN"] = True

            last_state = current_state
            last_action = action

            # 3. PHYSICS
            player.update(ai_input); cloud.update(game_speed)
            x_pos_bg -= game_speed
            if x_pos_bg <= -BG.get_width(): x_pos_bg = 0

            if len(obstacles) == 0:
                if random.randint(0, 2) == 0: obstacles.append(SmallCactus(SMALL_CACTUS))
                elif random.randint(0, 2) == 1: obstacles.append(LargeCactus(LARGE_CACTUS))
                elif random.randint(0, 2) == 2: obstacles.append(Bird(BIRD))

            for obstacle in obstacles:
                obstacle.update(game_speed, obstacles)
                if player.dino_rect.colliderect(obstacle.rect):
                    agent.learn(last_state, last_action, -100, current_state)
                    agent.update_epsilon()
                    
                    if episode % 100 == 0:
                        print(f"Ep: {episode} | Score: {points} | Eps: {agent.epsilon:.4f} | States: {len(agent.q_table)}")
                    
                    run = False; break

            points += 1
            if points % 100 == 0: game_speed += 1

    print("\n--- TRAINING COMPLETE ---")
    agent.save_brain()
    pygame.quit(); sys.exit()

if __name__ == "__main__":
    train()