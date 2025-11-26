import numpy as np
import random
import pickle

# ==============================================================================
#                               HYPERPARAMETERS
# ==============================================================================
TRAINING_EPISODES = 50000   # Total episodes to train
LEARNING_RATE = 0.01        
DISCOUNT_FACTOR = 0.95      

# EXPLORATION SETTINGS
EPSILON_START = 1.0         
EPSILON_END = 0.005          
# Decay Rate: 0.9999 ensures it explores for roughly ~40,000 episodes
# before settling down. This is crucial for long training (50k).
EPSILON_DECAY = 0.9999      
# ==============================================================================

class QLearningAgent:
    def __init__(self):
        self.epsilon = EPSILON_START
        self.alpha = LEARNING_RATE
        self.gamma = DISCOUNT_FACTOR
        self.actions = [0, 1, 2] # 0=Run, 1=Jump, 2=Duck
        self.q_table = {} 

    def get_state(self, distance, obstacle_y, speed, obstacle_type):
        """
        Input:
            distance: pixels to next obstacle
            obstacle_y: y-coordinate of obstacle (to distinguish height)
            speed: current game speed
            obstacle_type: 0 for Cactus, 1 for Bird
        """
        # 1. Distance Buckets
        if distance < 100: dist_state = 0
        elif distance < 200: dist_state = 1
        elif distance < 300: dist_state = 2
        elif distance < 450: dist_state = 3
        elif distance < 600: dist_state = 4
        else: dist_state = 5 

        # 2. Speed Buckets
        if speed < 20: speed_state = 0
        elif speed < 30: speed_state = 1
        elif speed < 40: speed_state = 2
        else: speed_state = 3

        # 3. Y Position Buckets (Height)
        if obstacle_y > 310: obs_state = 0   # Low (Small Cactus)
        elif obstacle_y > 280: obs_state = 1 # Mid (Large Cactus OR Low Bird)
        else: obs_state = 2                  # High (High Bird)

        # 4. Obstacle Type
        # Crucial fix: explicitly tells the brain "This is a Bird"
        type_state = obstacle_type

        return (dist_state, obs_state, speed_state, type_state)

    def choose_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)
        else:
            return np.argmax(self.q_table[state])

    def learn(self, state, action, reward, next_state):
        if state not in self.q_table: self.q_table[state] = [0, 0, 0]
        if next_state not in self.q_table: self.q_table[next_state] = [0, 0, 0]

        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        
        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[state][action] = new_value

    def update_epsilon(self):
        if self.epsilon > EPSILON_END:
            self.epsilon *= EPSILON_DECAY

    def save_brain(self):
        with open("dino_brain.pkl", "wb") as f:
            pickle.dump(self.q_table, f)

    def load_brain(self):
        try:
            with open("dino_brain.pkl", "rb") as f:
                self.q_table = pickle.load(f)
                print(f"Brain loaded! Size: {len(self.q_table)} states")
        except:
            print("No brain found, starting fresh.")