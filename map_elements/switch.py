import pygame
from .map_element import Map_element
from game_config import *

class Switch(Map_element):
    # this has 2 additional attributes, end2_inactive and next_segment_inactive. They are the alternative way the switch can connect if toggled, 
    #     case in which end2/end2_inactive and next_segment/next_segment_inactive will switch places.
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._end2_inactive = None
        self.next_segment_inactive = None
        # below endings coordinates are actual X and Y computed based on L/R/U/D values of end1 and end2 and end2_inactive:
        self.end1_coordinates = None
        self.end2_coordinates = None
        self.end2_inactive_coordinates = None
        self.recompute_end_coordinates() 

    @property
    def end1(self): return self._end1
    @property
    def end2(self): return self._end2
    @property
    def end2_inactive(self): return self._end2_inactive

    @end1.setter
    def end1(self, value): 
        self._end1 = value
        self.recompute_end_coordinates()
        
    @end2.setter
    def end2(self, value): 
        self._end2 = value
        self.recompute_end_coordinates()

    @end2_inactive.setter
    def end2_inactive(self, value): 
        self._end2_inactive = value
        self.recompute_end_coordinates()

    def toggle(self):
        # Switch between the two possible mobile ends
        self._end2, self._end2_inactive = self._end2_inactive, self._end2
        self.recompute_end_coordinates() 
        self.next_segment, self.next_segment_inactive = self.next_segment_inactive, self.next_segment

        # Redundant check/relink next segment
        # if self.next_segment and self.next_segment.previous_segment: self.next_segment.previous_segment = self
    def recompute_end_coordinates(self):
        end_coordinates_map = {
            'L': (self.x - self.size//2, self.y),
            'R': (self.x + self.size//2, self.y),
            'U': (self.x, self.y - self.size//2),
            'D': (self.x, self.y + self.size//2),
            None: (None, None)
        }
        
        self.end1_coordinates = end_coordinates_map[self._end1]
        self.end2_coordinates = end_coordinates_map[self._end2]
        self.end2_inactive_coordinates = end_coordinates_map[self._end2_inactive]
   

    def draw(self, screen):
        # Draw both paths, make the inactive one dimmer
        pygame.draw.line(screen, self.color, self.end1_coordinates, self.end2_coordinates, 3)
        pygame.draw.line(screen, pygame.Color(100, 100, 100), self.end1_coordinates, self.end2_inactive_coordinates, 3)
        
        # Draw a circle at the center of the switch
        pygame.draw.circle(screen, pygame.Color("gray"), (self.x, self.y), self.size // 3, 5)
        # small yellow circle to easily see end2:
        pygame.draw.circle(screen, pygame.Color("yellow"), (self.end2_coordinates[0]*0.8+self.x*0.2 , self.end2_coordinates[1]*0.8+self.y*0.2), 5)
