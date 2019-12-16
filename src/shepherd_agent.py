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
# root = tk.Tk()
# canvas = tk.Canvas(root, width=(CANVAS_WIDTH+134), height=CANVAS_HEIGHT, borderwidth=0, highlightthickness=0, bg="black")
# canvas.pack()
# root.update()

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
    rewards_ledger = {
        "sheep are near": NUMBER_OF_SHEEP*2,
        "per close sheep": 1,
        "no sheep near": -100,
        "all sheep herded": 500,
        "some sheep herded": 25,
        "no sheep herded": -100,
        "pen reached": 50,
        "x close to pen":10,
        "x far from pen":-75,
        "z OB":-75,
        "death":-200    
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
        self.q_table = { }
        self.n, self.alpha, self.gamma = n, alpha, gamma
        
        # world and agent variables
        self.prev_location = (0, 0)
        self.location = (7.5, -7.5)
        self.sheep = []
        self.number_of_movements = []
        self.possible_actions = {0: "move 1", 1: "move -1", 2: "strafe 1", 3: "strafe -1"}

    def add_mission_stat_slot(self):
        self.number_of_movements.append(0)

    def print_mission_steps(self):
        print(self.number_of_movements[-1])
    
    '''     STATE OBSERVATION METHODS       
            State definition  [ Vertical Distance from pen:[0,1,2,3,4] , Horizontal Distance from pen: [0,1,2,3,4] ]
    '''
    
    def state_to_reward(self, state):
        current_r = 0
        
        # Positional Eval
        if state[0] == 4 and state[1] == 4:
            current_r += self.rewards_ledger["pen reached"]
        else:
            # Horizontal position
            if state[1] != 1 or state[1] != 2: 
                current_r -= 10
            # Vertical position
            current_r -= pow(5, state[0])

        # Sheep stats
        sheep_near = self.number_of_sheep_near()
        sheep_prox = self.sheep_are_near(sheep_near)
        sheep_saved = self.sheep_in_pen()
        if sheep_prox == 2 or sheep_prox == 1:
            current_r += pow(7, sheep_prox+1)
        else:
            current_r += self.rewards_ledger["no sheep near"]

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
        z = self.agents_relative_z_pos()
        x = self.agents_relative_x_pos()
        return tuple([x, z])
                
    '''     STATE OBSERVATION UTILITY METHODS       '''

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
        # print("z:", z)
        if 15 < z <= 30:
            return 0
        elif 0 < z <= 15:
            return 1
        elif -15 < z <= 0:
            return 2
        elif -30 < z <= -15:
            return 3
        else:
            return 4

    def agents_relative_x_pos(self):
        x,z = self.location
        # print("x: ", x)
        if 15 < x <= 30:
            return 0
        elif 0 < x <= 15:
            return 1
        elif -15 < x <= 0:
            return 2
        elif -30 < x <= -15:
            return 3
        else:
            return 4

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

    def sign(self,a):
        if a > 0:
            return 1
        elif a < 0:
            return -1
        else:
            return 0

    '''     HIGH LEVEL AGENT COMMANDS       '''

    def head_to_pen(self):
        movements = []
        x,z = self.location
        while x < 40:
            movements.append(self.possible_actions[1])
            x += 1
        print(movements)
        return movements

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

    def head_to_Fcoord(self, dest_x, dest_z):
        new_x, new_z = self.get_Fcoord_midpoint(dest_x, dest_z)
        f_x, f_z = self.agents_relative_x_pos(), self.agents_relative_z_pos()
        x,z = self.location
        command_list = []
        move_com, strafe_com = "move " + str(dest_x - f_x), "strafe " + str(dest_z - f_z)
        print("head_to_Fcoord()",self.location,"-->", self.get_Fcoord_midpoint(dest_x, dest_z))
        while z != new_z:
            command_list.append(strafe_com)
            z+= self.sign(new_z-z)
            # print("z",str(z),"=",str(new_z), self.sign(new_z-z))
        while x != new_x:
            command_list.append(move_com)
            x+= self.sign(new_x-x)
            # print("x:",str(x),"=",str(new_x), self.sign(new_x-x))
        print()
        return command_list

    def get_Fcoord_midpoint(self, dest_x, dest_z):
        if dest_z == 0:
            z=22.5
        elif dest_z == 1:
            z=7.5
        elif dest_z == 2:
            z=-7.5
        elif dest_z == 3:
            z=-22.5

        if dest_x == 0:
            x=22.5
        elif dest_x == 1:
            x=7.5
        elif dest_x == 2:
            x=-7.5
        elif dest_x == 3:
            x=-22.5
        return x,z
            
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
        f_x, f_z = self.agents_relative_x_pos(), self.agents_relative_z_pos()
        if f_x != 0:
            actions.append((f_x - 1, f_z))
        if f_x != 3:
            actions.append((f_x + 1, f_z))
        if f_z != 0:
            actions.append((f_x, f_z - 1))
        if f_z != 3:
            actions.append((f_x, f_z + 1))
        if f_x == 0 and (f_z == 1 or f_z == 2):
            actions.append("pen")
        return actions

    def choose_action(self, state, possible_actions, eps):

        curr_state = self.get_q_state()
        f_x, f_z = self.agents_relative_x_pos(), self.agents_relative_z_pos()

        if curr_state not in self.q_table:
            self.q_table[curr_state] = {}
        for action in possible_actions:
            if action not in self.q_table[curr_state]:
                self.q_table[curr_state][action] = 0
        
        action = ""
        if random.random() < eps: 
            action = random.choice(possible_actions)
            print("[RANDOM eps] choose_action()", (f_x, f_z), "->", action )
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
            print("choose_action()", (f_x, f_z), "->", action )
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
                time.sleep(2)
            if action == "pen":
                movement = self.head_to_pen()
                agent_host.sendCommand(movement)
            else:
                new_x, new_z = action
                for move in self.head_to_Fcoord(new_x, new_z):
                    agent_host.sendCommand(move)
                    time.sleep(0.1)
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