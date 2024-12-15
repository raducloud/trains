import pygame
import random
import math
from enum import Enum
from typing import List, Tuple, Dict
import time

class Game_element:

    def __init__(self, x, y, size, color=pygame.Color('white')):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, screen):
       pass

class Station(Game_element):
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.size//2, 
                         self.y - self.size//2,
                         self.size, self.size))
        # Draw little roof triangle
        points = [(self.x - self.size//2, self.y - self.size//2),
                 (self.x + self.size//2, self.y - self.size//2),
                 (self.x, self.y - self.size)]
        pygame.draw.polygon(screen, self.color, points)
class Train(Game_element):
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, # Draw main body (rectangle)
                        (self.x - self.size//2,
                         self.y - self.size//4,
                         self.size,
                         self.size//2))
        pygame.draw.rect(screen, self.color,# Draw cabin (smaller rectangle)
                        (self.x - self.size//2,
                         self.y - self.size//2,
                         self.size//2,
                         self.size//4))
        wheel_radius = self.size//8# Draw wheels (circles)
        pygame.draw.circle(screen, self.color,
                          (self.x - self.size//4, self.y + self.size//4),
                          wheel_radius)
        pygame.draw.circle(screen, self.color,
                          (self.x + self.size//4, self.y + self.size//4),
                          wheel_radius)
        
class Track_segment(Game_element):
    def __init__(self, x, y, end1, end2, size, color=pygame.Color('white')):
        Game_element.__init__(self, x, y, size, color);
        self.end1=end1
        self.end2=end2

    def draw(self, screen):
        # Define the points where the track can connect
        points = {
            'L': (self.x - self.size//2, self.y),
            'R': (self.x + self.size//2, self.y),
            'U': (self.x, self.y - self.size//2),
            'D': (self.x, self.y + self.size//2)
        }
        
        start_point = points[self.end1]
        end_point = points[self.end2]
        
        pygame.draw.line(screen, self.color, start_point, end_point, 3)

class Game:

    MAP_WIDTH = 10
    MAP_HEIGHT = 10
    element_size = 50

    WINDOW_WIDTH = MAP_WIDTH * element_size
    WINDOW_HEIGHT = MAP_HEIGHT * element_size+200
    FPS = 60
    # Colors
    BACKGROUND_COLOR = (34, 89, 34)

    clock = pygame.time.Clock()
    
    train_spawn_interval = 5  # seconds

    def __init__(self):

        self.map_elements = [[None for x in range(Game.MAP_WIDTH)] for y in range(Game.MAP_HEIGHT)]
        self.screen = pygame.display.set_mode((Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT))
        pygame.display.set_caption("Train Routing Puzzle")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x,y=mouse_pos
                # clip to map if clicked outside map:
                #map_x = min(x-1,Game.MAP_WIDTH*self.element_size-1)
                #map_y = min(y-1,Game.MAP_HEIGHT*self.element_size-1)
                print(mouse_pos)
                if x <= Game.MAP_WIDTH*Game.element_size and y <= Game.MAP_HEIGHT*Game.element_size:
                    #print(x//Game.element_size,y//Game.element_size)
                    #print(map_x//Game.element_size,map_y//Game.element_size)
                    self.map_elements[(x-1)//Game.element_size][(y-1)//Game.element_size]=Track_segment(x, y, 'L', 'U', Game.element_size)
                #self.map_elements[map_x//Game.element_size][map_y//Game.element_size]=Track_segment(map_x, map_y, 'L', 'U', Game.element_size)
                        
        return True

    def draw(self):
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Draw grid lines
        for x in range(0, Game.MAP_WIDTH*self.element_size+1, self.element_size):
            pygame.draw.line(self.screen, pygame.Color('black'), (x, 0), (x, Game.MAP_HEIGHT*Game.element_size), 1)
        for y in range(0, Game.MAP_WIDTH*self.element_size+1, self.element_size):
            pygame.draw.line(self.screen, pygame.Color('black'), (0, y), (Game.MAP_WIDTH*Game.element_size, y), 1)

        for row in self.map_elements:
            for element in row:
                if element is not None:
                    element.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            # self.update()
            self.draw()
            self.clock.tick(self.FPS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
    