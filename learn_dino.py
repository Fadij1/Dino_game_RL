import pygame
import sys
import random
from brain import QLearningAgent, TRAINING_EPISODES
# Import shared classes from dino_env
from dino_env import Dinosaur, Cloud, SmallCactus, LargeCactus, Bird, SCREEN, BG, SMALL_CACTUS, LARGE_CACTUS, BIRD

pygame.init()
pygame.display.set_caption("Training Mode (Fast - No GUI)")

def train():
    agent = QLearningAgent()
    # Optional: Load brain if you want to continue training, but usually safer to start fresh
    # agent.load_brain() 
    print("--- STARTING TRAINING ---")
    
    for episode in range(1, TRAINING_EPISODES + 1):
        player = Dinosaur()
        cloud = Cloud()
        game_speed = 20
        x_pos_bg = 0
        points = 0
        obstacles = []
        
        # Initial dummy state
        last_state = (3, 0, 0, 0, 0)
        last_action = 0
        run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    agent.save_brain()
                    pygame.quit()
                    sys.exit()

            # 1. GET STATE
            obs_type = 0
            obs_width = 0
            if len(obstacles) > 0:
                distance = obstacles[0].rect.x - player.dino_rect.x
                obs_y = obstacles[0].rect.y
                obs_width = obstacles[0].rect.width # <--- CAPTURE WIDTH
                
                if isinstance(obstacles[0], Bird):
                    obs_type = 1
            else:
                distance = 1000
                obs_y = 325
                obs_width = 0

            # Pass width to brain
            current_state = agent.get_state(distance, obs_y, game_speed, obs_type, obs_width)

            # 2. LEARN FROM PREVIOUS STEP
            agent.learn(last_state, last_action, 1, current_state)

            # 3. CHOOSE NEW ACTION
            action = agent.choose_action(current_state)

            # Convert Action to Inputs
            jump_input = False
            duck_input = False
            if action == 1:
                jump_input = True
            elif action == 2:
                duck_input = True

            last_state = current_state
            last_action = action

            # 4. PHYSICS UPDATE
            player.update(jump_input, duck_input)
            cloud.update(game_speed)
            x_pos_bg -= game_speed
            if x_pos_bg <= -BG.get_width():
                x_pos_bg = 0

            # Generate Obstacles
            if len(obstacles) == 0:
                if random.randint(0, 2) == 0:
                    obstacles.append(SmallCactus(SMALL_CACTUS))
                elif random.randint(0, 2) == 1:
                    obstacles.append(LargeCactus(LARGE_CACTUS))
                elif random.randint(0, 2) == 2:
                    obstacles.append(Bird(BIRD))

            # Update Obstacles & Check Collision
            # We iterate over a copy of the list to safely remove items
            for obstacle in list(obstacles):
                # Update returns True if off-screen
                if obstacle.update(game_speed):
                    obstacles.remove(obstacle)

                if player.dino_rect.colliderect(obstacle.rect):
                    # Collision! Punishment
                    agent.learn(last_state, last_action, -100, current_state)
                    agent.update_epsilon()
                    
                    if episode % 100 == 0:
                        print(f"Ep: {episode} | Score: {points} | Eps: {agent.epsilon:.4f} | States: {len(agent.q_table)}")
                    
                    run = False
                    break

            points += 1
            if points % 100 == 0:
                game_speed += 1

    print("\n--- TRAINING COMPLETE ---")
    agent.save_brain()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    train()