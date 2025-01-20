import pygame
import math
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
        
        try:
            # Load base image (should be white/grayscale)
            self.original_image = pygame.image.load("assets/train.png").convert_alpha()
            # Scale the image
            self.original_image = pygame.transform.scale(self.original_image, (self.size, self.size))
            # Apply color tint
            self.original_image = self._apply_color_tint(self.original_image, self.color)
            self.image = self.original_image
        except pygame.error:
            print("Warning: Could not load train image. Falling back to simple drawing.")
            self.original_image = None
            self.image = None

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

    def _get_angle_from_versors(self):
        # Calculate angle in degrees from versors
        # arctan2 returns angle in radians, convert to degrees
        # Subtract 90 because pygame's rotation assumes 0° points upward
        angle = math.degrees(math.atan2(self.current_tile.versor_y, 
                                      self.current_tile.versor_x))
        return angle

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
        # Main circle (marble-like)
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size//3)
        # Shine effect (small white circle in upper-left)
        shine_offset = self.size//8
        pygame.draw.circle(screen, (255, 255, 255), 
                         (self.x - shine_offset, self.y - shine_offset), 
                         self.size//8)
        
    
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
        if self.image:
            # Rotate image based on movement direction
            angle = self._get_angle_from_versors()
            self.image = pygame.transform.rotate(self.original_image, angle)
            # Calculate position to center the image on the train's coordinates
            image_rect = self.image.get_rect(center=(self.x, self.y))
            screen.blit(self.image, image_rect)
        else:
            # Fallback to simple drawing if image loading failed
            self.draw_simple(screen)

    def _apply_color_tint(self, surface, color):
        # Create a copy of the original surface
        tinted = surface.copy()
        
        # Create a color overlay
        overlay = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        overlay.fill(color)
        
        # Blend the overlay with the original image, preserving alpha
        for x in range(tinted.get_width()):
            for y in range(tinted.get_height()):
                original_color = tinted.get_at((x, y))
                if original_color.a > 0:  # Only tint non-transparent pixels
                    # Calculate new color based on original brightness
                    brightness = (original_color.r + original_color.g + original_color.b) / (3 * 255)
                    new_color = pygame.Color(
                        int(color[0] * brightness),
                        int(color[1] * brightness),
                        int(color[2] * brightness),
                        original_color.a
                    )
                    tinted.set_at((x, y), new_color)
        
        return tinted
    
