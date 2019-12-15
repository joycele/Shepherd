import gym
import random
from gym import spaces
import numpy as np
from math import sqrt

metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second' : 60
        }

ACTION_MAP = {
    0: ( 0,  0),
    1: ( 1,  0),
    2: (-1,  0),
    3: ( 0,  1),
    4: ( 0, -1),
    5: ( 1,  1),
    6: (-1, -1),
    7: ( 1, -1),
    8: (-1,  0)
}

STAGE_WIDTH = 60
STAGE_HEIGHT = 60
SHEEP_NUM = 2
YARD_SIZE = 10
DEFAULT_POSITION = (0, 0)
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 600
LURING_RADIUS = 8

class SheepHerderEnvironment(gym.Env):
    def __init__(self):
        self.sheepNum = 5
        self.sheepList = np.zeros((self.sheepNum, 2))
        self.sheepInYard = np.zeros((self.sheepNum)).astype(bool)
        self.viewer = None
        self.pos = (0, 0)
        self.action_space = spaces.Discrete(9)
        self.observation_space = spaces.Dict({
            "agent": spaces.Box(low=np.array([-STAGE_WIDTH/2, -STAGE_HEIGHT/2]),
                                high=np.array([STAGE_WIDTH/2,STAGE_HEIGHT/2]),
                                dtype=np.float32),
            "sheep": spaces.Box(low=min(-STAGE_WIDTH, -STAGE_HEIGHT), high=max(STAGE_WIDTH, STAGE_HEIGHT), shape=(5,2), dtype=np.float32)
        })
        self.frame = 0
        self.agentVel = 4.3/60
        self.sheepVel = 4.19/60
        self.stageSize = (STAGE_WIDTH, STAGE_HEIGHT)
        self.yardSize = (10, 10)
        self.yardPos = (0, 0)

    def _take_action(self, action):
        pass

    def inStage(self):
        return ((-self.stageSize[0]/2 <= self.pos[0] <= self.stageSize[0]/2) 
            and (-self.stageSize[1]/2 <= self.pos[1] <= self.stageSize[1]/2))

    def inYard(self, pos):
        return ((self.yardPos[0] - self.yardSize[0]/2 < pos[0] < self.yardPos[0] + self.yardSize[0]/2)
            and (self.yardPos[1] - self.yardSize[1]/2 < pos[1] < self.yardPos[1] + self.yardSize[1]/2))

    def inAttractionRange(self, obj1, obj2, dist):
        return (obj1[0] - obj2[0])**2 + (obj1[1] - obj2[1])**2 <= dist**2

    def unitVector(self, pos1, pos2):
        base = sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        return np.array([(pos1[0] - pos2[0])/base, (pos1[1] - pos2[1])/base])

    def collisionBound(self, pos, bound):
        if pos[0] < bound["l"]:
            pos = (bound["l"], pos[1])
        if pos[0] > bound["r"]:
            pos = (bound["r"], pos[1])
        if pos[1] < bound["b"]:
            pos = (pos[0], bound["b"])
        if pos[1] > bound["t"]:
            pos = (pos[0], bound["t"])
        return pos

    def step(self, action):

        # agent position update
        self.pos = (self.pos[0] + ACTION_MAP[action][0] * self.agentVel,
                    self.pos[1] + ACTION_MAP[action][1] * self.agentVel)
        # Bounding box detection
        agent_bound = {
            "l": -0.5*self.stageSize[0],
            "r":  0.5*self.stageSize[0],
            "b": -0.5*self.stageSize[1],
            "t":  0.5*self.stageSize[1]
        }
        self.pos = self.collisionBound(self.pos, agent_bound)

        # sheep attraction
        yard_bound = {
            "l": self.yardPos[0] - 0.5*self.yardSize[0],
            "r": self.yardPos[0] + 0.5*self.yardSize[0],
            "b": self.yardPos[1] - 0.5*self.yardSize[1],
            "t": self.yardPos[1] + 0.5*self.yardSize[1]
        }
        for i in range(self.sheepNum):
            if self.inAttractionRange(self.sheepList[i], self.pos, LURING_RADIUS):
                self.sheepList[i] += self.unitVector(self.pos, self.sheepList[i]) * self.sheepVel
            if self.inYard(self.sheepList[i]):
                self.sheepInYard[i] = True
            if self.sheepInYard[i]:
                self.sheepList[i] = self.collisionBound(self.sheepList[i], yard_bound)

    def reset(self):
        self.pos = DEFAULT_POSITION
        self.sheepList = (np.random.rand(self.sheepNum, 2) - 0.5) * self.stageSize
        

    def render(self, mode="human", close=False):
        Xcanvas = CANVAS_WIDTH
        Ycanvas = CANVAS_HEIGHT
        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(Xcanvas, Ycanvas)

            # Add yard on canvas
            l,r,t,b = -0.5*Xcanvas*self.yardSize[0]/self.stageSize[0],\
                       0.5*Xcanvas*self.yardSize[0]/self.stageSize[0],\
                      -0.5*Ycanvas*self.yardSize[1]/self.stageSize[1],\
                       0.5*Ycanvas*self.yardSize[1]/self.stageSize[1]

            yard = rendering.FilledPolygon([(l,b), (l,t), (r,t), (r,b)])
            yard.set_color(.0,1.0,.0)
            self.yardtrans = rendering.Transform()
            yard.add_attr(self.yardtrans)
            self.viewer.add_geom(yard)

            # Add agent on canvas
            agent = rendering.make_circle()
            agent.set_color(1.0,.0,.0)
            self.agenttrans = rendering.Transform()
            agent.add_attr(self.agenttrans)
            self.viewer.add_geom(agent)

            # Add sheep on canvas
            sheepherd = [rendering.make_circle() for i in range(self.sheepNum)]
            self.sheepherd_trans = [rendering.Transform() for i in range(self.sheepNum)]
            for i in range(self.sheepNum):
                sheepherd[i].set_color(.0,.0,1.0)
                sheepherd[i].add_attr(self.sheepherd_trans[i])
                self.viewer.add_geom(sheepherd[i])

        # draw agent position to canvas
        x_coord = (0.5 + self.pos[0]/self.stageSize[0]) * Xcanvas
        y_coord = (0.5 + self.pos[1]/self.stageSize[1]) * Ycanvas
        self.agenttrans.set_translation(x_coord, y_coord)

        # draw yard position
        x_coord = (0.5 + self.yardPos[0]/self.stageSize[0]) * Xcanvas
        y_coord = (0.5 + self.yardPos[1]/self.stageSize[1]) * Ycanvas
        self.yardtrans.set_translation(x_coord, y_coord)

        # draw sheep herd position to canvas
        for i in range(self.sheepNum):
            x_sheep = (0.5 + self.sheepList[i][0]/self.stageSize[0]) * Xcanvas
            y_sheep = (0.5 + self.sheepList[i][1]/self.stageSize[0]) * Xcanvas
            self.sheepherd_trans[i].set_translation(x_sheep, y_sheep)

        return self.viewer.render(return_rgb_array = mode=='rgb_array')

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None