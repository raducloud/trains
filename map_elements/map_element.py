from pygame import Color
from math import sqrt
from game_config import *

class Map_element:

    # The parameters end1/end2 ('L'/'R'/'U'/'D' for left/right/up/down) and previous/next_segment references are for elements which can be part of chain (track segments, switches...)
    # end1 and previous_segment are towards "upstream" and end2 and next_segment are towards "downstream", relative to the train movement from the base station.
    #    end1/2 are used for drawing and so must have values even if the segment is not connected to neighbors.
    #    We detect that an ending is not connected by checking the prrevious/next_segment attributes for being populated or not.
    def __init__(self, x, y, end1:str='L', end2:str='R', previous_segment=None, next_segment=None, color=pygame.Color('white'), size=ELEMENT_SIZE):
        self.x = x
        self.y = y
        # Take care for end1 and previous_segment to be pointing towards the same neighbor, same for end2 and next_segment. This is used in logic.
        self._end1=end1
        self._end2=end2
        # below endings coordinates are actual X and Y computed based on L/R/U/D values of end1 and end2 and end2_inactive:
        self.end1_coordinates = None
        self.end2_coordinates = None
        self.versor_x = 0 # for movement direction and heading of potential trains traversing us
        self.versor_y = 0
        self.previous_segment = previous_segment
        self.next_segment = next_segment
        self.size = size
        self.color = color
        self.recompute_heading() 
        
    # The end1 and end2 attributes are implemented as properties in order to add some auto-rearanging or extra logic of the element in some cases. 
    @property
    def end1(self): return self._end1
    @property
    def end2(self): return self._end2

    @end1.setter
    def end1(self, value): 
        self._end1 = value
        self.recompute_heading()
        
    @end2.setter
    def end2(self, value): 
        self._end2 = value
        self.recompute_heading()
    
    def recompute_heading(self):
        # computes endings coordinates and movement vector (of potential trains traversing us) based on center(x,y) and orientation (end1/2=L/R/U/D)
        end_coordinates_map = {  # coordinates of points where the element can connect - left, right, up or down
            'L': (self.x - self.size//2, self.y),
            'R': (self.x + self.size//2, self.y),
            'U': (self.x, self.y - self.size//2),
            'D': (self.x, self.y + self.size//2),
            None: (None, None)
        }
        self.end1_coordinates = end_coordinates_map[self._end1]
        self.end2_coordinates = end_coordinates_map[self._end2]
        
        # movement versor
        # It only makes sense to calculate it if end2 is set (if the element has a downstream connection)
        if self.end2_coordinates[0] and self.end2_coordinates[1]:
            # the origin of movement can be either end1 (if the element has an upstream connection)
            # or otherwise the centre (as is the case for Base_station)
            if self.end1_coordinates[0] and self.end1_coordinates[1]:
                origin_x = self.end1_coordinates[0]
                origin_y = self.end1_coordinates[1]
            else:
                origin_x = self.x
                origin_y = self.y
            detla_x = self.end2_coordinates[0] - origin_x
            detla_y = self.end2_coordinates[1] - origin_y
            hypotenuse = sqrt(detla_x*detla_x + detla_y*detla_y)
            
            if hypotenuse == 0: # can happen in some extreme cases for the element to have length 0 (begins where it ends) - a design error, but should be handled
                self.versor_x = 0
                self.versor_y = 0
            else:
                self.versor_x = detla_x / hypotenuse
                self.versor_y = detla_y / hypotenuse

    def draw(self, screen):
        # Write move versors for debugging
        font = pygame.font.Font(None, VERY_SMALL_TEXT_SIZE)
        text = font.render(f"{self.versor_x:.1f},{self.versor_y:.1f}", True, pygame.Color('white'))
        text_rect = text.get_rect(center=(self.x, self.y-ELEMENT_SIZE//3))
        screen.blit(text, text_rect)

