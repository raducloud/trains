import pygame
from .map_element import Map_element
from game_config import *

class Base_station(Map_element): # a black square - like a tunnel hole from which all trains appear
    
    def __init__(self,x,y):
        Map_element.__init__(self, x, y, color=pygame.Color('black'))
        self.base_x_corner = self.x - int(self.size/2 * self.scale_factor)
        self.base_y_corner = self.y - int(self.size/2 * self.scale_factor)
        self.base_width = int(self.size * self.scale_factor)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, 
                        (self.base_x_corner, 
                         self.base_y_corner,
                         self.base_width, self.base_width))
        super().draw(screen)

