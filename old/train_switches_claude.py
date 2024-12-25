import pygame
import random
import math
from enum import Enum
from typing import List, Tuple, Dict
import time

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 900
FPS = 60

# Colors
BACKGROUND_COLOR = (34, 89, 34)
TRACK_COLOR = (64, 64, 64)
SWITCH_COLOR = (144, 238, 144)

class Direction(Enum):
    LEFT = 0
    RIGHT = 1

class Switch:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.direction = Direction.LEFT
        self.radius = 20
        
    def toggle(self):
        self.direction = Direction.RIGHT if self.direction == Direction.LEFT else Direction.LEFT
        
    def draw(self, screen):
        pygame.draw.circle(screen, SWITCH_COLOR, (self.x, self.y), self.radius)

class Station:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.width = 40
        self.height = 50
        
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

class Train:
    def __init__(self, color: Tuple[int, int, int], speed: float = 2):
        self.x = 100  # Starting x position
        self.y = 100  # Starting y position
        self.color = color
        self.speed = speed
        self.width = 30
        self.height = 20
        self.current_path = []
        self.path_index = 0
        
    def move(self):
        if self.path_index < len(self.current_path) - 1:
            target_x, target_y = self.current_path[self.path_index + 1]
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < self.speed:
                self.x = target_x
                self.y = target_y
                self.path_index += 1
            else:
                self.x += (dx/distance) * self.speed
                self.y += (dy/distance) * self.speed
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color,
                        (self.x - self.width//2,
                         self.y - self.height//2,
                         self.width, self.height))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
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
        
        self.switches = []
        self.stations = []
        self.trains = []
        self.tracks = []
        
        self.setup_game()
        self.last_train_time = time.time()
        self.train_spawn_interval = 5  # seconds
        
    def setup_game(self):
        # Create switches (binary tree nodes)
        switch_positions = [
            (400, 200),  # Top switch
            (300, 300),  # Second level left
            (500, 300),  # Second level right
            (250, 400),  # Third level far left
            (350, 400),  # Third level middle left
            (450, 400),  # Third level middle right
            (550, 400),  # Third level far right
        ]
        
        for pos in switch_positions:
            self.switches.append(Switch(*pos))
        
        # Create stations
        station_positions = [
            (200, 500, self.colors["yellow"]),
            (300, 500, self.colors["green"]),
            (400, 500, self.colors["blue"]),
            (500, 500, self.colors["black"]),
            (600, 500, self.colors["purple"]),
        ]
        
        for pos in station_positions:
            self.stations.append(Station(*pos))
        
        # Create tracks (connections between switches and stations)
        self.create_tracks()
        
    def create_tracks(self):
        # Create binary tree structure of tracks
        self.tracks = []
        
        # Connect switches in binary tree structure
        for i, switch in enumerate(self.switches):
            left_child_idx = 2 * i + 1
            right_child_idx = 2 * i + 2
            
            if left_child_idx < len(self.switches):
                self.tracks.append((
                    (switch.x, switch.y),
                    (self.switches[left_child_idx].x, self.switches[left_child_idx].y)
                ))
            
            if right_child_idx < len(self.switches):
                self.tracks.append((
                    (switch.x, switch.y),
                    (self.switches[right_child_idx].x, self.switches[right_child_idx].y)
                ))
        
        # Connect bottom level switches to stations
        for i, station in enumerate(self.stations):
            switch_idx = len(self.switches) - len(self.stations) + i
            if switch_idx >= 0 and switch_idx < len(self.switches):
                self.tracks.append((
                    (self.switches[switch_idx].x, self.switches[switch_idx].y),
                    (station.x, station.y)
                ))
    
    def spawn_train(self):
        available_colors = [color for color in self.colors.values()]
        if len(self.trains) < len(available_colors):
            color = random.choice(available_colors)
            while any(train.color == color for train in self.trains):
                color = random.choice(available_colors)
            
            train = Train(color)
            # Set initial position at the top switch
            train.x = self.switches[0].x
            train.y = self.switches[0].y - 50
            self.trains.append(train)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for switch in self.switches:
                    if math.dist((switch.x, switch.y), mouse_pos) < switch.radius:
                        switch.toggle()
                        
        return True
    
    def update(self):
        current_time = time.time()
        if current_time - self.last_train_time > self.train_spawn_interval:
            self.spawn_train()
            self.last_train_time = current_time
            
        for train in self.trains:
            train.move()
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw tracks
        for track in self.tracks:
            pygame.draw.line(self.screen, TRACK_COLOR, track[0], track[1], 5)
        
        # Draw switches
        for switch in self.switches:
            switch.draw(self.screen)
        
        # Draw stations
        for station in self.stations:
            station.draw(self.screen)
        
        # Draw trains
        for train in self.trains:
            train.draw(self.screen)
        
        pygame.display.flip()
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
    