# =============================================================================
'''
Quick description of the file
'''
# =============================================================================
__author__ = 'Simon Lassourreuille'
__version__ = '2.1'
__date__ = '05/12/2016'
__email__ = 'simon.lassourreuille@etu.u-bordeaux.fr'
__status__ = 'Prototype'
# =============================================================================
from Debugger import Debugger as D
from copy import deepcopy
from ezCLI import grid
from random import choice
from numpy import array

D.verbose = 0

# =============================================================================
class State(object):
    """ Main class defining what is the state of an Agent """

    def __init__(self, color, vars: dict, fields: dict,
                 status: list, sensors: dict, births: dict):
        """
        A state object does not do much except holding important informations
        to set up Agents
        :param name: Is the name of the state.
        :param vars: A dict of vars :
            { 'name' : [ init_value = 0, time_step_value = 0],
            'hunger' : [ 100, -5 ], 'age' : [ 0 , 1 ] }
        :param fields: A dict of fields :
            { 'name' : scaling,
              'blue' : -1, 'red' : -1 }
        :param status: list of status :
            [[ target state, statement ],
             [ 'END', ['life', '<', 0] ]]
        :param sensors: dict of sensors
            { 'hosting_var' : [['impacting_field', scale], ...],
              'comfort' : [['blue', +0.7], ['red', -0.3]] }
        :param births: dict of births
            {   'created_state' : statement,
                'photophobia' : [ 'seed', '<', 1 ] }
        """
        self.color = color
        self.vars = vars
        self.fields = fields
        self.status = status
        self.sensors = sensors
        self.births = births
# =============================================================================

class Agent(object):

    states = {'death':State("",{},{},[],{},{}),
              'end': State("", {}, {}, [], {}, {})}

    def __init__(self, state: str, *position):
        if len(position) == 1:
            position = position[0]
        self.x, self.y = position

        # Init of attributes
        self.__state = ''
        self.color = ''
        self.vars = {}
        self.status = []
        self.fields = {}
        self.sensors = {}
        self.births = {}
        self.state = state

    # =========================================================================
    # Static methods
    @staticmethod
    def add_state(name: str, state: 'State'):
        Agent.states[name] = state

    @staticmethod
    def dist(a, b):
        return max([abs(a[0] - b[0]), abs(a[1] - b[1])])

    # =========================================================================
    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, string: str):
        self.set_state(string)

    @property
    def pos(self):
        return (self.x, self.y)

    @pos.setter
    def pos(self, other):
        self.x,self.y = other

    # ─────────────────────────────────────────────────────────
    def check_statement(self, *statement) -> bool:
        " Checks a statement like 'active','<',3, returns a boolean "
        if len(statement) == 1:
            return True
        else :
            varname, symbol, threshold = statement
        if symbol not in ('=', '<', '>'):
            raise TypeError("The symbol given in check statement is wrong")
        # -------------------------------------------
        if symbol == '=':
            return self.vars[varname][0] == threshold
        elif symbol == '<':
            return self.vars[varname][0] < threshold
        else:
            return self.vars[varname][0] > threshold

    # ─────────────────────────────────────────────────────────
    def set_state(self, target_state: str):
        """
         A state stores every information about an Agent.
         See the States class file to know more
        """
        assert target_state in self.__class__.states.keys()

        state = self.__class__.states[target_state]

        self.__state = target_state
        self.color = state.color # str not mutable
        self.vars = deepcopy(state.vars) # dict mutable
        self.status = deepcopy(state.status) # dict mutable
        self.fields = deepcopy(state.fields) # dict mutable
        self.sensors = deepcopy(state.sensors) # dict mutable
        self.births = deepcopy(state.births)

    # ─────────────────────────────────────────────────────────
    def check_status(self):
        new_state = 0
        for elements in self.status:  # status are [ target_state, statement]
            if self.check_statement(*elements[1]):
                new_state = elements[0]
        if new_state :
            self.state = new_state

    # ─────────────────────────────────────────────────────────
    def sense_var(self, varname: str, fields: dict, *pos: tuple) -> float:
        """
        Senses the new value of one var according to the fields.
        Removes own interfering fields
        """
        a,b = pos[0] if len(pos) == 0 else pos
        value = 0
        for (field, scale) in self.sensors[varname]:
            value += scale * fields[field][a,b]
            if field in self.fields.keys():
                value -= self.emmit(field, Agent.dist(self.pos,pos)) * scale
        return value

    # -------------------------------------------------------------------------
    def sense_and_change(self, fields: dict):
        new_vars = {} # Storing results in another variable cause we might
            # reuse one old variable to compensate for the field it emmits
        for varname in self.sensors.keys():
            new_vars[varname] = self.sense_var(varname, fields, *self.pos)
        for varname in self.sensors.keys():
            self.vars[varname][0] = new_vars[varname]

    # ─────────────────────────────────────────────────────────
    def time_effect(self):
        """ Marks the effect of time using timestep of vars """
        for varname in self.vars.keys():
            self.vars[varname][0] += self.vars[varname][1]

    # ─────────────────────────────────────────────────────────
    def emmit(self, key: str, dist: int):
        return max(0, self.vars[key][0] + dist * self.fields[key])

    # -------------------------------------------------------------------------
    def field_range(self, key: str, max_lines: int, max_cols: int):
        if key in self.fields.keys():
            # r is the number such as a - r*b > 0 ; a - (r+1)*b <= 0
            r = abs(self.vars[key][0]) // abs(self.fields[key]) - int(
                abs(self.vars[key][0]) % abs(self.fields[key]) == 0)
            for a in range(max(0, self.x - r),
                           min(self.x + r, max_lines-1) + 1):
                for b in range(max(0, self.y - r),
                               min(self.y + r, max_cols - 1) + 1):
                    yield (a, b)
    # ─────────────────────────────────────────────────────────
    def try_birthing(self, *args, **kwargs):
        " Implements the method but its doing nothing "
        pass

    def try_moving(self, *args, **kwargs):
        " Implements the method but its doing nothing "
        pass

    #TEMPORARY
    def informations(self):
        # print(" -> Agent {} at {} {}\n     <> vars : {}".format(self.state,self.x,self.y,self.vars))
        pass
    # ─────────────────────────────────────────────────────────
    def __gt__(self, other):
        return sum([var[0] for var in self.vars.values()]) > sum(
                                        [var[0] for var in other.vars.values()])

    # ─────────────────────────────────────────────────────────
    def __repr__(self):
        return self.state[0].capitalize()

