import numpy as np
import random
import pickle

class QLearningAgent:
    def __init__(self):
        # Hyperparameters
        self.epsilon = 0.1       # Randomness (Exploration rate)
        self.alpha = 0.1         # Learning Rate (How fast we learn)
        self.gamma = 0.99        # Discount Factor (Future reward importance)
        
        # Action Space: 0 = Run, 1 = Jump, 2 = Duck
        self.actions = [0, 1, 2]
        
        # The Q-Table (Dictionary)
        # Maps state (tuple) -> [Q_value_Run, Q_value_Jump, Q_value_Duck]
        self.q_table = {} 

    def get_state(self, distance, obstacle_y, speed):
        # 1. Discretize Distance (Simplify logic)
        if distance < 100: dist_state = 0   # DANGER
        elif distance < 250: dist_state = 1 # Close
        elif distance < 400: dist_state = 2 # Medium
        else: dist_state = 3                # Far

        # 2. Discretize Speed
        if speed < 20: speed_state = 0
        elif speed < 30: speed_state = 1
        else: speed_state = 2

        # 3. Discretize Obstacle Type (Based on Y position)
        if obstacle_y > 310: obs_state = 0  # Low (Small Cactus) or High Bird
        elif obstacle_y > 280: obs_state = 1 # Mid (Large Cactus)
        else: obs_state = 2                 # High (Low Bird - MUST DUCK)

        return (dist_state, obs_state, speed_state)

    def choose_action(self, state):
        # Ensure state exists in Q-table
        if state not in self.q_table:
            self.q_table[state] = [0, 0, 0]

        # Epsilon-Greedy Strategy
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions) # Explore (Random)
        else:
            return np.argmax(self.q_table[state]) # Exploit (Best known action)

    def learn(self, state, action, reward, next_state):
        # Ensure states exist
        if state not in self.q_table: self.q_table[state] = [0, 0, 0]
        if next_state not in self.q_table: self.q_table[next_state] = [0, 0, 0]

        # Q-Learning Formula
        old_value = self.q_table[state][action]
        next_max = np.max(self.q_table[next_state])
        
        # New Q = Old Q + Alpha * (Reward + Gamma * Max_Future_Q - Old_Q)
        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[state][action] = new_value

    def save_brain(self):
        with open("dino_brain.pkl", "wb") as f:
            pickle.dump(self.q_table, f)
            print("Brain saved!")

    def load_brain(self):
        try:
            with open("dino_brain.pkl", "rb") as f:
                self.q_table = pickle.load(f)
                print("Brain loaded!")
        except:
            print("No brain found, starting fresh.")