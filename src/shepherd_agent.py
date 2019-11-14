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

import random, json, sys, time
from collections import defaultdict, deque
from create_world import NUMBER_OF_SHEEP
from math import sqrt

class Shepherd():
    #NOTE: Need penalty for death eventually
    rewards_ledger = {
        "per sheep herded": 1,
        "all sheep herded": 100,
        "no sheep herded": -100,
        "pen not reached": -150
    }

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
        self.possible_actions = {0: "move 0.5", 1: "move -0.5", 2: "strafe 0.5", 3: "strafe -0.5",
                                 4: "hotbar.2 1", 5: "hotbar.1 1"}

    def state_to_reward(self, state):
        current_r = 0
        christ_x, christ_z = self.location
        sheep_saved = self.sheep_in_pen()
        # Check if Shepherd made it to pen
        if christ_x < 30 and -10 < christ_z < 10:
            current_r += self.rewards_ledger["pen not reached"]
        # Check how many sheep were saved
        if sheep_saved == 0:
            current_r += self.rewards_ledger["no sheep herded"]
        elif sheep_saved < NUMBER_OF_SHEEP:
            current_r += self.rewards_ledger["no sheep herded"]
        elif sheep_saved == NUMBER_OF_SHEEP:
            current_r += self.rewards_ledger["all sheep herded"]
        return current_r

    # Update class attributes based on observations from the environment as present instant
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
                return (self.location, (ent["x"], ent["z"]))

        # State for Q-table is defined as ( AVG_DIST, MISS_END ) where
    
    #   - AVG_DIST = Average distance in blocks between Agent and each sheep
    #   - MISS_END = Distance between agent and mission termination frontier)
    def get_q_state(self):
        int_christ_loc = self.location
        distance_sum  = 0
        for sheepy in self.sheep:
            distance_sum = self.dist_to_entity(sheepy)
        avg_distance = distance_sum / len(self.sheep)
        return (round(self.dist_to_mission_end()), round(avg_distance))

    def agent_location(self):
        return self.location
    
    def sheep_location(self):
        return self.sheep

    # Determine if there are sheep within the Pen's coordinates        
    def sheep_in_pen(self):
        count = 0
        for coord in self.sheep:
            x,z = coord
            if 30 < x < 50 and -10 < z < 10:
                count += 1
        return count

    # Utility function to find distance to entity from Agent
    # Will be used in state calculation and sheep_are_near
    def dist_to_entity(self, ent):
        sheep_x, sheep_z = ent
        christ_x, christ_z = self.location
        return sqrt(pow(sheep_x - christ_x, 2) + pow(sheep_z - christ_z, 2))

    # Utiliity function to find distance to mission termination from Agent
    # Will be used in state calculation
    def dist_to_mission_end(self):
        x,z = self.location
        if x < 0:
            x*=-1
            return x + 39
        else:
            return 39 - x

    # If there are any sheep in the arena that are within a Euclidean distance of 5 blocks, return True
    def sheep_are_near(self):
        for sheepy in self.sheep:
            if self.dist_to_entity(sheepy) < 5:
                return True
        return False
    
    # End the mission after traveling to mission frontier within the pen 
    # (40th column of blocks east of arena's center block and inside of Pen borders)
    def end_mission(self):
        x,z = self.location
        return 39 < x < 50 and -10 < z < 10

    # Put agent on path towards the pen
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
    
    # Return actions available at a given state
    def get_possible_actions(self):
        # Check if actions are allowable or not recommended 
        # (e.g. drawing wheat when no sheep are near, walking to the pen without wheat drawn)
        if self.sheep_are_near():
            return [act for _id, act in self.possible_actions.items()]
        else:
            return [act for _id, act in self.possible_actions.items() if act != "hotbar.2 1"]

    def choose_action(self,state,possible_actions):
        curr_state = self.get_q_state()
        if curr_state not in self.q_table:
            self.q_table[curr_state] = {}
        for action in possible_actions:
            if action not in self.q_table[curr_state]:
                self.q_table[curr_state][action] = 0

        action = ""
        if random.random() < self.epsilon: 
            action = possible_actions[random.randint(0, len(possible_actions)-1)]
        else: 
            temp_r_map = self.q_table[self.get_q_state()]
            actions_by_reward = defaultdict(list)
            sorted_acts = []
            for key, val in temp_r_map.items():
                actions_by_reward[val].append(key)
            for reward, acts_list in actions_by_reward.items():
                sorted_acts.append((reward, acts_list))
            sorted_acts.sort(key=lambda tup: tup[0], reverse=True)
            action = random.choice(sorted_acts[0][1])
        return action    
    
    def act(self, agent_host, action):
        if self.end_mission():
            agent_host.sendCommand('quit')
            curr_state = self.get_q_state()
            return self.state_to_reward(curr_state)
        else:
            agent_host.sendCommand(action)
            return 0

    def run(self, agent_host):
        # self.get_current_state(agent_host)
        # action = self.choose_action(self.epsilon)
        # self.act(agent_host, action)
        S, A, R = deque(), deque(), deque()
        present_reward = 0
        done_update = False
        while not done_update:
            self.get_current_state(agent_host)
            s0 = self.get_q_state()
            possible_actions = self.get_possible_actions()
            a0 = self.choose_action(s0, possible_actions)
            S.append(s0)
            A.append(a0)
            R.append(0)

            T = sys.maxsize
            for t in range(sys.maxsize):
                time.sleep(0.1)
                if t < T:
                    current_r = self.act(agent_host, A[-1])
                    R.append(current_r)

                    if self.end_mission():
                        # Terminating state
                        T = t + 1
                        S.append('Term State')
                        present_reward = current_r
                        print("Reward:", present_reward)
                    else:
                        s = self.get_q_state()
                        S.append(s)
                        possible_actions = self.get_possible_actions()
                        next_a = self.choose_action(s, possible_actions)
                        A.append(next_a)

                tau = t - self.n + 1
                if tau >= 0:
                    self.update_q_table(tau, S, A, R, T)

                if tau == T - 1:
                    while len(S) > 1:
                        tau = tau + 1
                        self.update_q_table(tau, S, A, R, T)
                    done_update = True
                    break
    
    