import pygame
from map_elements import *
from game_config import *

class Train(Map_element):
    
    def __init__(self, x, y, color, current_tile:Map_element, train_status = Train_status.IN_BASE):
        self.train_status = train_status
        self.current_tile = current_tile
        self.previous_tile = None
        # for smooth movement and sub-pixel movement in case of small speeds:
        self._x_float = float(x)
        self._y_float = float(y)
        super().__init__(x=x, y=y, color=color)

        @property
        def x(self): return int(self._x_float)
        @property
        def y(self): return int(self._y_float)

        @x.setter
        def x(self, value): 
            self._x_float = float(value)
            
        @y.setter
        def y(self, value): 
            self._y_float = float(value)


    def advance(self):
        dx = int(self.current_tile.versor_x * TRAIN_SPEED)
        dy = int(self.current_tile.versor_y * TRAIN_SPEED)

        # check if a new move would lead us outside the tile:
        if (abs(self.x - self.current_tile.end2_coordinates[0]) >= abs(dx)  and 
            abs(self.y - self.current_tile.end2_coordinates[1]) >= abs(dy)):
            self.x += dx
            self.y += dy
        else: # a new move would lead us outside the tile, so switch to next tile if it exists:
            if self.current_tile.next_segment:
                self.current_tile = self.current_tile.next_segment
                if isinstance(self.current_tile, Station): 
                    if self.current_tile.color == self.color:
                        self.train_status = Train_status.IN_HOME_STATION
                    else:
                        self.train_status = Train_status.IN_WRONG_STATION
                else: # next segment exists and is not Station, so move at the beginning of it:
                    self.x = self.current_tile.end1_coordinates[0]
                    self.y = self.current_tile.end1_coordinates[1]
            else: # no next segment exists:
                self.train_status = Train_status.STRANDED

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
    
