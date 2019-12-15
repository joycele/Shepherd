import random

def genStageXML():
    xml = ""
    xml += '''<DrawCuboid x1="-1" y1="206" z1="-1" x2="31" y2="226" z2="31" type="grass"/>'''
    xml += '''<DrawCuboid x1="31" y1="205" z1="9" x2="45" y2="226" z2="23" type="grass"/>'''
    xml += '''<DrawCuboid x1="0" y1="207" z1="0" x2="30" y2="226" z2="30" type="air"/>'''
    xml += '''<DrawCuboid x1="31" y1="206" z1="9" x2="45" y2="226" z2="23" type="air"/>'''

    xml += '''<DrawLine x1="31" y1="206" z1="9" x2="31" y2="206" z2="23" type="fence"/>'''
    xml += '''<DrawLine x1="31" y1="206" z1="9" x2="45" y2="206" z2="9" type="fence"/>'''
    xml += '''<DrawLine x1="31" y1="206" z1="23" x2="45" y2="206" z2="23" type="fence"/>'''
    xml += '''<DrawLine x1="45" y1="206" z1="9" x2="45" y2="206" z2="23" type="fence"/>'''

    return xml


def genSheepXML(num=4):
    xml = ""
    for e in range(num):
        x = str(random.randint(1, 29))
        z = str(random.randint(1, 29))
        xml += '''<DrawEntity x="''' + x + '''" y="207" z="''' + z + '''" type="Sheep"/>'''
    return xml

def genDecXML():
    return genStageXML() + genSheepXML();

def genMissionXML(summary):
    return '''<?xml version="1.0" encoding="utf-8"?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>''' + summary + '''</Summary>
        </About>
        <ServerSection>
            <ServerInitialConditions>
                <Time>
                    <StartTime>10000</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                </Time>
                <Weather>clear</Weather>
                <AllowSpawning>true</AllowSpawning>
                <AllowedMobs>Sheep</AllowedMobs>
            </ServerInitialConditions>
            <ServerHandlers>
                <FlatWorldGenerator generatorString="3;7,3,2;1;"/>
                <DrawingDecorator>
                ''' + genDecXML() + '''
                </DrawingDecorator>
                <ServerQuitFromTimeUp timeLimitMs="30000"/>
                <ServerQuitWhenAnyAgentFinishes/>
            </ServerHandlers>
        </ServerSection>
        <AgentSection mode="Survival">
            <Name>Jesus</Name>
            <AgentStart>
                <Placement x="15" y="207" z="15" pitch="0" yaw="-90"/>
                <Inventory>
                    <InventoryItem slot="1" type="wheat"/>
                </Inventory>
            </AgentStart>
            <AgentHandlers>
                <ChatCommands/>
                <ContinuousMovementCommands turnSpeedDegs="360"/>
                <AbsoluteMovementCommands/>
                <DiscreteMovementCommands/>
                <ObservationFromNearbyEntities>
                    <Range name="entities" xrange="45" yrange="2" zrange="30" />
                </ObservationFromNearbyEntities>
                <InventoryCommands/>
                <MissionQuitCommands/>
                <ObservationFromFullStats/>
                <ObservationFromHotBar/>
                <AgentQuitFromReachingPosition>
                    <Marker x="44" y="206" z="15" tolerance="2" description="Goal_found"/>
                </AgentQuitFromReachingPosition>
            </AgentHandlers>
        </AgentSection>
    </Mission>'''