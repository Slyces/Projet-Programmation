# =============================================================================
'''
Quick description of the file
'''
# =============================================================================
__author__ = 'Simon Lassourreuille'
__version__ = ''
__date__ = '02/11/2016'
__email__ = 'simon.lassourreuille@etu.u-bordeaux.fr'
__status__ = 'Prototype'
# =============================================================================
from World import *

class Tester(GraphicWorld):

    def __init__(self, *args, **kwargs):
        GraphicWorld.__init__(self, *args, **kwargs)
        #self.ws[2] = tk.Frame(self, height=200, width=200)
        #self.ws[2].pack()

if __name__ == '__main__':
    world = Tester(30,30)
    poss = [(a,b) for a in range(30) for b in range(30)]
    for pos in [ch(poss) for i in range(5)]:
        world.create_agent(Agents.Predateur(pos))
    for pos in [ch(poss) for i in range(10)]:
        world.create_agent(Agents.Proie(pos))
    world.start()
    world.mainloop()