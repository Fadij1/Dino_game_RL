import datetime
import os
import random
import pygame

from brain import QLearningAgent # Import your new class

pygame.init()
# ==========================================
# GLOBAL VARIABLES
# ==========================================
MAX_EPISODES = 100 
current_episode = 0
points = 0
# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Chrome Dino Runner")

# Assets Loading (Ensure the 'assets' folder is in the same directory)
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
    print("Make sure you have the 'assets' folder in the same directory!")
    exit()

FONT_COLOR = (0, 0, 0)

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

        if (userInput[pygame.K_UP] or userInput[pygame.K_SPACE]) and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput[pygame.K_DOWN] and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not (self.dino_jump or userInput[pygame.K_DOWN]):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

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


def main():
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
    death_count = 0
    pause = False

    # =========================================================
    # 1. INITIALIZE THE BRAIN (Before the game loop starts)
    # =========================================================
    agent = QLearningAgent()
    # If you have a saved brain, uncomment the next line:
    agent.load_brain() 
    
    # We need a default state to start the loop
    last_state = (3, 0, 0) # (Far, Low Obstacle, Slow)
    last_action = 0        # Run
    # =========================================================

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        
        if not os.path.exists("score.txt"):
            with open("score.txt", "w") as f: f.write("0")

        with open("score.txt", "r") as f:
            content = f.read()
            score_ints = [int(x) for x in content.split()] if content else [0]
            highscore = max(score_ints) if score_ints else 0
            if points > highscore: highscore = points
            
            text = font.render(f"High Score: {highscore}  Points: {points}", True, FONT_COLOR)
        
        textRect = text.get_rect()
        textRect.center = (900, 40)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    def unpause():
        nonlocal pause, run
        pause = False
        run = True

    def paused():
        nonlocal pause
        pause = True
        font = pygame.font.Font("freesansbold.ttf", 30)
        text = font.render("Game Paused, Press 'u' to Unpause", True, FONT_COLOR)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        SCREEN.blit(text, textRect)
        pygame.display.update()

        while pause:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_u:
                    unpause()

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                run = False
                paused()

        # =========================================================
        # 2. GET CURRENT STATE (What does the AI see?)
        # =========================================================
        if len(obstacles) > 0:
            distance = obstacles[0].rect.x - player.dino_rect.x
            obs_y = obstacles[0].rect.y
        else:
            distance = 1000 # Safe distance if no obstacles
            obs_y = 325

        current_state = agent.get_state(distance, obs_y, game_speed)

        # =========================================================
        # 3. AI LEARNING & DECISION STEP
        # =========================================================
        
        # A. Learn from the PREVIOUS move
        # We survived since the last frame, so give a small reward (+1)
        agent.learn(last_state, last_action, 1, current_state)

        # B. Decide NEXT move
        action = agent.choose_action(current_state)

        # C. Execute the Move
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
        else: # Action 0 (Run)
            player.dino_duck = False
            player.dino_run = True
            player.dino_jump = False

        # D. Update Memory for next loop
        last_state = current_state
        last_action = action
        # =========================================================

        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            SCREEN.fill((255, 255, 255))
        else:
            SCREEN.fill((0, 0, 0))
        
        userInput = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.update(userInput)

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
            
            # COLLISION DETECTION (DEATH)
            if player.dino_rect.colliderect(obstacle.rect):
                
                # =================================================
                # 4. PUNISH THE AI
                # =================================================
                # Agent died! Give a huge negative reward (-100)
                agent.learn(last_state, last_action, -100, current_state)
                agent.save_brain() # Save progress
                print(f"Dead! Total Points: {points} | Saving Brain...")
                # =================================================

                pygame.time.delay(2000)
                death_count += 1
                menu(death_count)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        #clock.tick(30)
        #pygame.display.update()

def menu(death_count):
    global points
    global FONT_COLOR
    
    # 1. Save the score logic (Keep this)
    if not os.path.exists("score.txt"):
        with open("score.txt", "w") as f: f.write("0")

    with open("score.txt", "a") as f:
        f.write(str(points) + "\n")
    
    # 2. Print status to console so you know it's working
    print(f"Generation: {death_count} | Score: {points} | Restarting automatically...")

    # 3. DIRECTLY RESTART THE GAME (Bypass the "Press Key" screen)
    # We add a tiny delay just so your CPU doesn't explode, 
    # but for fast training, you can remove the delay.
    pygame.time.delay(100) 
    main()
# Entry point
if __name__ == "__main__":
    menu(death_count=0)