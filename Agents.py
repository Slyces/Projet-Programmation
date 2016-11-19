# =============================================================================
'''
This file codes every type of agents and how they interact with each-other
'''
# =============================================================================
__author__ = 'Simon Lassourreuille'
__version__ = ''
__date__ = '02/11/2016'
__email__ = 'simon.lassourreuille@etu.u-bordeaux.fr'
__status__ = 'Prototype'
# =============================================================================
# Imports
# from random import random, randint as rdi
import Status
from Field import Field


# =============================================================================
class Agent(object):
    """
    An Agent is an entity interacting with the world.
    """
    # Counter of instances of Agents
    __id = 0

    def __init__(self, pos, type: str, status={}, field=Field(1, 5),
                 sensors: dict={}):
        """
        :param pos: starting position
        :param status: a dict of status { StatusName : status, ... }
                see status
        :param sensors: A dict structured like :
                { AgentType : value, AgentType : value, ... }
        """
        # Id of agent to differenciate them easily
        self.id = Agent.__id
        Agent.__id += 1

        # Basic attributes
        self.type = type
        self.field = field
        self.sensors = sensors
        self.status = status
        self.__color = '#000000'

        # Death status for every type of Agent
        self.status['Death'] = Status.Death()
        for status in self.status.keys():
            self.status[status].start()  # Starting status

        # Position of the Agent
        self.pos = pos

    def set_field(self, field):
        """ Function to modify field in a status """
        self.field = field

    def set_sensor(self,type: str, value: int):
        """ Function to modify sensor in a status """
        self.sensors[type] = value

    def sense(self, fields, x, y):
        """ Returns the perception of an agent for a cell of coords (x,y) """
        value = 0  # The value is set to 0 by default
        for type in self.sensors.keys():  # Parsing every type available
            value += self.sensors[type]*fields[type][x][y]
            #  Multiply each sensor by the value of the corresponding field
            #  at the cell (x,y), and adds this to the value
        return value

    def age(self):
        """ Makes the Agent 'older' by using each status' time function """
        for status in self.status.values():
           status.time()

    def get_color(self):
        """ Return the Agent's color """
        return self.__color

    def set_color(self, color):
        """ Sets the Agent's color """
        self.__color = color

    def __getitem__(self, string: str):
        return self.status[string]

    def __setitem__(self, key, value):
        self.status[key] = value

    def __bool__(self):
        return bool(self['Death'])

    def death(self):
        self['Death'](1)

# =============================================================================
class Proie(Agent):
    def __init__(self, pos):
        Agent.__init__(self, pos, 'Proie',
                       field= Field(20,10,0,reduction='High'),
                       sensors={'Proie':1,'Predateur':-100, 'Vegetal':0})

    def get_color(self):
        return 'black'

class Predateur(Agent):
    def __init__(self, pos):
        Agent.__init__(self, pos, 'Predateur',
                       field=Field(20, 6, reduction='None'),
                       status={'Hunger':Status.Hunger(self, 'Proie'),'Age':Status.Age(self)},
                       sensors={'Proie': 400, 'Predateur': 0, 'Vegetal':0})
        self.colored = 'red'

    def get_color(self):
        return self.colored

class Vegetal(Agent):
    def __init__(self, pos):
        Agent.__init__(self, pos, 'Vegetal',
                       field=Field(1,5,0,'High'),
                       sensors={'Proie':0, 'Predateur':0, 'Vegetal':1})

    def get_color(self):
        return 'green'