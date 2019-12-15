import math, json
import numpy as np


class WorldObserver:
    def __init__(self):
        self.state = np.zeros((50,50))
        self.agent_pos = (0,0)
        self.sheep_pos= []

    def getEnvState(self, world_state):
        # update world states
        info = "old"
        if world_state.number_of_observations_since_last_state > 0:
            self.state = np.zeros((50,50))
            info = "new"
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            if "entities" in ob:
                entities = ob["entities"]
                self.sheep_pos = []
                for e in entities:
                    if e["name"] == "Sheep":
                        self.sheep_pos.append((e["x"], e["z"]))
                        self.state[math.floor(e["x"])][math.floor(e["z"])] = 125
                    if e["name"] == "Jesus":
                        self.agent_pos = (e["x"], e["z"])
                        self.state[math.floor(e["x"])][math.floor(e["z"])] = 255
        reward = self.getReward()
        done = self.isEnd()
        return (self.state.reshape(-1, self.state.size), reward, done, info)

    def isEnd(self):
        # need agent pos
        if self.agent_pos[0] >= 43:
            return True
        if (self.agent_pos[0] >= 31) and (self.agent_pos[1] <= 11 or self.agent_pos[1] >= 21):
            return True
        return False

    def numOfSheepInPen(self):
        num = 0
        for x, z in self.sheep_pos:
            if x >= 31:
                num += 1
        return num

    def distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def numOfSheepNearBy(self):
        num = 0
        for sheep in self.sheep_pos:
            if self.distance(self.agent_pos, sheep) <= 8:
                num += 1
        return num

    def sheepDistToPen(self):
        dist = .0
        for sheep in self.sheep_pos:
            dist  += self.distance(sheep, (43,15))
        return dist

    def agentInPen(self):
        return self.agent_pos[0] >= 31

    def getReward(self):
        # need agent pos and sheep pos
        # use self.agent
        reward = 0
        reward += self.numOfSheepInPen() * 100
        reward += self.agentInPen() * 50
        reward += self.numOfSheepNearBy() * 10
        reward -= self.sheepDistToPen()

        # print("dist penality:", self.sheepDistToPen(), "near:", self.numOfSheepNearBy())
        return reward