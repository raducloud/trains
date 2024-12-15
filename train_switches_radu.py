import pygame
import random
import math
from enum import Enum
from typing import List, Tuple, Dict
import time

class Map_element:

    def __init__(self, x, y, size, color=pygame.Color('white')):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, screen):
       pass

class Station(Map_element):
    
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

class Game:

    MAP_WIDTH = 10
    MAP_HEIGHT = 10
    element_size = 50

    WINDOW_WIDTH = MAP_WIDTH * element_size
    WINDOW_HEIGHT = MAP_HEIGHT * element_size
    FPS = 60
    # Colors
    BACKGROUND_COLOR = (34, 89, 34)
    TRACK_COLOR = (64, 64, 64)
    SWITCH_COLOR = (144, 238, 144)

    clock = pygame.time.Clock()
    
    # Colors for trains and stations
    colors = {
        "red": (255, 0, 0),
        "blue": (0, 0, 255),
        "green": (0, 255, 0),
        "yellow": (255, 255, 0),
        "purple": (255, 0, 255),
        "black": (0, 0, 0)
    }
    
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
                print(x//Game.element_size,y//Game.element_size)
                self.map_elements[x//Game.element_size][y//Game.element_size]=Station(x, y, Game.element_size)
                        
        return True

    def draw(self):
        self.screen.fill(self.BACKGROUND_COLOR)
        
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
    