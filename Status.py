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
from typing import Callable, Optional
TimeFunction = Optional[Callable[['Status'], None]]


def useless_function(*args, **kwargs) -> None: return


# =============================================================================
class Status(object):
    """
    A status is a class related to Agent handling one parameter of an Agent
    It has the important role of managing every kind of information we can know
    about an Agent. A status can and must change over time.
    For this, 3 kinds of trigger exists :
    - time based trigger : modification of the variable with every loop of the
      system
    - interaction based trigger : if an unit interacts with another unit
    - other status action : if another status reaches a step and modifies this
      status

    A status has one or more steps. Upon reaching these steps, a function is
    called to make an action. Modifying a sensor, modifying a status ...
    """

    def __init__(self, start: int,
                 steps=[],
                 min_val: Optional[int] = None,
                 max_val: Optional[int] = None,
                 time_effect: TimeFunction = None)->'Status':
        """
        This function creates a status. See class description
        :param start: init value of the status
        :param steps: list of this structure, already ordered by steps :
                      [ (step0, function0),
                        (step1, function1) ]

                      where function 0 is called uppon reaching :
                      step0 <= value < step1

                      function n is called upon reaching :
                      step[n] <= value <= step[n+1]
        :param min: minimal value, optionnal
        :param max: maximal value, optionnal
        :param time_effect: function called upon each time loop on the variable
        """
        # Basic attributes
        self.__value = start
        self.__timeEffect = time_effect
        self.min, self.max = min_val, max_val
        self.__steps = [step[0] for step in steps]
        self.__functions = [step[1] for step in steps]

    def start(self):
        """
        The status has to call a function when an interval is reached.
        The start calls the interval in which the starting position is.
        """
        start = self()  # Getting the actual starter value
        self(-100000)  # Setting the value to a big value to be sure we get out
                       # of the current interval
        self(start)  # Then coming back to that interval

    def time(self)->None:
        """ Uses the function given in time effect """
        if self.__timeEffect :  # First checking if that function exists
            return self.__timeEffect(self)
        return

    def __call__(self, other=None):
        """ self() returns the current value of the status """
        if other is None:  # When called on self()
            return self.__value
        else:
            assert isinstance(other, (int,float)), "Type error in [status]({})" \
                                                   "".format(other)
            self += other - self.__value

    def __add__(self, other: [int,float]):
        """
        The complex function of Status class.
        The main goal of this function is to restrain the evolution of a status
        by "steps". Every new value is compared to the precedent one.

        Every status is structured like :
        [x0, x1[ u [x1, x2[ u [x2, x3[ u [xn-1, xn[
        """
        backup = self.__value
        self.__value += other
        if self.max and self.__value > self.max :
            self.__value = backup
        if self.min and self.__value < self.min :
            self.__value = backup
        if self.__steps :
            k = sum([self.__value >= self.__steps[i] for i in range(
                                                            len(self.__steps))])
            l = sum([backup >= self.__steps[i] for i in range(
                                                            len(self.__steps))])
            if k != l and k > 0:
                self.__functions[k-1]()
        return self

    def __sub__(self, other):
        return self.__add__(-other)

# =============================================================================
# Usual Status
class Death(Status):
    def __init__(self):
        Status.__init__(self, 0, min_val=0, max_val=1)

class Thirst(Status):
    def __init__(self, agent):
        Status.__init__(self, 100, steps=[(-50,agent.death)])

class Hunger(Status):
    def __init__(self, agent, feeding_type: str):
        self.agent = agent
        self.agent = agent
        self.feeding_type = feeding_type
        Status.__init__(self, 100, min_val=-200, max_val=100,
                        time_effect= lambda s : s - 5,
                        steps=[(-200,agent.death)] + [(a,lambda x=b: self.find_food(x)) for (a,b) in [(-150,100),(0,50),(50,0)]])

    def find_food(self, value):
        self.agent.sensors[self.feeding_type] = value

class Age(Status):
    def __init__(self, agent):
        self.agent = agent
        Status.__init__(self,0,time_effect= lambda s: s + 5,
                        steps=[(10*(x+1),self.coloring) for x in range(200)])

    def coloring(self):
        self.agent.colored = '#' + hex(max(0,255-self()))[2:].zfill(2) + '5050'
        print(self.agent.colored)

def say(i):
    print("Step {} crossed".format(i))


if __name__ == '__main__':
    S = Status(50, [(-100+10*i,lambda x=-100+10*i:say(x)) for i in range(21)], min_val=-100, max_val=-100)
    Age()