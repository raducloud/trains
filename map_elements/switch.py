import pygame
from .map_element import Map_element
from game_config import *

class Switch(Map_element):
    # this has additional attributes *_inactive. They are the alternative way the switch can connect if toggled, 
    #     case in which end2/end2_inactive and next_segment/next_segment_inactive will switch places.
    def __init__(self, *args, **kwargs):
        self._end2_inactive = 'D'
        self.next_segment_inactive = None
        self.end2_inactive_coordinates = None
        super().__init__(*args, **kwargs)  # this will also call recompute_end_coordinates (the overwritten below version)

    @property
    def end2_inactive(self): return self._end2_inactive

    @end2_inactive.setter
    def end2_inactive(self, value): 
        self._end2_inactive = value
        self.recompute_heading()

    def toggle(self):
        # Switch between the two possible mobile ends
        self._end2, self._end2_inactive = self._end2_inactive, self._end2
        self.end2_coordinates, self.end2_inactive_coordinates = self.end2_inactive_coordinates, self.end2_coordinates
        self.next_segment, self.next_segment_inactive = self.next_segment_inactive, self.next_segment
        self.recompute_heading() # needs to be called because end2 is changed, so we need to recalculate movement vector

    def recompute_heading(self):
        super().recompute_heading()
        # besides the parent function which calculates coordinates and movement vectors, 
        # we need to suplement with coordinates calculation for the switch specific end2_inactive, just for the drawing of it:
        end_coordinates_map = {
            'L': (self.x - self.size//2, self.y),
            'R': (self.x + self.size//2, self.y),
            'U': (self.x, self.y - self.size//2),
            'D': (self.x, self.y + self.size//2),
            None: (None, None)
        }
        self.end2_inactive_coordinates = end_coordinates_map[self._end2_inactive]


    def draw(self, screen):
        # Draw both paths, make the inactive one dimmer
        pygame.draw.line(screen, self.color, self.end1_coordinates, self.end2_coordinates, 3)
        pygame.draw.line(screen, pygame.Color(100, 100, 100), self.end1_coordinates, self.end2_inactive_coordinates, 3)
        
        # Draw a circle at the center of the switch
        pygame.draw.circle(screen, pygame.Color("gray"), (self.x, self.y), self.size // 3, 5)
        # small yellow circle to easily see end2:
        pygame.draw.circle(screen, pygame.Color("yellow"), (self.end2_coordinates[0]*0.8+self.x*0.2 , self.end2_coordinates[1]*0.8+self.y*0.2), 5)
        super().draw(screen)