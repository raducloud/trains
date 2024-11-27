from abc import ABC, abstractmethod
import pygame
import random
import math
from enum import Enum
from typing import List, Tuple, Dict
import time

class Map_element(ABC):
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    @abstractmethod
    def draw(self, screen):
       pass

class Station(Map_element):
    # def __init__(self, x, y):
    #     super().__init__(x, y)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.width//2, 
                         self.y - self.height//2,
                         self.width, self.height))
        # Draw little roof triangle
        points = [(self.x - self.width//2, self.y - self.height//2),
                 (self.x + self.width//2, self.y - self.height//2),
                 (self.x, self.y - self.height//2 - 20)]
        pygame.draw.polygon(screen, self.color, points)

class Game:

    MAP_WIDTH = 10
    MAP_HEIGHT = 10

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 900
    FPS = 60
    # Colors
    BACKGROUND_COLOR = (34, 89, 34)
    TRACK_COLOR = (64, 64, 64)
    SWITCH_COLOR = (144, 238, 144)

    def __init__(self):
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.map_elements = [[None for x in range(self.MAP_WIDTH)] for y in range(self.MAP_HEIGHT)]

        pygame.display.set_caption("Train Routing Puzzle")
        self.clock = pygame.time.Clock()
        
        # Colors for trains and stations
        self.colors = {
            "red": (255, 0, 0),
            "blue": (0, 0, 255),
            "green": (0, 255, 0),
            "yellow": (255, 255, 0),
            "purple": (255, 0, 255),
            "black": (0, 0, 0)
        }
        
        self.train_spawn_interval = 5  # seconds

