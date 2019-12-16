import numpy as np
import json
'''
    An agent
'''

class SHBaseAgent:
    def __init__(self):
        self.agent_pos = (0, 0)
        self.sheep_pos = []
        self.ob = {}

    def distance(self, p1, p2):
        return np.sqrt(np.power((p1[0] - p2[0]), 2) + np.power((p1[1] - p2[1]), 2))

    def updateWorldState(self, world_state):
        if world_state.number_of_observations_since_last_state > 0:
            msg = world_state.observations[-1].text
            ob = json.loads(msg)
            if "entities" in ob:
                entities = ob["entities"]
                self.sheep_pos = []
                for e in entities:
                    if e["name"] == "Sheep":
                        self.sheep_pos.append((e["x"], e["z"]))
                    if e["name"] == "Jesus":
                        self.agent_pos = (e["x"], e["z"])

class ConvexHullAgent(SHBaseAgent):
    def __init__(self):
        super().__init__()
        self.agent_start = (0, 0)
        self.obj = (0, 0)
        self.obj_stack = []
    def orientation(self, p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - \
            (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0
        elif val > 0:
            return 1
        else:
            return -1
    def clear_stack(self):
        self.obj_stack = []

    def genConvexHull(self):
        # return a clock-wise sheep position start with the nearest sheep to the agent
        points = sorted(self.sheep_pos, key=lambda x: x[0])
        if len(self.sheep_pos) < 3:
            self.obj_stack = sorted(self.sheep_pos, key=lambda x: self.distance(self.agent_pos, x))
            return

        n = len(points)
        hull = []
        p = 1
        q = 0
        while True:
            hull.append(p)
            q = (p + 1) % n
            for i in range(n):
                if(self.orientation(points[p], points[i], points[q]) == -1):
                    q = i
            p = q
            if p == 1:
                break
        nearest = np.argmin([self.distance(self.agent_pos, self.sheep_pos[sheepidx]) for sheepidx in hull])
        aim = hull[nearest:] + hull[:nearest]
        self.obj_stack = [points[i] for i in aim]

        # set the final destimation to rightend of pen
        self.obj_stack.append((29, 15))
        self.obj_stack.append((44, 15))
        self.obj = self.obj_stack[0]
        self.agent_start = self.agent_pos
    
    def reachDest(self):
        return self.distance(self.agent_pos, self.obj) < 5

    def act(self):

        if self.reachDest():
            self.obj_stack.pop(0)
            if len(self.obj_stack) != 0:
                self.obj = self.obj_stack[0]
            else:
                return np.zeros((2,))
        
        v = np.array([self.obj[0] - self.agent_pos[0], self.obj[1] - self.agent_pos[1]])
        return v / (np.sqrt(np.power(v, 2).sum()))
        

        # tolerance = 0.1
        # vec = (self.obj[0] - self.agent_start[0], self.obj[1] - self.agent_start[1])
        # curr_vec = (self.obj[0] - self.agent_pos[0], self.obj[1] - self.agent_pos[1])

        # horizontal_mov = 3 if vec[0] >= 0 else 2
        # vertical_mov = 0 if vec[1] >= 0 else 1

        # if np.absolute(curr_vec[0]) <= tolerance:
        #     return vertical_mov
        # radian = np.arctan(vec[1] / vec[0])
        # curr_radian = np.arctan(vec[1] / vec[0])
        # if radian >= 0:
        #         return vertical_mov if curr_radian >= radian else horizontal_mov
        # else:
        #     return horizontal_mov if curr_radian >= radian else vertical_mov
