import pygame

from .map_element import Map_element
from game_config import *

class Track_segment(Map_element):

    def draw(self, screen):
        
        pygame.draw.line(screen, self.color, self.end1_coordinates, self.end2_coordinates, 3)  # later we can make a curve instead
        pygame.draw.circle(screen, pygame.Color("red"), (self.end2_coordinates[0]*0.8+self.x*0.2 , self.end2_coordinates[1]*0.8+self.y*0.2), 5)
        super().draw(screen)
