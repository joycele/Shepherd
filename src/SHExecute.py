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

from SHEnvObserver import WorldObserver
from tensorflow.keras import models

import functools
print = functools.partial(print, flush=True)


NUM_OF_EPISODE = 100
MAX_RETRIES = 3
BATCH_SIZE = 32
ACTION_MAP = {
    0: "move 0.25",
    1: "move -0.25",
    2: "strafe -0.25",
    3: "strafe 0.25",
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
    if not os.path.exists("./model-saved"):
        print("Fail to create model checkpoint directory")
        sys.exit()
    agent_host = MalmoPython.AgentHost()
    observer = WorldObserver()

    # Load neuralnetwork model fomr directory
    agent_net = models.load_model("./model-saved/999.h5")

    print("Successfully load saved model!")

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

            action = np.argmax(agent_net.predict(state))
            executeAction(agent_host, action)
            # Get world state
            state, reward, done, info = observer.getEnvState(world_state)
            if done:
                agent_host.sendCommand('quit')
                break;

            for error in world_state.errors:
                print("Error:",error.text)

        print()
        print("Mission ended")