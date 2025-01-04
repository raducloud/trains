from pygame import Color
from game_config import *

class Map_element:

    # The parameters end1/end2 ('L'/'R'/'U'/'D' for left/right/up/down) and previous/next_segment references are for elements which can be part of chain (track segments, switches...)
    # end1 and previous_segment are towards "upstream" and end2 and next_segment are towards "downstream", relative to the train movement from the base station.
    def __init__(self, x, y, end1:str=None, end2:str=None, previous_segment=None, next_segment=None, color=pygame.Color('white'), size=ELEMENT_SIZE):
        self.x = x
        self.y = y
        # Take care for end1 and previous_segment to be pointing towards the same neighbor, same for end2 and next_segment. This is used in logic.
        self._end1=end1
        self._end2=end2
        self.previous_segment = previous_segment
        self.next_segment = next_segment
        self.size = size
        self.color = color

    # The end1 and end2 attributes are implemented as properties in order to add some auto-rearanging logic of the element in some cases. 
    @property
    def end1(self): return self._end1
    @property
    def end2(self): return self._end2
    @end1.setter
    def end1(self, value): 
        self._end1 = value
        # if the segment has curled (because of connecting to a reverse-placed unconnected neighbor), straighten it:
        # if self._end2 == self._end1:
        #     self._end2 = Utils.get_opposite_end(self._end1)
        
    @end2.setter
    def end2(self, value): 
        self._end2 = value
        # if the segment has curled (because of connecting to a reverse-placed unconnected neighbor), straighten it:
        # if self._end1 == self._end2:
        #     self._end1 = Utils.get_opposite_end(self._end2)
    
    def draw(self, screen):
       pass # abstract function

