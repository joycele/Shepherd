# create_world.py

# Spawn sheep in random locations on a farm
# (later) spawn lava blocks in random locations

import random

# Draw the flowing lava blocks randomly in the arena
def getLavaBlocks():
    xml=""
    number_of_blocks = 10
    for item in range(number_of_blocks):
        x = str(random.randint(-60 / 2, 60 / 2))
        z = str(random.randint(-60 / 2, 60 / 2))
        xml += '''<DrawBlock x="''' + x + '''" y="207" z="''' + z + '''" type="flowing_lava"/>'''
    return xml


# Draw the Sheep spawner blocks randomly in the arena
def getSpawnerBlocks():
    xml=""
    number_of_sheep = 2
    for item in range(number_of_sheep):
        x = str(random.randint(-60 / 2, 60 / 2))
        z = str(random.randint(-60 / 2, 60 / 2))
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
                    <!-- Draw 60x60 Boundary World-->
                    <DrawCuboid x1="-31" y1="206" z1="-31" x2="31" y2="226" z2="31" type="grass"/>
                    <DrawCuboid x1="-30" y1="207" z1="-30" x2="30" y2="226" z2="30" type="air"/>
                    
                    <!-- Draw Herding Pen (Shepherd must go here to finish mission) -->
                    <DrawCuboid x1="30" y1="205" z1="10" x2="50" y2="217" z2="-10" type="air"/>
                    <DrawCuboid x1="30" y1="205" z1="10" x2="50" y2="205" z2="-10" type="grass"/>
                    <DrawLine x1="30" y1="206" z1="10" x2="30" y2="206" z2="-10" type="fence"/>
                    <DrawLine x1="50" y1="206" z1="10" x2="50" y2="206" z2="-10" type="fence"/>
                    <DrawLine x1="50" y1="206" z1="10" x2="30" y2="206" z2="10" type="fence"/>
                    <DrawLine x1="30" y1="206" z1="-10" x2="50" y2="206" z2="-10" type="fence"/>
                    <!-- Put some cows, pigs, chickens in there because it's a farm and it's cute-->
                    <DrawEntity x="37" y="206" z="0" type="Cow"/>
                    <DrawEntity x="42" y="206" z="-5" type="Pig"/>
                    <DrawEntity x="33" y="206" z="-3" type="Chicken"/>
                    <DrawEntity x="45" y="206" z="3" type="Chicken"/>
                    <DrawEntity x="35" y="206" z="5" type="Pig"/>
                                        
                    <!-- Spawn random sheep and lava blocks -->
                    ''' + getSpawnerBlocks() + '''
                </DrawingDecorator>
                <ServerQuitFromTimeUp timeLimitMs="30000"/>
                <ServerQuitWhenAnyAgentFinishes />
            </ServerHandlers>
        </ServerSection>
        <AgentSection mode="Survival">
            <Name>Jesus</Name>
            <AgentStart>
                <Placement x="0.5" y="207.0" z="0.5" pitch="30" yaw="0"/>
                <Inventory>
                    <InventoryItem slot="1" type="wheat"/>
                </Inventory>
            </AgentStart>
            <AgentHandlers>
                <ChatCommands/>
                <ContinuousMovementCommands turnSpeedDegs="480"/>
                <AbsoluteMovementCommands/>
                <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="60" yrange="2" zrange="60" />
                </ObservationFromNearbyEntities>
                <InventoryCommands/>
                <AgentQuitFromTouchingBlockType>
                    <Block type="diamond_block" />
                </AgentQuitFromTouchingBlockType>
                <ObservationFromFullStats/>
            </AgentHandlers>
        </AgentSection>
    </Mission>
    '''