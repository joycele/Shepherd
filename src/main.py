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

import create_world as world
from shepherd_agent import Shepherd
from farm_world import Farm

import functools
print = functools.partial(print, flush=True)



def get_logistics():
    pass
    
if __name__ == "__main__":
    
    agent_host = MalmoPython.AgentHost()
    farm = Farm()
    shepherd = Shepherd(farm.world.size)
    sample_batch_size = 40
    runs = 15000
    
    for i in range(runs):
        time.sleep(0.1)
        farm.initialize()
        mission_XML = world.getMissionXML("Sheep Apocalypse #" + str(i+1))
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
        agent_host.sendCommand("hotbar.1 1")
        agent_host.sendCommand("hotbar.1 0")
        state = farm.get_flattened_state()
        while world_state.is_mission_running:
            time.sleep(0.1)
            if farm.end_mission:
                agent_host.sendCommand('quit')
                get_logistics()
                break
            shepherd.run(farm, agent_host)
            world_state = agent_host.getWorldState()
        print()
        print("Mission " + str(i+1) + " Sheep in pen: " + str(farm.sheep_in_pen()) 
              + " actions taken: " + str(shepherd.number_actions_taken) + 
              " calculations made: " + str(farm.number_calculations) + " total reward: " + str(farm.total_reward) 
              + " avg reward: " + str(farm.total_reward / farm.number_calculations))
        time.sleep(1)
    
    print("Completed all runs.")
                