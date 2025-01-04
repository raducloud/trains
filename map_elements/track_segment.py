import pygame
from .map_element import Map_element
from game_config import *

class Track_segment(Map_element):

    def draw(self, screen):
       
        points_map = {  # points where the track can connect - left, right, up or down
            'L': (self.x - self.size//2, self.y),
            'R': (self.x + self.size//2, self.y),
            'U': (self.x, self.y - self.size//2),
            'D': (self.x, self.y + self.size//2)
        }
        
        start_point = points_map[self._end1]
        end_point = points_map[self._end2]
        
        pygame.draw.line(screen, self.color, start_point, end_point, 3)  # later we can make a curve instead
        pygame.draw.circle(screen, pygame.Color("red"), (end_point[0]*0.8+self.x*0.2 , end_point[1]*0.8+self.y*0.2), 5)

