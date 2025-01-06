import pygame
from .map_element import Map_element
from game_config import *

class Train(Map_element):
    
    def __init___(self, x, y, color, current_tile:Map_element):
        super().__init__(self, x=x, y=y, color=color)
        self.status = Train_status.IN_BASE
        self.current_tile = current_tile
        self.previous_tile = None

    def advance():
        # {'L':'R', 'R':'L', 'U':'D', 'D':'U', None:None}[self.current_tile.]
        pass

    def draw_simple(self,screen):
        pygame.draw.circle(screen, self.color, self.x-self.size//2, self.x-self.size//3)
        
    
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
        

    def draw(self,screen):
        if self.status == Train_status.EN_ROUTE:
            draw_simple(self,screen)
    
