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
import ezCLI
import tkinter as tk
from Agent import AgentFactory, create_Agent, create_state
from Parser import parser, parse_map

verbose = 3

def dist(pos0, pos1):
    x0,y0 = pos0
    x1,y1 = pos1
    return max(abs(x0-x1), abs(y0-y1))

class World(object):
    """ Grille rectangulaire sur laquelle évoluent les Agents """

    def __init__(self, n: int, m: int, color: str)->'World':
        """
        Respectivement le nombre de lignes et colonnes
        """
        self.nb_lines,self.nb_cols = n,m
        self.__cells = [[0 for i in range(m)] for j in range(n)]
        self.fields = {}
        self.agents = []

    def __getitem__(self, item):
        if isinstance(item, (tuple, list)) and len(item)==2:
            return self.__cells[item[0]][item[1]]

    def __setitem__(self, key, value):
        if isinstance(key, (tuple, list)):
            self.__cells[key[0]][key[1]] = value

    def __repr__(self):
        return ezCLI.grid(self.__cells,size=3)

    def update(self):
        self.update_fields()
        self.update_agents()

    def add_agents(self, *agents):
        for agent in agents :
            self[agent.pos] = agent
            self.agents.append(agent)
        # Updating the fields maps
        keys = self.fields.keys() # get the fields registered
        for agent in self.agents:
            for key in agent.fields.keys():
                if key not in keys : # register a new field
                    self.fields[key] = [[0 for i in range(self.nb_cols)]
                                           for j in range(self.nb_lines)]

    def update_fields(self):
        # Init of the fields
        for key in self.fields.keys():
            self.fields[key] = [[0 for i in range(self.nb_cols)]
                                   for j in range(self.nb_lines)]
            for agent in self.agents:
                if key in agent.fields.keys():
                    for i in range(self.nb_lines):
                        for j in range(self.nb_cols):
                            self.fields[key][i][j] += agent.emmit(key, dist(agent.pos, (i,j)))
        if verbose > 0:
            print(ezCLI.grid(self.fields['life'], size=3))
            pass

    def update_agents(self):
        if verbose >= 1 :
            print("========================================")
        for agent in self.agents:
            for field in self.fields.keys():
                if verbose >= 1 :
                    print('----------------------------------------')
                    print("Sensing a field at position : {} {}, value : {}".format(agent.x,agent.y,self.fields[field][agent.x][agent.y]))
                agent.sense(field, self.fields[field][agent.x][agent.y])
                if verbose >= 1 :
                    print('----------------------------------------')
                agent.test_status()

def load_file(filename='Wireworld.txt'):
    parsed = parser(filename)

    # Configuring the new Agent
    states = []
    for block in parsed:
        # Creating the world
        if block[0][0] == 'world':
            world = World(*block[0][1:])
        if block[0][0] in ('mineral', 'animal', 'vegetal'):
            states.append(create_state(block))
        if block[0][0] == 'agent':
            AgentCreator = AgentFactory(states)# Assuming agents are at the end
            agents = create_Agent(AgentCreator, block) # Creating agents
            world.add_agents(*agents) # Adding them into the world
    return world

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
                    self.frames[i][j]['bg'] = '#FFF'
                else:
                    if verbose >= 3 :
                        print(self.world[i, j], self.world[i, j].color)
                    self.frames[i][j]['bg'] = self.world[i,j].color
        self.after(25, self.update_frames)

if __name__ == '__main__':
    world =load_file('Game of Life')
    window = GraphicWorld(world)
    window.mainloop()

