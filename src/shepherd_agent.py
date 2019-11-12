# shepherd_agent.py

# Shepherd class used to keep track of the agent
#   class methods:
#     - get_current_state
#     - agent_location
#     - sheep_location
#     - sheep_in_pen
#     - sheep_are_near
#     - end_mission
#     - update_q_table
#     - movement_towards_pen
#     - choose_action
#     - act (do an action)
#     - run (run the agent)

import random, json
from math import sqrt

class Shepherd():
    def __init__(self, alpha=0.3, gamma=1, n=1):
        """Constructing an RL agent.

        Args
            alpha:  <float>  learning rate      (default = 0.3)
            gamma:  <float>  value decay rate   (default = 1)
            n:      <int>    number of back steps to update (default = 1)
        """
        # q-learning variables
        self.epsilon = 0.2 # chance of taking a random action instead of the best
        self.q_table = {}
        self.n, self.alpha, self.gamma = n, alpha, gamma
        
        # world and agent variables
        self.prev_location = (0, 0)
        self.location = (0.5, 0.5)
        self.head_to_pen = False
        self.sheep = []
        self.possible_actions = {0: "move 1", 1: "move -1", 2: "strafe 1", 3: "strafe -1",
                                 4: "hotbar.2 1", 5: "hotbar.1 1"}
        
    def get_current_state(self, agent_host):
        "Get current state of the world and agent, update class variables"
        sheep_location = []
        while True:
            world_state = agent_host.getWorldState()
            if not world_state.is_mission_running:
                return
            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                ob = json.loads(msg)
                for ent in ob["entities"]:
                    if ent["name"] == "Jesus":
                        self.prev_location = self.location
                        self.location = (ent["x"], ent["z"])
                    if ent["name"] == "Sheep":
                        sheep_location.append((ent["x"], ent["z"]))
                self.sheep = sheep_location
                return
                        
    def agent_location(self):
        return self.location
    
    def sheep_location(self):
        return self.sheep
            
    def sheep_in_pen(self):
        count = 0
        for coord in self.sheep:
            x,z = coord
            if 30 < x < 50 and -10 < z < 10:
                count += 1
        return count

    # If there are any sheep in the arena that are within a Euclidean distance of 5 blocks, return True
    def sheep_are_near(self):
        for sheepy in self.sheep:
            sheep_x, sheep_z = sheepy
            christ_x, christ_z = self.location
            euclid_dist = sqrt(pow(sheep_x - christ_x, 2) + pow(sheep_z - christ_z, 2))
            if euclid_dist < 5:
                return True
        return False
    
    # End the mission after traveling to mission frontier within the pen 
    # (40th column of blocks east of arena's center block and inside of Pen borders)
    def end_mission(self):
        x,z = self.location
        return 39 < x < 50 and -10 < z < 10
    
    def update_q_table(self, tau, S, A, R, T): # got from assignment 2
        """Performs relevant updates for state tau.

        Args
            tau: <int>  state index to update
            S:   <dequqe>   states queue
            A:   <dequqe>   actions queue
            R:   <dequqe>   rewards queue
            T:   <int>      terminating state index
        """
        curr_s, curr_a, curr_r = S.popleft(), A.popleft(), R.popleft()
        G = sum([self.gamma ** i * R[i] for i in range(len(S))])
        if tau + self.n < T:
            G += self.gamma ** self.n * self.q_table[S[-1]][A[-1]]
            
        old_q = self.q_table[curr_s][curr_a]
        self.q_table[curr_s][curr_a] = old_q + self.alpha * (G - old_q)

    # Put agent on path towards the pen
    #NOTE: Function may break agent's behavior if we add turn based commands
    def movement_towards_pen(self):
        movement = ""
        x,z = self.location
        if -10 < z < 10:
            movement = self.possible_actions[1]
        elif z < 10:
            movement = self.possible_actions[2]
        elif z > -10:
            movement = self.possible_actions[3]
        return movement
    
    def choose_action(self, eps):
        # return a random move for now
        action = self.possible_actions[random.randint(0, 5)]
        # Check if actions are allowable or not recommended 
        # (e.g. drawing wheat when no sheep are near, walking to the pen without wheat drawn)
        if self.head_to_pen and self.sheep_are_near():
            return self.movement_towards_pen()
        elif action == "hotbar.2 1":
            if self.sheep_are_near():
                self.head_to_pen = True
                return action
            else:
                return "hotbar.1 1"
        else:
            return action
    
    def act(self, agent_host, action):
        if self.end_mission():
            agent_host.sendCommand('quit')
        else:
            agent_host.sendCommand(action)

    def run(self, agent_host):
        # run with random move, need to implement q-learning
        self.get_current_state(agent_host)
        action = self.choose_action(self.epsilon)
        self.act(agent_host, action)
    