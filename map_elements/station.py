import pygame
from .map_element import Map_element
from trains_config import *

class Station(Map_element):
    
    def draw(self, screen):
        scale_factor = 0.8
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.size//2 * scale_factor, 
                         self.y - self.size//2 * scale_factor,
                         self.size * scale_factor, self.size * scale_factor))
        # Draw little roof triangle
        points = [(self.x - self.size//2 * scale_factor, self.y - self.size//2 * scale_factor),
                 (self.x + self.size//2 * scale_factor, self.y - self.size//2 * scale_factor),
                 (self.x, self.y - self.size * scale_factor)]
        pygame.draw.polygon(screen, self.color, points)

