import numpy as np
import random
from tensorflow.keras import Model, Sequential
from tensorflow.keras.layers import Dense, Embedding, Reshape, Flatten
from tensorflow.keras.optimizers import Adam
from collections import deque

class SHAgent:

    def __init__(self, ob_size, act_size):

        # basic attributes
        self.observation_space_size = ob_size
        self.action_space_size = act_size
        self.replay = deque(maxlen=300)

        # q network parameters
        self.epsilon = 0.1
        self.gamma = 0.6
        self.alpha = 0.01

        # q network model initialization
        self.optimizer = Adam(learning_rate=self.alpha)
        self.q_network = self.build_model()
        self.target_network = self.build_model()
        self.synchronize_target_model()

    def store(self, state, action, reward, next_state, done):
        # store to replay memory replay
        self.replay.append((state, action, reward, next_state, done))

    def random_act(self):
        return random.randint(0,5)

    def build_model(self):
        # tf model
        model = Sequential()
        model.add(Dense(10, input_shape=(self.observation_space_size,), activation='relu'))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(self.action_space_size, activation='linear'))
        model.compile(loss='mean_squared_error', optimizer=self.optimizer)
        return model

    def synchronize_target_model(self):
        # align model weights to q_network
        self.target_network.set_weights(self.q_network.get_weights())

    def act(self, state):
        # randomly select action if less than opsilon
        # ortherwise choose the action with the highest q value

        if random.random() <= self.epsilon:
            return random.randint(0, self.action_space_size - 1)
        return np.argmax(self.q_network.predict(state)[0])

    def train(self, batch_size):
        # retain the neural network with past memory

        batchpoll = random.sample(self.replay, batch_size)

        for state, action, reward, next_state, done in batchpoll:
            target = self.q_network.predict(state)
            if done:
                target[0][action] = reward
            else:
                t = self.target_network.predict(next_state)
                target[0][action] = reward + self.gamma * np.amax(t)
            self.q_network.fit(state, target, epochs=1,verbose=0)
