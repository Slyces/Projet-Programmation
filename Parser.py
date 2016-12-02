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

def parser(filename='ForestFire'):
    """ Extracts the relevant informations from a file """
    file = open("Examples/"+filename, 'r').read()
    # Parsing lines of the file to remove comments
    lines = file.split('\n')
    blocks = [[]]
    k = 0
    for line in lines :
        comment = line.find('# ')
        if comment == -1:
            comment = len(line)
        if line[:comment].strip() != '':
            blocks[k].append(line[:comment].strip())
        elif line == '':
            blocks.append([])
            k += 1
    returned_blocks = [[[ezCLI.convert(word) for word in line.split(' ')] for line in block] for block in blocks]
    return [parse_map(block) if block[0][0] == 'keys' else block for block in returned_blocks]

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
    agents = dict([(chars[key],[]) for key in chars.keys()])
    for i in range(len(lines)):
        for j in range(len(lines[0])):
            if lines[i][j] != '.':
                for key in chars.keys():
                    if lines[i][j] == key:
                        agents[chars[key]].append('({},{})'.format(i,j))
    agent_block = []
    for type in agents.keys():
        if agents[type]:
            agent_block += [['agent',type] +agents[type]]
    return agent_block

if __name__ == '__main__':
    for block in parser('Wireworld3'):
        print(block)