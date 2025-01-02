import pygame
from .map_element import Map_element
from trains_config import *

class Switch(Map_element):
    # this has 2 additional attributes, end2_inactive and next_segment_inactive. They are the alternative way the switch can connect if toggled, 
    #     case in which end2/end2_inactive and next_segment/next_segment_inactive will switch places.
    def __init__(self, x, y, 
                 end1:str=None, end2:str=None, end2_inactive:str=None, 
                 previous_segment=None, next_segment=None, next_segment_inactive=None, 
                 color=pygame.Color('white'), size=ELEMENT_SIZE):
        super().__init__(x, y, end1, end2, previous_segment, next_segment, color, size)
        self.end2_inactive = end2_inactive
        self.next_segment_inactive = next_segment_inactive

    def toggle(self):
        # Switch between the two possible mobile ends
        self.end2, self.end2_inactive = self.end2_inactive, self.end2
        
        self.next_segment, self.next_segment_inactive = self.next_segment_inactive, self.next_segment

        # Redundant check/relink next segment
        # if self.next_segment and self.next_segment.previous_segment: self.next_segment.previous_segment = self

    def draw(self, screen):
        points_map = {
            'L': (self.x - self.size//2, self.y),
            'R': (self.x + self.size//2, self.y),
            'U': (self.x, self.y - self.size//2),
            'D': (self.x, self.y + self.size//2)
        }
        
        # Draw both paths, make the inactive one dimmer
        pygame.draw.line(screen, self.color, points_map[self.end1], points_map[self.end2], 3)
        pygame.draw.line(screen, pygame.Color(100, 100, 100), points_map[self.end1], points_map[self.end2_inactive], 3)
        
        # Draw a hollow circle at the center of the switch
        circle_radius = self.size // 3
        pygame.draw.circle(screen, pygame.Color("gray"), (self.x, self.y), circle_radius)
        pygame.draw.circle(screen, pygame.Color("yellow"), (points_map[self.end2][0]*0.8+self.x*0.2 , points_map[self.end2][1]*0.8+self.y*0.2), 5)
