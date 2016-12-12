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
import ezCLI
import ezTK
import tkinter as tk
from Debugger import Debugger as D
from numpy import array
from Agents import Agent,Animal,Vegetal

# Debugging : priority of birth at n+1 = lvl 11 #arbitrary
# Debugging : moves at n+1 = lvl 13
# Deeper interactions : lvl 17
D.verbose = 0


# =============================================================================
class World(object):
    """ Grille rectangulaire sur laquelle évoluent les Agents """

    def __init__(self, n: int, m: int, color: str) -> 'World':
        """ Respectivement le nombre de lignes et colonnes """
        self.nb_lines, self.nb_cols = n, m
        self.__cells = [['' for i in range(m)] for j in range(n)]
        self.fields = {}
        self.agents = []
        self.color = color

    @property
    def size(self)->tuple:
        return (self.nb_lines, self.nb_cols)

    def __getitem__(self, item):
        if isinstance(item, (tuple, list)) and len(item) == 2:
            return self.__cells[item[0]][item[1]]

    def __setitem__(self, key: str, value)->None:
        if isinstance(key, (tuple, list)):
            self.__cells[key[0]][key[1]] = value

    def __repr__(self):
        return ezCLI.grid(self.__cells, size=3)

    # -------------------------------------------------------------------------
    def add_agent(self, agent)->None:
        """
        :param agents: tuple of Agents or one Agent
        :return:
        """
        self[agent.pos] = agent
        self.agents.append(agent)
        # Updating the fields maps
        keys = self.fields.keys()  # get the fields registered
        for agent in self.agents:
            for key in agent.fields.keys():
                if key not in keys:  # register a new field
                    self.fields[key] = array([[0 for i in range(self.nb_cols)]
                                        for j in range(self.nb_lines)])

    # =========================================================================
    def update(self):
        self.update_fields()
        self.update_agents()

    # ─────────────────────────────────────────────────────────
    def update_fields(self):
        # Init of the field
        for key in self.fields.keys():
            self.fields[key] = array([[0 for i in range(self.nb_cols)]
                                for j in range(self.nb_lines)])
        for agent in self.agents:
            for key in agent.fields.keys():
                for (i, j) in agent.field_range(key, *self.size):
                    self.fields[key][i,j] += agent.emmit(
                                                key, Agent.dist(agent.pos, (i, j)))
    # ─────────────────────────────────────────────────────────
    def update_agents(self):
        birth_givers = []
        moving = []
        for agent in self.agents:
            agent.sense_and_change(self.fields)
            agent.time_effect()
            agent.informations()
            if agent.try_birthing(self.__cells, self.fields, *self.size):
                birth_givers.append(agent)
            if agent.try_moving(self.fields, *self.size):
                moving.append(agent)
            if agent.state == 'death':
                self[agent.pos] = ''
                self.agents.remove(agent)
        self.handle_movements(moving)
        self.handle_birth_conflicts(birth_givers)
        for agent in self.agents :
            agent.check_status()
    # ─────────────────────────────────────────────────────────
    def handle_movements(self, moving):
        """ Handles the movement interactions """
        D.print('Called me with moving : {}'.format(moving), lvl=13, exclusive=True)
        new_map=[[0 for i in range(self.nb_cols)]for j in range(self.nb_lines)]
        leftovers = []
        for agent in moving:
            a,b = agent.move
            D.print("   Agent at pos {} {} wants to move to {} {}".format(agent.x,agent.y,a,b), lvl=13, exclusive=True)

            D.print("      -> on the map, this cell is : <{}>".format(self[a,b]), lvl=13, exclusive=True)
            if not self[a,b]:  # Moving to an empty cell in real world
                if new_map[a][b] and agent > new_map[a][b] : # case wanted
                    D.print('Conflict over the cell {} {}\n  Stronger agent (winning):\n--------------------'.format(a,b), lvl=17, exclusive=True)
                    agent.informations()
                    D.print('--------------------', lvl=17, exclusive=True)
                    D.print(
                        '  Weaker agent (loosing):\n--------------------'.format(a, b),
                        lvl=17, exclusive=True)
                    new_map[a][b].informations()
                    D.print('--------------------', lvl=17, exclusive=True)
                    leftovers.append(new_map[a][b])
                    new_map[a][b] = agent # I'm stronger, taking the place
                elif new_map[a][b]: # I'm weaker
                    D.print(
                        'Conflict over the cell {} {}\n  Stronger agent (winning):\n--------------------'.format(a, b),
                        lvl=17, exclusive=True)
                    new_map[a][b].informations()
                    D.print('--------------------', lvl=17, exclusive=True)
                    D.print(
                        '  Weaker agent (loosing):\n--------------------'.format(a, b),
                        lvl=17, exclusive=True)
                    agent.informations()
                    D.print('--------------------', lvl=17, exclusive=True)
                    leftovers.append(agent)
                else :
                    new_map[a][b] = agent
            elif agent > self[a,b]: # The real world cell is not empty
                for var in agent.vars.keys():
                    if var in self[a,b].vars.keys():
                        agent.vars[var][0] += self[a,b].vars[var][0]
                        self[a,b].vars[var][0] = 0
            else :
                for var in self[a,b].vars.keys():
                    if var in agent.vars.keys():
                        self[a, b].vars[var][0] += agent.vars[var][0]
                        agent.vars[var][0] = 0
        for i in range(self.nb_lines):
            for j in range(self.nb_cols):
                if new_map[i][j]:
                    self[new_map[i][j].pos] = ''
                    self[new_map[i][j].move] = new_map[i][j]
                    new_map[i][j].pos = new_map[i][j].move
        if leftovers:
            self.handle_movements(leftovers)

    # ─────────────────────────────────────────────────────────
    def handle_birth_conflicts(self, birth_givers):
        # Handling conflicts in birth
        Map = [[0 for i in range(self.nb_cols)]for j in range(self.nb_lines)]
        leftovers = []
        newborns = []
        for agent in birth_givers:
            for newborn in agent.newborns:
                # newborn like ((x,y), state)
                newborns.append([agent] + newborn)
        for newborn in newborns:
            # newborn like [agent, (x,y), state]
            x,y = newborn[1]
            if not Map[x][y]: # If no one wants this case, take it
                Map[x][y] = newborn
            else: # If the case is taken, take it if you're stronger
                D.print("The case I want :[{} {}] is taken !!".format(x,y),lvl=11,exclusive=True)
                D.print("     I'm a {} in case {} {} against a {} in case {} {}.\n"\
                      "           My sum is {}, my vars {}\n"\
                      "           Its sum is {}, its vars {}".format(
                    newborn[0].state, newborn[0].x, newborn[0].y,
                    Map[x][y][0].state, Map[x][y][0].x, Map[x][y][0].y,
                    sum([var[0] for var in newborn[0].vars.values()]),newborn[0].vars,
                    sum([var[0] for var in Map[x][y][0].vars.values()]),Map[x][y][0].vars
                ),lvl=11,exclusive=True)
                if newborn[0] > Map[x][y][0]:
                    leftovers.append(Map[x][y][0])
                    Map[x][y] = newborn
                else : # If you're not, you're left over
                    leftovers.append(newborn[0])
        birth_givers = []
        for line in Map:
            for element in line:
                if element: # [agent, (x,y), state]
                    agent,(x,y),state = element
                    self.add_agent(agent.__class__(state, x, y))
                    D.print(' <> Agent at [{} {}] was not challenged when infanting at [{} {}]'.format(agent.x, agent.y, x, y),lvl=11,exclusive=True)
        for agent in leftovers:
            if agent.try_birthing(self.__cells, self.fields, *self.size):
                birth_givers.append(agent)
        if birth_givers:
            self.handle_birth_conflicts(birth_givers)


