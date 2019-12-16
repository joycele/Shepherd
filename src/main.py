# main.py

# Main function to run malmo program

import os, sys, time
import math, errno

try:
    import MalmoPython
    import malmoutils
except:
    import malmo.MalmoPython as MalmoPython
    import malmo.malmoutils as malmoutils

import create_world as farm
from shepherd_agent import Shepherd

import functools
print = functools.partial(print, flush=True)



if __name__ == "__main__":
        
    # Create default Malmo objects:

    agent_host = MalmoPython.AgentHost()
    my_client_pool = MalmoPython.ClientPool()
    my_client_pool.add(MalmoPython.ClientInfo("127.0.0.1", 10000))

    try:
        agent_host.parse( sys.argv )
    except RuntimeError as e:
        print('ERROR:',e)
        print(agent_host.getUsage())
        exit(1)
    if agent_host.receivedArgument("help"):
        print(agent_host.getUsage())
        exit(0)

    shepherd = Shepherd()
    runs = 100
    for i in range(runs):
        mission_XML = farm.getMission2XML("Sheep Apocalypse #" + str(i+1))
        my_mission = MalmoPython.MissionSpec(mission_XML, True)
        my_mission_record = MalmoPython.MissionRecordSpec()

        # Attempt to start a mission:
        max_retries = 3
        for retry in range(max_retries):
            try:
                agent_host.startMission(my_mission, my_client_pool, my_mission_record, 0, "JESUS")
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:",e)
                    exit(1)
                else:
                    time.sleep(2)

        # Loop until mission starts:
        print("Mission", i)
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:",error.text)
        
        # Run shepherd agent until the mission is over
        shepherd.add_mission_stat_slot()
        while world_state.is_mission_running:
            time.sleep(0.1)
            shepherd.run(agent_host)
            world_state = agent_host.getWorldState()
        # shepherd.print_mission_steps()
        shepherd.get_current_observations(agent_host)
        # print(agent_host.getWorldState())
    print("Completed all runs.")
    print("Q-table after 100 runs")
    for state, actions in shepherd.q_table.items():
        print(state,":",actions,",\\")