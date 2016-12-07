# =============================================================================
'''
Quick description of the file
'''
# =============================================================================
__author__ = 'Simon Lassourreuille'
__version__ = '2.0'
__date__ = '05/12/2016'
__email__ = 'simon.lassourreuille@etu.u-bordeaux.fr'
__status__ = 'Prototype'
# =============================================================================
import ezCLI
import ezTK
import tkinter as tk
from Debugger import Debugger as D

def dist(a,b):
    a0,a1 = a
    b0,b1 = b
    return max(abs(a0-b0), abs(a1-b1))

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
    def size(self):
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
                    self.fields[key] = [[0 for i in range(self.nb_cols)]
                                        for j in range(self.nb_lines)]

    # =========================================================================
    def update(self):
        self.update_fields()
        self.update_agents()

    # ─────────────────────────────────────────────────────────
    def update_fields(self):
        # Init of the field
        for key in self.fields.keys():
            self.fields[key] = [[0 for i in range(self.nb_cols)]
                                for j in range(self.nb_lines)]
        for agent in self.agents:
            for key in agent.fields.keys():
                for (i, j) in agent.field_range(key, *self.size):
                    self.fields[key][i][j] += agent.emmit(
                                                key, dist(agent.pos, (i, j)))
    # ─────────────────────────────────────────────────────────
    def update_agents(self):
        for agent in self.agents:
            agent.sense_and_change(self.fields)
            agent.time_effect()
            agent.check_status()

# One try
class GraphicWorldEZTK(ezTK.Win):
    def __init__(self, world: 'World', cell_size:int=20, refresh:int = 250):
        self.world = world
        ezTK.Win.__init__(self, fold=self.world.nb_cols)
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

class GraphicWorld(World,tk.Tk):
    def __init__(self, world: 'World', *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.world = world
        self.frames = [[None for i in range(self.world.nb_cols)] for j in range(self.world.nb_lines)]
        size = 20
        self.T = [[False for i in range(self.world.nb_cols)] for j in range(self.world.nb_lines)]
        for i in range(self.world.nb_lines):
            for j in range(self.world.nb_cols):
                self.frames[i][j] = tk.Frame(self, height=size, width=size)
                self.frames[i][j].grid(row=i,column=j,padx=1,pady=1)
        self.update_frames()

    def update_frames(self):
        self.world.update()
        for i in range(self.world.nb_lines):
            for j in range(self.world.nb_cols):
                if not self.world[i,j] :
                    self.frames[i][j]['bg'] = self.world.color
                else:
                    self.frames[i][j]['bg'] = self.world[i,j].color
        self.after(200, self.update_frames)