# ────────────────────────────────────────────────────────────
# One try
class GraphicWorldEZTK(ezTK.Win):
    def __init__(self, world: 'World', refresh:int = 250):
        self.world = world
        ezTK.Win.__init__(self, fold=self.world.nb_cols)
        # Computing the size of every frame
        width = int(self.winfo_screenwidth() * 0.99)
        height = int(self.winfo_screenheight() * 0.80)
        cell_size = min(width//self.world.nb_cols, height//self.world.nb_lines)
        # ---------------------------------
        for loop in range(self.world.nb_cols*self.world.nb_lines):
            ezTK.Brick(self, bg=self.world.color, height=cell_size,
                       width=cell_size)
        self.refresh = refresh
        self.graphic_update()

    def graphic_update(self):
        for i in range(self.world.nb_lines):
            for j in range(self.world.nb_cols):
                self[i][j]['bg'] = self.world.color if not \
                                     self.world[i,j] else self.world[i,j].color
        self.world.update()
        self.after(self.refresh, self.graphic_update)


# ────────────────────────────────────────────────────────────
class GraphicWorld(World,tk.Tk):
    def __init__(self, world: 'World', *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.world = world
        self.frames = [[None for i in range(self.world.nb_cols)]
                       for j in range(self.world.nb_lines)]

        # Computing the size of every frame
        width = int(self.winfo_screenwidth() * 0.80)
        height = int(self.winfo_screenheight() * 0.80)
        size = min(width // self.world.nb_cols, height // self.world.nb_lines)
        # ---------------------------------
        self.T = [[False for i in range(self.world.nb_cols)]
                  for j in range(self.world.nb_lines)]
        for i in range(self.world.nb_lines):
            for j in range(self.world.nb_cols):
                self.frames[i][j] = tk.Frame(self, height=size, width=size)
                self.frames[i][j].grid(row=i,column=j,padx=1,pady=1)
        self.bind('<space>', lambda unused_ev: self.update_frames())
        self.update_frames()

    # ─────────────────────────────────────────────────────────
    def update_frames(self):
        self.world.update()
        print('==============================================================')
        for i in range(self.world.nb_lines):
            for j in range(self.world.nb_cols):
                if not self.world[i,j] :
                    self.frames[i][j]['bg'] = self.world.color
                else:
                    self.frames[i][j]['bg'] = self.world[i,j].color
        #self.after(600, self.update_frames)
    # ─────────────────────────────────────────────────────────