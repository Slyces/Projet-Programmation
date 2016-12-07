# =============================================================================
'''
Quick description of the file
'''
# =============================================================================
__author__ = 'Simon Lassourreuille'
__version__ = ''
__date__ = '04/12/2016'
__email__ = 'simon.lassourreuille@etu.u-bordeaux.fr'
__status__ = 'Prototype'


# =============================================================================

class Debugger(object):
    """
    Class for debugging
    """
    verbose = 1

    @staticmethod
    def print(*printable, lvl: int = 1, exclusive: bool = False) -> None:
        comparison = lvl.__eq__ if exclusive else lvl.__le__
        if comparison(Debugger.verbose):
            print(*printable)


if __name__ == '__main__':
    pass
