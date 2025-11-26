import pygame
import random
import os
import datetime
# Import shared classes from dino_env
from dino_env import Dinosaur, Cloud, SmallCactus, LargeCactus, Bird, SCREEN, SCREEN_WIDTH, SCREEN_HEIGHT, BG, SMALL_CACTUS, LARGE_CACTUS, BIRD

pygame.init()
pygame.display.set_caption("Chrome Dino Runner - Human Mode")
Ico = pygame.image.load("assets/DinoWallpaper.png")
pygame.display.set_icon(Ico)

FONT_COLOR = (0, 0, 0)

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

    def score():
        global points, game_speed
        points += 1
        if points % 100 == 0:
            game_speed += 1
        
        # Simple High Score Logic
        highscore = 0
        if os.path.exists("score.txt"):
            with open("score.txt", "r") as f:
                try:
                    score_ints = [int(x) for x in f.read().split()]
                    if score_ints:
                        highscore = max(score_ints)
                except:
                    pass
        
        if points > highscore:
            highscore = points
            
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

        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            SCREEN.fill((255, 255, 255))
        else:
            SCREEN.fill((0, 0, 0))
            
        # Get Keyboard Input
        userInput = pygame.key.get_pressed()
        jump_cmd = userInput[pygame.K_UP] or userInput[pygame.K_SPACE]
        duck_cmd = userInput[pygame.K_DOWN]

        player.draw(SCREEN)
        player.update(jump_cmd, duck_cmd)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        # FIXED OBSTACLE LOOP
        for obstacle in list(obstacles):
            obstacle.draw(SCREEN)
            # update returns True if off-screen
            if obstacle.update(game_speed):
                obstacles.remove(obstacle)
            
            if player.dino_rect.colliderect(obstacle.rect):
                pygame.time.delay(1000)
                death_count += 1
                menu(death_count)

        background()
        cloud.draw(SCREEN)
        cloud.update(game_speed)
        score()

        clock.tick(30)
        pygame.display.update()

def menu(death_count):
    global points
    global FONT_COLOR
    run = True
    while run:
        current_time = datetime.datetime.now().hour
        if 7 < current_time < 19:
            FONT_COLOR = (0, 0, 0)
            SCREEN.fill((255, 255, 255))
        else:
            FONT_COLOR = (255, 255, 255)
            SCREEN.fill((128, 128, 128))
        font = pygame.font.Font("freesansbold.ttf", 30)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, FONT_COLOR)
        elif death_count > 0:
            text = font.render("Press any Key to Restart", True, FONT_COLOR)
            score_label = font.render("Your Score: " + str(points), True, FONT_COLOR)
            scoreRect = score_label.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score_label, scoreRect)
            
            # Save Score
            with open("score.txt", "a") as f:
                f.write(str(points) + "\n")
                
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                main()

if __name__ == "__main__":
    menu(death_count=0)