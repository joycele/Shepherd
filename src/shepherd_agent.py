# shepherd-agent.py

# Use Shepherd class to represent DQL Shepherd Agent

# CODE IN THIS FILE IS MODELED AFTER THE FOLLOWING DEEP Q-LEARNING ARTICLES : 

# https://keon.io/deep-q-learning/?fbclid=IwAR0wf9ldsXcJjH6GkuKjhkDIX-Plbrc4-cveIeMEHDJqpcTb1THxFjqpx1k
# https://medium.com/@gtnjuvin/my-journey-into-deep-q-learning-with-keras-and-gym-3e779cc12762

import random
import numpy as np
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam


class Shepherd():
    
    def __init__(self, state_size):
        #self.possible_actions = {0: "movenorth 1", 1: "movesouth 1", 2: "moveeast 1", 3: "movewest 1",
        #                         4: "hotbar.2 1", 5: "hotbar.1 1"} # discrete
        self.possible_actions = {0: "move 1", 1: "move -1", 2: "strafe -1", 3: "strafe 1",
                                 4: "hotbar.2 1", 5: "hotbar.1 1"} # continuous
        self.state_size = state_size
        self.action_size = len(self.possible_actions)
        self.memory = deque(maxlen=500)
        self.epsilon = 0.15 # chance of taking a random action instead of the best
        self.alpha = 0.001 # learning rate
        self.gamma = 0.95
        self.model = self._build_model()
        self.prev_action = None
        self.holding_wheat = False
        self.number_actions_taken = 0
    
    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(self.state_size, input_shape=(self.state_size,), activation='relu'))
        model.add(Dense(self.state_size, activation='relu'))
        model.add(Dense(self.state_size, activation='relu'))
        model.add(Dense(self.action_size))
        model.compile(loss='mse', optimizer=Adam(lr=self.alpha))
        return model
    
    def predict(self, state):
        if (state.ndim == 1):
            state = np.array([state])
        return self.model.predict(state)
    
    def fit(self, state, target_model):
        if (state.ndim == 1):
            state = np.array([state])
        self.model.fit(state, target_model, epochs=1, verbose=0)
    
    def perform_action(self, action, agent_host):
        agent_host.sendCommand(self.possible_actions[action])
        self.number_actions_taken += 1
        self.prev_action = action
        
    def act(self, world, state) -> int:
        x, z = world.agent_location
        if world.sheep_are_near(4) == 0 and self.holding_wheat:
            self.holding_wheat = False
            return 5  # let go of wheat if no sheep are near
        if world.sheep_are_near(2) > 0 and self.prev_action != 4:
            self.holding_wheat = True
            return 4  # pull out wheat if sheep are near
        if x <= 15:
            return 2 # once in pen, move towards end of pen
        if np.random.rand() <= self.epsilon:
            return random.randrange(4)
        act_values = self.predict(state)
        return np.argmax(act_values[0])  
    
    def remember(self, state, action, reward, next_state, done):
        experience = (state, action, reward, next_state, done)
        self.memory.append(experience)
        
    # once Shepherd agent has ran through enough missions, start training
    def replay(self, sample_batch_size):
        if len(self.memory) < sample_batch_size:
            # agent has not run enough missions
            return
        sample_batch = random.sample(self.memory, sample_batch_size)
        for state, action, reward, next_state, done in sample_batch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.predict(next_state)[0])
            target_model = self.predict(state)
            target_model[0][action] = target
            self.fit(state, target_model)
    
    # run the agent
    def run(self, world, agent_host):
        state = world.get_flattened_state()
        done = False
        if not done:
            action = self.act(world, state)
            self.perform_action(action, agent_host)
            reward, next_state, done = world.update_farm_state(action, agent_host)
            self.remember(state, action, reward, next_state, done)
            state = next_state
        self.replay(sample_batch_size)
        