# =============================================================================
class Mineral(Agent):
    def __init__(self, state, *position):
        Agent.__init__(self, state, *position)

# =============================================================================
class Vegetal(Agent):
    def __init__(self, state, *position):
        Agent.__init__(self, state, *position)
        self.newborns = []

    # -------------------------------------------------------------------------
    def give_birth(self, state: str, fields:dict, max_lines:int, max_cols:int,
                                                             cells=None)->None:
        """
        Returns nothing, but updates the self.newborns list with the position &
        state of the next to be born childs
        """
        best = self.best_of_adjacent(fields, max_lines, max_cols, cells=cells)
        if best:
            self.newborns.append([best, state])

    # ─────────────────────────────────────────────────────────
    def try_birthing(self, cells, fields, max_lines, max_cols):
        self.newborns = []
        for children in self.births.keys():
            if self.check_statement(*self.births[children]):
                self.give_birth(children, fields, max_lines, max_cols, cells=cells)
        return bool(self.newborns)

    # -------------------------------------------------------------------------
    def best_of_adjacent(self, fields, max_lines, max_cols, cells=None)->tuple:
        """
        If no cells given, gives the best cells regardless of what
        it contains
        """
        adjacents = self.adjacent(max_lines, max_cols, cells=cells)
        if not adjacents:
            return tuple()
        best = []
        score = -2 * 10 ** 20
        for (i, j) in adjacents:
            sense = 0
            for sensor in self.sensors.keys():
                sense += self.sense_var(sensor, fields, i, j)
            if sense > score:
                best = [(i, j)]
                score = sense
            if sense == score:
                best.append((i, j))
        return choice(best)

    # ─────────────────────────────────────────────────────────
    def adjacent(self, max_lines, max_cols, cells=None)->list:
        coords = []
        for (i,j) in [(0,1),(0,-1),(1,0),(-1,0)]:
            if 0 <= self.x+i <= max_lines-1 and 0 <= self.y+j <= max_cols-1 \
                              and (not cells or not cells[self.x+i][self.y+j]):
                coords.append((self.x+i,self.y+j))
        return coords

# =============================================================================
class Animal(Vegetal):
    def __init__(self, state, *position):
        Vegetal.__init__(self, state, *position)
        self.move = []

    def try_moving(self, fields, max_lines, max_cols):
        self.move = []
        self.move = self.best_of_adjacent(fields, max_lines, max_cols)
        return bool(self.move)
# =============================================================================

if __name__ == '__main__':
    Agent.add_state('test', State('',{'a':[2,0]},{'a':-1},[],{}))
    agent = Agent('test', 10,10)
    print(list(agent.field_range('a', 20, 20)))
