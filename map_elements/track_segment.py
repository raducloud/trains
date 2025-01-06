import pygame

from .map_element import Map_element
from game_config import *

class Track_segment(Map_element):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recompute_end_coordinates() # end coordinates are actual X and Y computed based on L/R/U/D values of end1 and end2
        
    @property
    def end1(self): return self._end1
    @property
    def end2(self): return self._end2

    @end1.setter
    def end1(self, value): 
        self._end1 = value
        self.recompute_end_coordinates()
        
    @end2.setter
    def end2(self, value): 
        self._end2 = value
        self.recompute_end_coordinates()
    
    def recompute_end_coordinates(self):
        point_coordinates_map = {  # coordinates of points where the track can connect - left, right, up or down
            'L': (self.x - self.size//2, self.y),
            'R': (self.x + self.size//2, self.y),
            'U': (self.x, self.y - self.size//2),
            'D': (self.x, self.y + self.size//2),
            None: (None, None)
        }
        
        self.start_coordinates = point_coordinates_map[self._end1]
        self.end_coordinates = point_coordinates_map[self._end2]
    
    def draw(self, screen):
        
        pygame.draw.line(screen, self.color, self.start_coordinates, self.end_coordinates, 3)  # later we can make a curve instead
        pygame.draw.circle(screen, pygame.Color("red"), (self.end_coordinates[0]*0.8+self.x*0.2 , self.end_coordinates[1]*0.8+self.y*0.2), 5)

