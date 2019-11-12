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
    runs = 1
    for i in range(runs):
        mission_XML = farm.getMissionXML("Sheep Apocalypse #" + str(i+1))
        my_mission = MalmoPython.MissionSpec(mission_XML, True)
        my_mission_record = MalmoPython.MissionRecordSpec()

        # Attempt to start a mission:
        max_retries = 3
        for retry in range(max_retries):
            try:
                agent_host.startMission( my_mission, my_mission_record )
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:",e)
                    exit(1)
                else:
                    time.sleep(2)

        # Loop until mission starts:
        print("Starting mission " + str(i+1))
        world_state = agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:",error.text)
        
        while world_state.is_mission_running:
            shepherd.run(agent_host)
            time.sleep(0.1)
            world_state = agent_host.getWorldState()
        
        shepherd.get_current_state(agent_host)
        print()
        print("Shepherd location:", shepherd.agent_location())
        print("Sheep locations:", shepherd.sheep_location())
        print("Shepherd in pen:", shepherd.end_mission())
        print("Sheep in pen:", shepherd.sheep_in_pen())

        print()
        print("End of mission")
        print()
        time.sleep(1)
        # Mission has ended.
        
    print("Completed all runs.")
