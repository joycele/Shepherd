import random, json, sys, time
from collections import defaultdict, deque
from create_world import NUMBER_OF_SHEEP
from math import sqrt
import tkinter as tk

ARENA_WIDTH = 60
ARENA_BREADTH = 60
MOB_TYPE = "Sheep"

# Display parameters:
CANVAS_BORDER = 20
CANVAS_WIDTH = 400
CANVAS_HEIGHT = CANVAS_BORDER + ((CANVAS_WIDTH - CANVAS_BORDER) * ARENA_BREADTH / ARENA_WIDTH)
CANVAS_SCALEX = (CANVAS_WIDTH-CANVAS_BORDER)/ARENA_WIDTH
CANVAS_SCALEY = (CANVAS_HEIGHT-CANVAS_BORDER)/ARENA_BREADTH
root = tk.Tk()
canvas = tk.Canvas(root, width=(CANVAS_WIDTH+134), height=CANVAS_HEIGHT, borderwidth=0, highlightthickness=0, bg="black")
canvas.pack()
root.update()

# Function determining x position on TKinter canvas for x value based on distance from agent
def canvasX(x):
    return CANVAS_BORDER/2 + (0.5 + (x/float(ARENA_WIDTH))) * (CANVAS_WIDTH-CANVAS_BORDER)

# Function determining y position on TKinter canvas for y value based on distance from agent
def canvasY(y):
    return CANVAS_BORDER/2 + (0.5 + (y/float(ARENA_BREADTH))) * (CANVAS_HEIGHT-CANVAS_BORDER)

# Draw the sheep on TKinter
def drawMobs(entities):
    canvas.delete("all")
    canvas.create_rectangle(canvasX(-ARENA_WIDTH/2), canvasY(-ARENA_BREADTH/2), canvasX(ARENA_WIDTH/2), canvasY(ARENA_BREADTH/2), fill="#888888")
    canvas.create_rectangle(400,133,400+133,133+133,fill="#ffd200")
    for ent in entities:
        if ent["name"] == MOB_TYPE:
            canvas.create_oval(canvasX(ent["x"])-2, canvasY(ent["z"])-2, canvasX(ent["x"])+2, canvasY(ent["z"])+2, fill="#ff2244")
        else:
            canvas.create_oval(canvasX(ent["x"])-4, canvasY(ent["z"])-4, canvasX(ent["x"])+4, canvasY(ent["z"])+4, fill="#22ff44")
    root.update()

