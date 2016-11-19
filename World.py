# =============================================================================
'''
World class for the OSCAR programming project
'''
# =============================================================================
__author__ = 'Simon Lassourreuille'
__version__ = ''
__date__ = '02/11/2016'
__email__ = 'simon.lassourreuille@etu.u-bordeaux.fr'
__status__ = 'Prototype'
# =============================================================================
# Imports
import tkinter as tk
import Agents
from random import choice as ch

# =============================================================================
class World(object):
    """
    Represents the board of cells, where each cell represents void or on agent
    """
    def __init__(self, n: int, m: int)->'World':
        """
        :param n: length of the board (number of cells)
        :param m: height of the board (number of cells)
        """
        self.fields = {}
        self.size = (n,m) # x,y ; length,height

        # Creating the cells. Init to None, an empty cell
        self.cells = [[0 for i in range(n)]for j in range(m)]
        self.agent_types = {}

    def create_agent(self, agent: 'Agents.Agent')->None:
        if agent.type in self.agent_types.keys():
            self.agent_types[agent.type].append(agent)
        else :
            self.agent_types[agent.type] = [agent]
            self.fields[agent.type] = [[0 for i in range(self.size[0])]
                                       for j in range(self.size[1])]
        keys = agent.sensors.keys()
        for key in self.agent_types.keys():
            assert key in keys, "Missing sensor"
        a,b = agent.pos
        self.cells[a][b] = agent

    def kill_agent(self, agent):
        self.agent_types[agent.type].remove(agent)
        a,b = agent.pos
        self.cells[a][b] = 0
        del agent

    def update_agents(self):
        # Reseting cells to place each
        self.cells = [[0 for i in range(self.size[0])]
                         for j in range(self.size[1])]
        self.compute_fields()
        for type in self.agent_types.keys():
            for agent in self.agent_types[type] :
                agent.age()
                x,y = agent.pos
                for (a,b) in self.__get_close(*agent.pos):
                    if agent.sense(self.fields, a, b) >= agent.sense(self.fields, x, y):
                        x,y = a,b
                if not self.cells[x][y]:
                    self.cells[x][y] = agent
                    agent.pos = (x,y)
                else :
                    if (agent.type,self.cells[x][y].type) in [('Proie','Predateur'),('Predateur','Proie')]:
                        if agent.type == 'Proie' :
                            self.kill_agent(agent)
                        else :
                            self.kill_agent(self.cells[x][y])
                        print('AHAHAHAH KILLED A PREY')
                if agent.status['Death']() :
                    self.kill_agent(agent)

    def compute_fields(self):
        for type in self.agent_types.keys():
            self.fields[type] = [[0 for i in range(self.size[0])]
                                    for j in range(self.size[1])]
            for agent in self.agent_types[type] :
                x,y = agent.pos
                for (a,b) in self.__get_close(x,y, agent.field.max_range):
                    self.fields[type][a][b] += agent.field.compute(abs(x-a)+abs(y-b))


    def __get_close(self, a, b, dist=1):
        cells = [(a,b)]
        for i in range(-dist,dist+1):
            for j in range(-dist,dist+1):
                if abs(i) + abs(j) <= dist :
                    if 0 <= a + i < self.size[0] and 0 <= b + j < self.size[1]:
                        cells.append((a+i,b+j))

        return cells



class GraphicWorld(tk.Tk, World):
    """
    A graphic representation of the world
    """
    def __init__(self, n: int, m: int, *args, **kwargs)->'GraphicWorld':
        """
        This class merges a graphic representation with the World object
        handling agents
        :param n: length of the board (number of cells)
        :param m: height of the board (number of cells)
        :param args: classic params for Tk object (see tkinter : Tk 's doc)
        :param kwargs: same as args
        """
        World.__init__(self, n, m)
        tk.Tk.__init__(self, *args, **kwargs)
        cell_size = 20

        self.ws = {}
        self.ws[1] = tk.Frame(self)
        self.ws[1].pack(side='right')

        # Creating the graphic cells
        self.frames = [[None for i in range(n)] for j in range(m)]
        for i in range(m):
            for j in range(n):
                self.frames[i][j] = tk.Frame(self.ws[1], height=cell_size,
                                                  width=cell_size, background='white')
                self.frames[i][j].grid(row=i,column=j)

    def update_cells(self)->None:
        """
        Loops through every cell to update the screen according to
        their state or position
        :return: None
        """
        self.update_agents()
        for i in range(self.size[0]):
            for j in range(self.size[1]):
                self.frames[i][j]['bg'] = self.cells[i][j].get_color() if self.cells[i][j] else 'white'
        try :
            print("Actuellement, le prédateur d'id {} a faim comme ça : {} et du coup il s'intéresse aux proies comme ça : {}".format(
                self.agent_types['Predateur'][0].id,self.agent_types['Predateur'][0].status['Hunger'](),self.agent_types['Predateur'][0].sensors['Proie']
            ))
        except :
            print("Woops, he's dead")
        self.after(500, self.update_cells)

    def start(self):
        self.update_cells()

if __name__ == '__main__':
    world = GraphicWorld(30,30)
    poss = [(a,b) for a in range(30) for b in range(30)]
    for pos in [ch(poss) for i in range(5)]:
        world.create_agent(Agents.Predateur(pos))
    for pos in [ch(poss) for i in range(10)]:
        world.create_agent(Agents.Proie(pos))
    for pos in [ch(poss) for i in range(20)]:
        world.create_agent(Agents.Vegetal(pos))
    world.start()
    world.mainloop()