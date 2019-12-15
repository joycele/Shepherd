import os, sys, time, json
import math, errno
try:
    import MalmoPython
    import malmoutils
except:
    import malmo.MalmoPython as MalmoPython
    import malmo.malmoutils as malmoutils

import SHBuildWorld as worldbuilder
import numpy as np

from SHAgent import SHAgent
from SHEnvObserver import WorldObserver

import functools
print = functools.partial(print, flush=True)



NUM_OF_EPISODE = 100
MAX_RETRIES = 3
BATCH_SIZE = 32
ACTION_MAP = {
    0: "move 1",
    1: "move -1",
    2: "strafe -1",
    3: "strafe 1",
    4: "hotbar.1 1",
    5: "hotbar.2 1"
}

def executeAction(agent_host, action):
    agent_host.sendCommand(ACTION_MAP[action])
    if action < 4:
        return
    else:
        if action == 4:
            agent_host.sendCommand("hotbar.1 0")
        if action == 5:
            agent_host.sendCommand("hotbar.2 0")

if __name__ == "__main__":
    agent_host = MalmoPython.AgentHost()
    observer = WorldObserver()
    dqn = SHAgent(observer.state.size, len(ACTION_MAP))
    for episode in range(NUM_OF_EPISODE):

        # generate mission xml
        mission_xml = worldbuilder.genMissionXML("Episode #{}".format(episode))
        my_mission = MalmoPython.MissionSpec(mission_xml, True)
        my_mission_record = MalmoPython.MissionRecordSpec()

        for retry in range(MAX_RETRIES):
            try:
                agent_host.startMission(my_mission, my_mission_record)
                break;
            except RuntimeError as e:
                if retry == MAX_RETRIES - 1:
                    print("Error starting mission:",e)
                    exit(1)
                else:
                    time.sleep(2)

        world_state = agent_host.getWorldState()

        # Loop until mission starts:
        print("Waiting for the mission to start ", end=' ')
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            print(".", end="")
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:",error.text)
        print()
        print("Episode #{}".format(episode))

        state, _, _, _ = observer.getEnvState(world_state)
        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()

            action = dqn.act(state)
            executeAction(agent_host, action)
            # Get world state
            next_state, reward, done, info = observer.getEnvState(world_state)

            dqn.store(state, action, reward, next_state, done)
            state = next_state
            if done:
                dqn.synchronize_target_model()
                agent_host.sendCommand('quit')
                break;
            if len(dqn.replay) > BATCH_SIZE:
                dqn.train(BATCH_SIZE)

            for error in world_state.errors:
                print("Error:",error.text)

        print()
        print("Mission ended")
        if not os.path.exists("./model-saved"):
            try:
                os.mkdir("./model-saved")
            except:
                print("Fail to create model checkpoint directory")
        dqn.q_network.save("./model-saved/{}.h5".format(episode))