# shepherd_agent.py
# Shepherd class used to keep track of the agent
class Shepherd():
    #NOTE: Need penalty for death eventually
    rewards_ledger = {
        "sheep are near": NUMBER_OF_SHEEP*2,
        "per close sheep": 1,
        "no sheep near": -10,
        "all sheep herded": 500,
        "some sheep herded": 25,
        "no sheep herded": -100,
        "pen reached": 50,
        "x close to pen":10,
        "x far from pen":-75,
        "z OB":-75    
    }

    def __init__(self, alpha=0.3, gamma=1, n=1):
        """Constructing an RL agent.
        Args
            alpha:  <float>  learning rate      (default = 0.3)
            gamma:  <float>  value decay rate   (default = 1)
            n:      <int>    number of back steps to update (default = 1)
        """
        # q-learning variables
        self.epsilon = 0.18 # chance of taking a random action instead of the best
        self.q_table = { (0, 2, 0, 0) : {'pen': -7.5597899240816435, 'sheep_0': -7.6853831842439355, 'sheep_1': -8.603556212495494},\
            (0, 1, 0, 0) : {'sheep_0': -7.914284748856445, 'sheep_1': -6.021899688886062, 'pen': -8.172103098091144},\
            (0, 2, 1, 0) : {'sheep_1': -9.519268514588026, 'pen': -7.541436934529407, 'sheep_0': -19.190134333978285},\
            (1, 2, 1, 0) : {'sheep_1': -6.295540809121916, 'pen': -6.663798077391407, 'sheep_0': -7.706357104494696},\
            (0, 2, 2, 0) : {'pen': -6.7362059984981375},\
            (1, 2, 2, 0) : {'pen': -4.524126885537593},\
            (0, 1, 2, 0) : {'pen': -5.352840163953106},\
            (0, 1, 1, 0) : {'pen': -7.281680241135881, 'sheep_1': -7.214801337052651, 'sheep_0': -12.675326924362164},\
            (1, 2, 0, 0) : {'sheep_0': -4.639119372121955, 'sheep_1': -5.4904389518004555, 'pen': -6.236208769944893},\
            (1, 1, 1, 0) : {'pen': -6.661158896780346, 'sheep_1': -27.52720206067534},\
            (0, 0, 2, 0) : {'pen': -0.6088616588383906},\
            (0, 0, 0, 1) : {'sheep_1': 0.2316381891188879, 'pen': -1.363710915727579, 'sheep_0': -0.8645627717216375},\
            (1, 0, 0, 1) : {'sheep_0': 0.0, 'sheep_1': 0.0, 'pen': 0.0},\
            (0, 0, 2, 1) : {'pen': -1.1182323155309408},\
            (0, 0, 2, 2) : {'pen': -0.7403421624034879},\
            (0, 0, 1, 2) : {'pen': -0.037150730105799404, 'sheep_0': 0.0},\
            (0, 0, 0, 2) : {'sheep_1': -2.11923348338677, 'pen': -2.5176048617260456, 'sheep_0': -1.8733079246752578},\
            (1, 1, 0, 0) : {'pen': -4.923332580332339, 'sheep_0': -4.822257952068439, 'sheep_1': -4.119083715535733},\
            (0, 0, 0, 0) : {'sheep_1': -1.5746178358919596, 'pen': 0.5070032587347629, 'sheep_0': -1.9959794287289259},\
            (0, 0, 1, 0) : {'sheep_1': -0.5839450798493717, 'pen': -0.9056753115917838},\
            (0, 0, 1, 1) : {'sheep_1': -0.4312747536347856, 'pen': -1.9179809031739592},\
            (1, 0, 1, 1) : {'sheep_1': 0.0, 'pen': 0.0}, \
            (1, 0, 0, 0) : {'sheep_0': -0.3891005272029484, 'sheep_1': -0.19354045524592256, 'pen': -0.015750324608946445},\
            (1, 1, 2, 0) : {'pen': -3.021376079772385},\
            (1, 0, 0, 2) : {'pen': 0.0},\
            (1, 0, 2, 2) : {'pen': -0.2580997354040565} }
        self.n, self.alpha, self.gamma = n, alpha, gamma
        
        # world and agent variables
        self.prev_location = (0, 0)
        self.location = (0.5, 0.5)
        self.sheep = []
        self.number_of_movements = []
        self.possible_actions = {0: "move 1", 1: "move -1", 2: "strafe 1", 3: "strafe -1"}

    def add_mission_stat_slot(self):
        self.number_of_movements.append(0)

    def print_mission_steps(self):
        print(self.number_of_movements[-1])
    '''     STATE OBSERVATION METHODS       
                State definition
            [
                Vertical Distance from pen:[0,1,2] (inside, close, far),
                Horizontal Distance from pen: [0, 1, 2] (inside, leftbound, rightbound)
                Sheep nearby: [0,1,2] (no, some, yes),
                (term state) Sheep herded:[0,1,2] (no, some, yes)
            ]
    '''
    
    def state_to_reward(self, state):
        current_r = 0
        
        # Horizontal position
        if state[0] == 0 and state[1] == 0:
            current_r += self.rewards_ledger["pen reached"]
        else: # z OB
            current_r += self.rewards_ledger["z OB"]
        
        # Vertical position
        if state[1] == 1: # x close
              current_r += self.rewards_ledger["x close to pen"]
        elif state[1] == 2: # z far
              current_r += self.rewards_ledger["x far from pen"]

        # Sheep nearby
        if state[2] == 2:
            current_r += self.rewards_ledger["sheep are near"]
        elif state[2] == 1:
            current_r += self.rewards_ledger["per close sheep"]*self.number_of_sheep_near()
        else:
            current_r += self.rewards_ledger["no sheep near"]

        # If applicable, check how many sheep were saved
        if len(state) == 4:
            sheep_saved = state[3]
            if sheep_saved == 0:
                current_r += self.rewards_ledger["no sheep herded"]
            elif sheep_saved < NUMBER_OF_SHEEP:
                current_r += self.rewards_ledger["some sheep herded"]
            elif sheep_saved == NUMBER_OF_SHEEP:
                current_r += self.rewards_ledger["all sheep herded"]
        return current_r

    # Update class attributes based on observations from the environment as present instant
    def get_current_observations(self, agent_host):
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
                return ob

    def get_q_state(self):
        sheep_saved = self.sheep_in_pen()
        sheep_near = self.sheep_are_near(self.number_of_sheep_near())
        z = self.agents_relative_z_pos()
        x = self.agents_relative_x_pos()
        term_state = True

        if term_state:
            return tuple([z, x, sheep_near, sheep_saved])
        else:
            return tuple([z, x, sheep_near])
                
    '''     STATE OBSERVATION UTILITY METHODS       '''

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
        if count == 0:
            return 0
        elif count == NUMBER_OF_SHEEP:
            return 2
        else:
            return 1

    def number_of_sheep_near(self):
        close_sheep = 0
        for sheepy in self.sheep:
            if self.dist_to_entity(sheepy) < 5:
                close_sheep += 1
        return close_sheep

    def agents_relative_z_pos(self):
        x,z = self.location
        if -10 < z < 10:
            return 0
        else:
            return 1

    def agents_relative_x_pos(self):
        x,z = self.location
        if 29 < x < 50:
            return 0
        elif 1 < x < 29:
            return 1
        else:
            return 2

    # Find distance to entity from Agent
    def dist_to_entity(self, ent):
        sheep_x, sheep_z = ent
        christ_x, christ_z = self.location
        return sqrt(pow(sheep_x - christ_x, 2) + pow(sheep_z - christ_z, 2))

    # Find distance to mission termination from Agent
    def dist_to_mission_end(self):
        x,z = self.location
        if x < 0:
            x*=-1
            return x + 39
        else:
            return 39 - x

    # If there are any sheep in the arena that are within a Euclidean distance of 5 blocks, return value for state definitions
    def sheep_are_near(self, close_sheep):
        if close_sheep == 0:
            return 0
        elif close_sheep == NUMBER_OF_SHEEP:
            return 2
        else:
            return 1
    
    # End the mission after traveling to mission frontier within the pen 
    # (40th column of blocks east of arena's center block and inside of Pen borders)
    def end_mission(self, world_state):
        x,z = self.location
        return (39 < x < 50 and -10 < z < 10) or not world_state.is_mission_running
    
    def euclid_dist(self, a_x, a_z, b_x, b_z):
        return sqrt(pow(b_x - a_x, 2) + pow(b_z - a_z, 2))

    '''     HIGH LEVEL AGENT COMMANDS       '''

    def head_to_pen(self):
        movement = ""
        x,z = self.location
        if -10 < z < 10:
            movement = self.possible_actions[1]
        elif z < -10:
            movement = self.possible_actions[3]
        elif z > 10:
            movement = self.possible_actions[2]
        return movement

    def head_to_sheep(self, sheep_coord):
        movement = ""
        x,z = self.location
        sheep_x, sheep_z = sheep_coord
        #NOTE: Will break if possible_actions attribute is altered 
        move_results = [  
            self.euclid_dist(x-1, z, sheep_x, sheep_z), \
            self.euclid_dist(x+1, z, sheep_x, sheep_z), \
            self.euclid_dist(x, z-1, sheep_x, sheep_z), \
            self.euclid_dist(x, z+1, sheep_x, sheep_z)]
        return self.possible_actions[move_results.index(min(move_results))]


    '''     AGENT DELIBERATION      '''

    def best_policy(self, agent_host):
        current_r = 0
        ob = self.get_current_observations(agent_host)
        while not self.end_mission(agent_host.getWorldState()):
            if ob is not None and "entities" in ob:
                entities = ob["entities"]
                drawMobs(entities)
            s = self.get_q_state()
            possible_actions = self.get_possible_actions()
            next_a = self.choose_action(s, possible_actions, self.epsilon)
            current_r = self.act(agent_host, next_a)
        print(self.get_q_state())
        print("Reward:", current_r)
        return current_r == 554

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
        actions = []
        x,z = self.location
        for i in range(len(self.sheep)):
            sheep_x, sheep_z = self.sheep[i]
            if self.euclid_dist(x,z,sheep_x,sheep_z) > 6:
                actions.append("sheep_"+str(i))
        actions.append("pen")
        return actions

    def choose_action(self, state, possible_actions, eps):
        curr_state = self.get_q_state()
        if curr_state not in self.q_table:
            self.q_table[curr_state] = {}
        for action in possible_actions:
            if action not in self.q_table[curr_state]:
                self.q_table[curr_state][action] = 0
        
        action = ""
        if random.random() < eps: 
            action = random.choice(possible_actions)
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
        # Metric
        self.number_of_movements[-1] += 1
        if self.end_mission(agent_host.getWorldState()):
            curr_state = self.get_q_state()
            agent_host.sendCommand("quit")
            return self.state_to_reward(curr_state)
        else:
            x,z = self.location
            curr_state = self.get_q_state()
            if x%0.5 != 0 or z%0.5 != 0:
                command = "tp " + str(int(x) + 1.5) + " 207 " + str(int(z) + 0.5)
                print(x,z,command)
                agent_host.sendCommand(command)
            if action == "pen":
                movement = self.head_to_pen()
                agent_host.sendCommand(movement)
            else:
                try:
                    sheep_number = int(action[-1])
                    if sheep_number > len(self.sheep):
                        sheep_number = len(self.sheep) - 1
                    sheep_coord = self.sheep[sheep_number]
                    movement = self.head_to_sheep(sheep_coord)
                    agent_host.sendCommand(movement)
                except:
                    print("Number of Sheep = ", len(self.sheep))
                    print(action)
            return 0

    def run(self, agent_host):
        S, A, R = deque(), deque(), deque()
        present_reward = 0
        done_update = False
        while not done_update:
            s0 = self.get_q_state()
            possible_actions = self.get_possible_actions()
            a0 = self.choose_action(s0, possible_actions,self.epsilon)
            S.append(s0)
            A.append(a0)
            R.append(0)

            T = sys.maxsize
            for t in range(sys.maxsize):
                time.sleep(0.1)
                world_state = agent_host.getWorldState()
                ob = self.get_current_observations(agent_host)
                if t < T:
                    current_r = self.act(agent_host, A[-1])
                    R.append(current_r)
                    if ob is not None and "entities" in ob:
                        entities = ob["entities"]
                        drawMobs(entities)
                    if self.end_mission(world_state):
                        T = t + 1
                        present_reward = current_r
                        print("Reward", present_reward)
                    else:
                        s = self.get_q_state()
                        S.append(s)
                        possible_actions = self.get_possible_actions()
                        next_a = self.choose_action(s, possible_actions, self.epsilon)
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