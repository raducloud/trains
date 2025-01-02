import pygame
from .map_element import Map_element
from trains_config import *

class Base_station(Map_element): # a black square - like a tunnel hole from which all trains appear
    
    def __init__(self,x,y):
        Map_element.__init__(self, x, y, color=pygame.Color('black'));

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.size//2, 
                         self.y - self.size//2,
                         self.size, self.size))

