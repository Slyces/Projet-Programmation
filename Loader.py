# =============================================================================
'''
Quick description of the file
'''
# =============================================================================
__author__ = 'Simon Lassourreuille'
__version__ = '2.0'
__date__ = '04/12/2016'
__email__ = 'simon.lassourreuille@etu.u-bordeaux.fr'
__status__ = 'Prototype'
# =============================================================================
import ezCLI
from World import World, GraphicWorld
from Agents import Mineral, Vegetal, Animal, State
from random import choice
from Debugger import Debugger as D


# -----------------------------------------------------------------------------

def parser(filename: str = 'ForestFire') -> list:
    """
    Extracts the relevant informations from a file
    -> Returns a list of blocks
        -> A block is separated by a blank line in the file
           a block is a list of lines
            -> A line is a list of words
                -> Words are converted as int or tuples when possible
    """
    file = open("Examples/" + filename, 'r').read()
    # Parsing lines of the file to remove comments
    lines = file.split('\n')
    blocks = [[]]
    k = 0
    for line in lines:
        comment = line.find('# ')
        if comment == -1:
            comment = len(line)
        if line[:comment].strip() != '':  # Converting a line in a list of words
            blocks[k].append([ezCLI.convert(word) for word
                              in line[:comment].strip().split(' ')])
            if line[:5] == 'agent':
                # If the first word of the line is agent, there can be agents
                # like (a:b,c:d) expecting special processing
                new_line = blocks[k][-1][:2]  # Keeping the ['agent','_state_']
                for word in blocks[k][-1][2:]:  # Processing remainings positions
                    new_line += position_slicer(word)
                # Unpacking of slicing notation is done, let's process choices
                if new_line[1][:6] == 'choice':
                    # Here, we have : agent choice(empty,a1,...,an)
                    # We process by doing a dict of lists
                    choices = new_line[1][7:-1].split(',')
                    agents = dict([(word, ['agent', word]) for word in choices])
                    for element in new_line[2:]:
                        agents[choice(choices)].append(element)
                    blocks[k] = blocks[k][:-1] # Deleting the last line
                    # Adding new lines for each type
                    for key in agents.keys():
                        if key != 'empty' :
                            blocks[k].append(agents[key])
                else:
                    blocks[k][-1] = new_line

        elif line == '':  # Jumping to new block on real empty line
            blocks.append([])
            k += 1
    # Now dealing with maps representation, with the keyword keys
    for i in range(len(blocks)):
        # print(blocks[i])
        if blocks[i][0][0] == 'keys':
            blocks[i] = parse_map(blocks[i])
    return blocks

# -----------------------------------------------------------------------------
def position_slicer(word):
    """
    slicing a word like (0:4,0:1) in :
    (0,0) (0,1) (1,0) (1,1) (2,0) (2,1) (3,0) (3,1) (4,0) (4,1)
    """
    if type(word) == tuple:  # When there's no ':', ezCLI makes it a tuple
        return [word]
    # Here we have : (a, b:c) or (a:b, c) or (a:b, c:d)
    coords = word[1:-1].split(',')
    for i in range(2):
        if ':' in coords[i]:
            a, b = coords[i].split(':')
            coords[i] = list(range(int(a), int(b)))
        else:
            coords[i] = [int(coords[i])]
    return [(a, b) for a in coords[0] for b in coords[1]]


def parse_map(block):
    """
    The block extracted from a file is like this :
    [ ['keys', '(letter,agent_name)', ... ], # [0] : Chars correspondance
      [<class 'map'>], [1] : Annoucing the map
      ['.','.','.','.', ... ], [2:] -> real map
      ['-','-','+','+', ... ],
      [ ... ]
      ['-','-','+','+', ... ] ]
    """
    # Extracting the dict of chars correspondance
    # Not keeping the 'keys', a couple is '(letter,agent_name)'
    chars = dict([couple[1:-1].split(',') for couple in block[0][1:]])
    lines = block[1:]
    agents = dict([(chars[key], []) for key in chars.keys()])
    for i in range(len(lines)):
        for j in range(len(lines[0])):
            if lines[i][j] != '.':
                for key in chars.keys():
                    if lines[i][j] == key:
                        agents[chars[key]].append((i, j))
    agent_block = []
    for type in agents.keys():
        if agents[type]:
            agent_block += [['agent', type] + agents[type]]
    return agent_block



# =============================================================================
def create_state(block: list):
    """
    Creating state from a block like 'mineral ...' or 'vegetal ...'
        or 'animal ...'
    """
    name, color = block[0][1:]  # mineral name color
    vars, status, fields, sensors, births = {}, [], {}, {}, {}
    for line in block[1:]:
        # Creating vars
        if line[0] == "var":
            # var name init_val=0 time_step=0
            if len(line) < 3:
                line.append(0)
            if len(line) < 4:
                line.append(0)
            vars[line[1]] = line[2:]
        # Creating status
        if line[0] == 'status':
            # status varname < k targetstate
            # or status targetstate
            if len(line) == 5:
                status.append([line[4], line[1:4]])
            else :
                status.append([line[1], [True]])
        # Creating sensors
        if line[0] == 'sensor':
            # sensor hosting_var impacting_field scale
            if line[2] not in sensors.keys():
                sensors[line[1]] = []
            sensors[line[1]].append([line[2],line[3]])
        # Creating fields
        if line[0] == 'field':
            # field variable reduction
            fields[line[1]] = line[2]
        if line[0] == 'birth':
            # birth seed < 1 photophobia
            births[line[4]] = line[1:4]

    return State(color, vars, fields, status, sensors, births)
# =============================================================================
def load(filename='Wireworld'):
    parsed = parser(filename)

    # Configuring Mineral, Vegetal & Animal
    classes = {'mineral': Mineral, 'animal': Animal, 'vegetal': Vegetal}
    states_classes = {}
    for block in parsed:
        if block[0][0] == 'world':  # Creating the world
            world = World(*block[0][1:])
        if block[0][0] in ('mineral', 'animal', 'vegetal'):
            state = create_state(block)  # Parsing block
            classes[block[0][0]].add_state(block[0][1],state)
            states_classes[block[0][1]] = block[0][0]
        if block[0][0] == 'agent':
            # agent state (a1,b1) (a2,b2) ... (
            for line in block :
                for i in range(len(line) - 2):
                    world.add_agent(classes[states_classes[line[1]]](line[1], *line[2 + i]))
    return world


if __name__ == '__main__':
    # world = load('Game Of Life')
    # print(world)
    # for i in range(8):
    #     print('='*161)
    #     world.update_fields()
    #     print(ezCLI.grid([[' ' if k == 0 else k for k in line]for line in world.fields['life']], size=3))
    #
    #     # Looking at one head's sensing
    #     for agent in world.agents :
    #         if agent.state == 'head':
    #             agent.sensors['test'] = [['electric', 1]]
    #             map = [[0 for j in range(6)]for i in range(7)]
    #             for i in range(7):
    #                 for j in range(6):
    #                     map[i][j] = agent.sense_var('test', world.fields, i, j)
    #
    #             print("Head at position {} would sense electricity this way :".format(agent.pos))
    #             print(ezCLI.grid([[' ' if k == 0 else k for k in line]for line in map], size=3))
    #             agent.sensors.pop('test')
    #     world.update_agents()
    #     print(world)
    world = GraphicWorld(load('PhotoTropism'))
    world.mainloop()
