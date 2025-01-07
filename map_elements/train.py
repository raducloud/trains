import pygame
from .map_element import Map_element
from game_config import *

class Train(Map_element):
    
    def __init__(self, x, y, color, current_tile:Map_element, train_status = Train_status.IN_BASE):
        super().__init__(x=x, y=y, color=color)
        self.train_status = train_status
        self.current_tile = current_tile
        self.previous_tile = None

    def advance(self):
        # {'L':'R', 'R':'L', 'U':'D', 'D':'U', None:None}[self.current_tile.]
        self.x +=   self.x + self.current_tile.end2_coordinate

    def draw_simple(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size//3)
        
    
    def draw_complex(self, screen):
        pygame.draw.rect(screen, self.color, # Draw main body (rectangle)
                        (self.x - self.size//2,
                         self.y - self.size//4,
                         self.size,
                         self.size//2))
        pygame.draw.rect(screen, self.color, # Draw cabin (smaller rectangle)
                        (self.x - self.size//2,
                         self.y - self.size//2,
                         self.size//2,
                         self.size//4))
        wheel_radius = self.size//8 # Draw wheels (circles)
        pygame.draw.circle(screen, self.color,
                          (self.x - self.size//4, self.y + self.size//4),
                          wheel_radius)
        pygame.draw.circle(screen, self.color,
                          (self.x + self.size//4, self.y + self.size//4),
                          wheel_radius)
        

    def draw(self, screen):
        self.draw_simple(screen)
    
