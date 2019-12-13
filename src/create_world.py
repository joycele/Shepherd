# create_world.py

# Spawn sheep in random locations on a farm
# (later) spawn lava blocks in random locations

import random

# Draw the flowing lava blocks randomly in the arena
def getLavaBlocks():
    xml=""
    number_of_blocks = 10
    for item in range(number_of_blocks):
        x = str(random.randint(20, 50))
        z = str(random.randint(1, 30))
        xml += '''<DrawBlock x="''' + x + '''" y="207" z="''' + z + '''" type="flowing_lava"/>'''
    return xml


# Draw the Sheep spawner blocks randomly in the arena
def getSpawnerBlocks():
    xml=""
    number_of_sheep = 4
    for item in range(number_of_sheep):
        x = str(random.randint(20, 50))
        z = str(random.randint(1, 30))
        xml += '''<DrawEntity x="''' + x + '''" y="207" z="''' + z + '''" type="Sheep"/>'''
    return xml


def getMissionXML(summary):
    return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>''' + summary + '''</Summary>
        </About>
        <ServerSection>
            <ServerInitialConditions>
                <Time>
                    <StartTime>1000</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                </Time>
                <Weather>clear</Weather>
                <AllowSpawning>true</AllowSpawning>
                <AllowedMobs>Sheep</AllowedMobs>
            </ServerInitialConditions>
            <ServerHandlers>
                <FlatWorldGenerator generatorString="3;7,2*3,2;1;" />
                <DrawingDecorator>
                    <!-- Draw 30x50 Boundary World-->
                    <DrawCuboid x1="51" y1="206" z1="30" x2="14" y2="226" z2="0" type="grass"/>
                    <DrawCuboid x1="50" y1="207" z1="29" x2="15" y2="226" z2="1" type="air"/>
                    
                    <!-- Clear surrounding area outside of Boundary free of objects -->
                    <DrawCuboid x1="15" y1="205" z1="51" x2="-70" y2="226" z2="30" type="air"/>
                    <DrawCuboid x1="70" y1="205" z1="80" x2="15" y2="226" z2="32" type="air"/>
                    <DrawCuboid x1="100" y1="205" z1="70" x2="52" y2="226" z2="-70" type="air"/>
                 
                    <!-- Draw 30x15 Herding Pen (Shepherd must go here to finish mission) -->
                    <DrawCuboid x1="15" y1="205" z1="31" x2="-70" y2="226" z2="-1" type="air"/>
                    <DrawCuboid x1="15" y1="205" z1="31" x2="0" y2="205" z2="-1" type="grass"/>
                    <DrawLine x1="0" y1="206" z1="-1" x2="0" y2="206" z2="31" type="fence"/>
                    <DrawLine x1="0" y1="206" z1="-1" x2="15" y2="206" z2="-1" type="fence"/>
                    <DrawLine x1="15" y1="206" z1="-1" x2="15" y2="206" z2="31" type="fence"/>
                    <DrawLine x1="0" y1="206" z1="31" x2="15" y2="206" z2="31" type="fence"/>
                    
                    <!-- Put some cows, pigs, chickens in there because it's a farm and it's cute-->
                    <DrawEntity x="7" y="206" z="15" type="Cow"/>
                    <DrawEntity x="3" y="206" z="7" type="Pig"/>
                    <DrawEntity x="5" y="206" z="21" type="Chicken"/>
                    <DrawEntity x="10" y="206" z="26" type="Chicken"/>
                    <DrawEntity x="13" y="206" z="12" type="Pig"/>
                                        
                    <!-- Spawn random sheep and lava blocks -->
                    ''' + getSpawnerBlocks() + '''
                </DrawingDecorator>
                <!-- Commented to simplify testing -->
                <ServerQuitFromTimeUp timeLimitMs="20000"/>
                <ServerQuitWhenAnyAgentFinishes />
            </ServerHandlers>
        </ServerSection>
        <AgentSection mode="Survival">
            <Name>Jesus</Name>
            <AgentStart>
                <Placement x="32" y="207.0" z="15" pitch="30" yaw="0"/>
                <Inventory>
                    <InventoryItem slot="1" type="wheat"/>
                </Inventory>
            </AgentStart>
            <AgentHandlers>
                <ChatCommands/>
                <DiscreteMovementCommands/>
                <AbsoluteMovementCommands/>
                <ContinuousMovementCommands turnSpeedDegs="480"/>
                <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="35" yrange="2" zrange="30" />
                </ObservationFromNearbyEntities>
                <InventoryCommands/>
                <MissionQuitCommands/>
                <ObservationFromFullStats/>
                <ObservationFromHotBar/>
                <AgentQuitFromReachingPosition>
                    <Marker x="3" y="207.7" z="0" tolerance="2" description="Goal_found"/>
                </AgentQuitFromReachingPosition>
            </AgentHandlers>
        </AgentSection>
    </Mission>'''
