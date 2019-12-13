# farm.py

# Use Farm class to keep track of the 30x50 numpy array used to represent the Farm.
# In each update of the Farm state, also calculate reward
#     
#    array[x][z] = entity at (x,z) coordinate
#    entity values : 0 = nothing important, 1 = sheep, 2 = agent
#

import math, json
import numpy as np


class Farm():
    def __init__(self):
        self.initialize()
    
    def initialize(self):
        self.world = np.zeros((31, 51)) 
        
        self.agent_location = (32, 15) # starting coords of agent
        self.prev_agent_location = (0, 0)
        self.action = 0
        self.sheep = []
        self.end_mission = False
        self.number_calculations = 0
        self.total_reward = 0
        
    def sheep_in_pen(self) -> int:
        count = 0
        for coord in self.sheep:
            x,z = coord
            if 30 < x < 50 and -10 < z < 10:
                count += 1
        return count
    
    def agent_in_pen(self) -> bool:
        x,z = self.agent_location
        return 0 < x < 15
    
    def get_flattened_state(self):
        return self.world.reshape(-1)
    
    @staticmethod
    def dist_to_entity(ent1: tuple, ent2: tuple) -> float:
        # calculate euclidean distance between two entity locations
        x1, z1 = ent1
        x2, z2 = ent2
        return math.sqrt(pow(x1 - x2, 2) + pow(z1 - z2, 2))
    
    # Return number of sheep in the arena that are within a Euclidean distance of 5 blocks
    def sheep_are_near(self, distance) -> int:
        near = 0
        for sheepy in self.sheep:
            if self.dist_to_entity(self.agent_location, sheepy) < distance:
                near += 1
        return near
    
    
    # evaluate sheep locations, agent location, action and previous action
    def calculate_reward(self, action):
        self.number_calculations += 1
        # base reward: -1 for each step taken
        reward = -1 
        if action == 4 or action == 5: 
            # taking out/putting away wheat is hard coded, so just return reward
            return reward
        
        # give 500 for each sheep found in pen, 200 for agent reaching pen
        if self.agent_in_pen():
            print("agent in pen!")
            reward = 200
            for i in range(self.sheep_in_pen()):
                print("rewarding sheep")
                reward += 500
        else:
            # negative reward for distance from pen
            reward -= self.agent_location[0] - 15
            for sheep in self.sheep:
                dist_to_agent = self.dist_to_entity(self.agent_location, sheep)
                if dist_to_agent < 4:
                    reward += 100 # positive reward for staying near sheep
                else:
                    reward -= dist_to_agent # negative reward for distance to sheepies
                    
        # discourage wasted/repetitive actions
        if action == self.action:
            reward -= 100
        self.total_reward += reward
        return reward
    
    
    # given an action, update the state of the Farm and calculate a reward
    def update_farm_state(self, action, agent_host):
        world_state = agent_host.getWorldState()
        reward = -1
        if world_state.number_of_observations_since_last_state > 0:
            sheep_locations = []
            self.world = np.zeros((31, 51))
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            for ent in ob["entities"]:
                x = int(ent["x"])
                z = int(ent["z"])
                if ent["name"] == "Jesus":
                    self.prev_agent_location = self.agent_location
                    self.agent_location = (x, z)
                    self.world[z][x] = 2
                if ent["name"] == "Sheep":
                    sheep_locations.append((x, z))
                    self.world[z][x] = 1
            self.sheep = sheep_locations
            reward = self.calculate_reward(action)
        if self.agent_location[0] <= 5:
            self.end_mission = True
        self.action = action
        next_state = self.world.reshape(-1)
        return reward, next_state, self.end_mission
            
