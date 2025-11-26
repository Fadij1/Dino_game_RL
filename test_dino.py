import pygame
import random
from brain import QLearningAgent
# Import shared classes from dino_env
from dino_env import Dinosaur, Cloud, SmallCactus, LargeCactus, Bird, SCREEN, BG, SMALL_CACTUS, LARGE_CACTUS, BIRD

pygame.init()
pygame.display.set_caption("Dino AI - TESTING MODE")

def test(agent):
    global game_speed, x_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    points = 0
    obstacles = []
    
    # Disable randomness for testing
    agent.epsilon = 0.0 

    def background():
        global x_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, 380))
        SCREEN.blit(BG, (image_width + x_pos_bg, 380))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False

        # 1. GET STATE
        obs_type = 0
        obs_width = 0
        if len(obstacles) > 0:
            distance = obstacles[0].rect.x - player.dino_rect.x
            obs_y = obstacles[0].rect.y
            obs_width = obstacles[0].rect.width # Capture width
            
            if isinstance(obstacles[0], Bird):
                obs_type = 1
        else:
            distance = 1000
            obs_y = 325
            obs_width = 0

        # Pass width to brain
        current_state = agent.get_state(distance, obs_y, game_speed, obs_type, obs_width)
        action = agent.choose_action(current_state)

        # 2. EXECUTE ACTION
        jump_cmd = False
        duck_cmd = False
        if action == 1: 
            jump_cmd = True
        elif action == 2:
            duck_cmd = True

        # 3. RENDER
        SCREEN.fill((255, 255, 255))
        player.update(jump_cmd, duck_cmd)
        player.draw(SCREEN)
        
        if len(obstacles) == 0:
            if random.randint(0, 2) == 0: obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1: obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2: obstacles.append(Bird(BIRD))

        for obstacle in list(obstacles): 
            obstacle.draw(SCREEN)
            # Check off-screen
            if obstacle.update(game_speed):
                obstacles.remove(obstacle)
            
            # Collision
            if player.dino_rect.colliderect(obstacle.rect):
                print(f"GAME OVER. Score: {points}")
                pygame.time.delay(1000)
                # Recursion reset (or just break loop to restart cleanly)
                test(agent) 
                return
            
        background()
        cloud.draw(SCREEN)
        cloud.update(game_speed)
        
        points += 1
        if points % 100 == 0: game_speed += 1
        
        text = pygame.font.Font("freesansbold.ttf", 20).render(f"TESTING SCORE: {points}", True, (0, 0, 0))
        SCREEN.blit(text, (800, 40))
        clock.tick(30)
        pygame.display.update()

if __name__ == "__main__":
    agent = QLearningAgent()
    agent.load_brain()
    test(agent)