# shepherd_agent.py

# Shepherd class used to keep track of the agent
#   class methods:
#     - get_current_state
#     - agent_location
#     - sheep_location
#     - sheep_in_pen
#     - agent_in_pen
#     - update_q_table
#     - choose_action
#     - act (do an action)
#     - run (run the agent)

import random, json

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
    
    def agent_in_pen(self):
        x,z = self.location
        return 30 < x < 50 and -10 < z < 10
    
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
    
    def choose_action(self, curr_state, eps):
        # return a random move for now
        a = random.randint(0, 5)
        return self.possible_actions[a]
    
    def act(self, agent_host, action):
        if self.agent_in_pen():
            agent_host.sendCommand('quit')
        else:
            agent_host.sendCommand(action)
    
    def run(self, agent_host):
        # run with random move, need to implement q-learning
        state = self.get_current_state(agent_host)
        action = self.choose_action(state, self.epsilon)
        print(action + ",", end = " ")
        self.act(agent_host, action)
    