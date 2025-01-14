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
    def x(self): 
        return int(self._x_float)
    @property
    def y(self): 
        return int(self._y_float)

    @x.setter
    def x(self, value): 
        self._x_float = float(value)
        
    @y.setter
    def y(self, value): 
        self._y_float = float(value)


    def advance(self) -> int:  # returns +1 if the train arrived in home station, -1 if in the wrong station, 0 otherwise

        score_point = 0
        
        dx = self.current_tile.versor_x * TRAIN_SPEED
        dy = self.current_tile.versor_y * TRAIN_SPEED

        if (abs(dx) > 0 or abs(dy) > 0):
            # check if a new move would lead us outside the tile:
            if (abs(self._x_float - self.current_tile.end2_coordinates[0]) >= abs(dx)  and 
                abs(self._y_float - self.current_tile.end2_coordinates[1]) >= abs(dy)):
                self._x_float += dx
                self._y_float += dy
            else: # a new move would lead us outside the tile, so switch to next tile if it exists:
                if self.current_tile.next_segment:
                    self.current_tile = self.current_tile.next_segment
                    if isinstance(self.current_tile, Station): 
                        if self.current_tile.color == self.color:
                            self.train_status = Train_status.IN_HOME_STATION
                            score_point = 1
                        else:
                            self.train_status = Train_status.IN_WRONG_STATION
                            score_point = -1
                    else: # next segment exists and is not Station, so move at the beginning of it:
                        self._x_float = float(self.current_tile.end1_coordinates[0])
                        self._y_float = float(self.current_tile.end1_coordinates[1])
                else: # no next segment exists:
                    self.train_status = Train_status.STRANDED
        else: # dx and dy are both 0, probably because the base station is unconnected, or an unexpected call of this function:
            self.train_status = Train_status.STRANDED

        return score_point        


    def draw_simple(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size//3)
        
    
    def draw_complex(self, screen):
        pygame.draw.rect(screen, self.color, # Draw main body (rectangle)
                        (self.x - self.size//2, # left
                         self.y - self.size//4, # top
                         self.size, # width
                         self.size//3)) # height
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
        self.draw_complex(screen)
    
