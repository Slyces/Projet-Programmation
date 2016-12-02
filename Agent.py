# =============================================================================
'''
Quick description of the file
'''
# =============================================================================
__author__ = 'Simon Lassourreuille'
__version__ = ''
__date__ = '24/11/2016'
__email__ = 'simon.lassourreuille@etu.u-bordeaux.fr'
__status__ = 'Prototype'
# =============================================================================
from copy import deepcopy
verbose = 0

class Var(object):
    def __init__(self, name: str, init_value: int=0, time_step: int=0):
        self.__name = name
        self.__value = init_value
        self.__time_step = time_step

    @property
    def time_step(self):
        return self.__time_step

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def name(self):
        return self.__name

class Status(object):
    def __init__(self, test_var: str, comp: str='', threshold: int=0, target_state: str=''):
        self.__t_var = test_var
        self.__comparison = comp
        self.__threshold = threshold
        self.__target_state = target_state

    def test(self, agent):
        if self.__comparison == '>':
            if agent.vars[self.__t_var].value > self.__threshold :
                if verbose >= 1 :
                    print('    State : {} ; Var : {} = {} -> {}'.format(agent.state, self.__t_var,
                                                                        agent.vars[self.__t_var].value,
                                                                        self.__target_state if agent.vars[
                                                                                                  self.__t_var].value > self.__threshold else agent.state))
                return self.__target_state
        elif self.__comparison == '<':
            if agent.vars[self.__t_var].value < self.__threshold:
                if verbose >= 1 :
                    print('    State : {} ; Var : {} = {} -> {}'.format(agent.state, self.__t_var,
                                                                        agent.vars[self.__t_var].value,
                                                                        self.__target_state if agent.vars[
                                                                                                   self.__t_var].value < self.__threshold else agent.state))
                return self.__target_state
        else : # if comparison is '', the first parameter is the target state
            if verbose >= 2 :
                print('    State : {} ; -> {}'.format(agent.state, self.__t_var))
            return self.__t_var
        return False

class State(object):
    def __init__(self, name, color, vars={}, status=[],fields={},sensors={}):
        self.color = color
        self.name = name
        self.vars = vars
        self.status = status
        self.fields = fields
        self.sensors = sensors

class Field(object):
    def __init__(self, variable, reduction):
        self.__var = variable
        self.__reduction = reduction

    @property
    def var(self):
        return self.__var

    def value(self, var: int, distance: int=0):
        if distance == 0:
            return var - 1
        return max(0, var + self.__reduction * distance)

class Sensor(object):
    def __init__(self, target_var, source_field, scale):
        self.target_var = target_var
        self.source_field = source_field
        self.scale = scale

class Agent(object):

    states = {}
    def __init__(self, state, *position):
        if len(position) == 1:
            position = position[0]
        self.x,self.y = position

        # Init of attributes
        self.state = state
    # =========================================================================
    # Static methods
    @staticmethod
    def set_states(*states):
        for state in states :
            Agent.states[state.name] = state

    # =========================================================================
    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, string: str):
        self.set_state(string)

    @property
    def pos(self):
        return self.x,self.y

    def set_state(self, string: str):
        assert string in Agent.states.keys()
        assert string in Agent.states.keys()
        self.__state = string
        state = deepcopy(Agent.states[string])
        self.color = state.color
        self.vars = state.vars
        self.status = state.status
        self.fields = state.fields
        self.sensors = state.sensors

    def test(self, status: 'Status'):
        return status.test(self)

    def test_status(self):
        if verbose >= 2 :
            print("Agent at position {} {} :\nStarting status test from state = {}".format(self.x,self.y,self.state))

        new_status = self.state
        for status in self.status:
            state = self.test(status)
            if verbose > 0 :
                print('     test says : ',state)
            if state :
                new_status = state
        self.state = new_status
        if verbose >= 2 :
            print("Status test finished : new state = {}".format(self.state))

    def sense(self, field_name, value):
        for key in self.sensors.keys():
            if key == field_name:
                if verbose >= 2 :
                    print("Agent at position {} {} :\n  Sensing with key={} & value={}".format(self.x,self.y,key, value))

                before = self.vars[self.sensors[key].target_var].value
                self.vars[self.sensors[key].target_var].value = value * self.sensors[key].scale
                if verbose >= 2 :
                    print("    -> ancien active = {} -> new active = {}".format(before, self.vars[
                        self.sensors[key].target_var].value))


    def move(self, *new_pos):
        if len(new_pos) == 1:
            new_pos = new_pos[0]
        self.x,self.y = new_pos

    def emmit(self, field: str, dist: int):
        field = self.fields[field]
        return field.value(self.vars[field.var].value, dist)

    def get_close(self):
        x,y = self.pos
        return ()

    def __repr__(self):
        return 'Agent'
        reprs = {'#FF0':'○',
                 '#00F':'■',
                 '#F00':'◘'}
        return reprs[self.color]


def AgentFactory(states=[]):
    new_Agent = Agent
    new_Agent.set_states(*states)
    return new_Agent

def create_state(parsed_state)->'State':
    # Mineral tree #0F0
    name,color = parsed_state[0][1:]
    vars, status, fields, sensors = {}, [], {}, {}
    for line in parsed_state[1:]:
        # Creating vars
        if line[0] == "var":
            # var name init_val=0 time_step=0
            vars[line[1]] = Var(*line[1:])
        # Creating status
        if line[0] == 'status':
            status.append(Status(*line[1:]))
        # Creating sensors
        if line[0] == 'sensor':
            # sensor target_var field_emitting scale
            sensors[line[2]] = Sensor(*line[1:])
        # Creating fields
        if line[0] == 'field':
            # field variable reduction
            fields[line[1]] = Field(*line[1:])
    return State(name, color, vars, status, fields, sensors)

def create_Agent(Agent_creator, parsed_agents):
    # Seekinf (a:b) to extend the lines
    new_agents = []
    for line in parsed_agents: # agent agent_state (x0,y0) (x1,y1) ...
        for i in range(len(line[2:])):
            if type(line[i+2]) == str : # (a:b,c) (a,b:c) (a:b,c:d)
                first,second = line[i+2][1:-1].split(',')
                if ':' in first :
                    a,b = first.split(':')
                    a,b = int(a),int(b)
                    first = [a + i for i in range(b-a+1)]
                else :
                    first = [int(first)]
                if ':' in second :
                    a,b = second.split(':')
                    a,b = int(a),int(b)
                    second = [a + i for i in range(b-a+1)]
                else :
                    second = [int(second)]
                for i in range(len(first)):
                    for j in range(len(second)):
                        new_agents.append(Agent_creator(line[1],first[i],second[j]))
            else :
                new_agents.append(Agent_creator(line[1],*line[i+2]))
    return new_agents


if __name__ == '__main__':
    print(Agent())
