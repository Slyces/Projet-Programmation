# =============================================================================
'''
Quick description of the file
'''
# =============================================================================
__author__ = 'Simon Lassourreuille'
__version__ = ''
__date__ = '07/11/2016'
__email__ = 'simon.lassourreuille@etu.u-bordeaux.fr'
__status__ = 'Prototype'
# =============================================================================
from typing import Optional

class Field(object):

    inf = pow(10,9)
    def __init__(self, strength:int, max_range: int, min_range: int=1,
                 reduction: str='None'):
        """
        :param strength: strength of the field
        :param range: maximum range of the field
        :param starter: minimum range of the field, often set to 1
        :param reduction: function to determine the strength of the field
                according to the distance from the Agent
                Pick one among :
                - None : field is equal on every cell
                - Low : strength - (dist/range)
                - High : strength / dist
        """
        self.__strength = strength
        self.max_range = max_range
        self.min_range = min_range
        self.compute = {'None' : self.__uniform,
                          'Low' : self.__low,
                          'High' : self.__high}[reduction.capitalize()]


    def __uniform(self, dist):
        """ Uniform repartition ; no changes through distance"""
        if self.min_range <= dist <= self.max_range :
            return self.__strength
        return 0

    def __low(self, dist):
        """ Value slowly lowering with distance """
        if self.min_range <= dist <= self.max_range :
            return self.__strength - (dist/self.max_range)
        return 0

    def __high(self, dist):
        """ Value highly lowering with distance """
        if self.min_range <= dist <= self.max_range :
            return self.__strength / dist if dist else 2*self.__strength
        return 0
