import pygame
from .map_element import Map_element
from game_config import *

class Station(Map_element):
    
    def draw(self, screen):
        
        station_scale_factor = self.scale_factor * 0.8 # specific factor for the below drawing which is bigg
        
        pygame.draw.rect(screen, self.color, 
                        (int(self.x - self.size/2 * station_scale_factor), 
                         int(self.y - self.size/2 * station_scale_factor),
                         int(self.size * station_scale_factor), int(self.size * station_scale_factor)))
        # Draw little roof triangle
        points = [(self.x - int(self.size/2 * station_scale_factor), int(self.y - self.size/2 * station_scale_factor)),
                 (self.x + int(self.size/2 * station_scale_factor), int(self.y - self.size/2 * station_scale_factor)),
                 (self.x, self.y - int(self.size * station_scale_factor))]
        pygame.draw.polygon(screen, self.color, points)
        super().draw(screen)

