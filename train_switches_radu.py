import pygame
import random
import math
from enum import Enum
from typing import List, Tuple, Dict
import time

MAP_WIDTH = 10
MAP_HEIGHT = 10
ELEMENT_SIZE = 50
BUTTON_WIDTH = 80
BUTTON_HEIGHT = 40
BUTTON_MARGIN = 10
WINDOW_WIDTH = MAP_WIDTH * ELEMENT_SIZE
WINDOW_HEIGHT = MAP_HEIGHT * ELEMENT_SIZE+BUTTON_HEIGHT + BUTTON_MARGIN * 2
BACKGROUND_COLOR = (34, 89, 34)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (180, 180, 180)
BUTTON_SELECTED_COLOR = (150, 150, 150)
BUTTON_TEXT_COLOR = (0, 0, 0)
FPS = 60
TRAIN_SPAWN_INTERVAL = 5  # seconds
FONT = None

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.is_selected = False

    def draw(self, surface):
        color = BUTTON_SELECTED_COLOR if self.is_selected else BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)  # border
        text_surface = FONT.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos) # True only if the click was on this button

class ToggleButton(Button):
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_selected = not self.is_selected
                return True
        return super().handle_event(event)

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

    def __init__(self):

        pygame.init()
        self.clock = pygame.time.Clock()
        global FONT
        FONT = pygame.font.Font(None, 20)
        pygame.display.set_caption("Train Routing Puzzle")
        self.map_elements = [[None for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        toolbar_y = MAP_HEIGHT * ELEMENT_SIZE + 10
        self.station_button = ToggleButton(BUTTON_MARGIN, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Station")
        self.track_button = ToggleButton(BUTTON_MARGIN * 2 + BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Track")
        self.start_button = Button(WINDOW_WIDTH - BUTTON_MARGIN * 2 - BUTTON_WIDTH * 2, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Start")
        self.clear_button = Button(WINDOW_WIDTH - BUTTON_MARGIN - BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Clear")
        self.buttons = [self.station_button, self.track_button,self.start_button, self.clear_button]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
    
            for button in self.buttons:
                if button.handle_event(event):
                    if button == self.station_button and button.is_selected:
                        self.track_button.is_selected = False
                        self.current_tool = 'station'
                    elif button == self.track_button and button.is_selected:
                        self.station_button.is_selected = False
                        self.current_tool = 'track'
                    elif button == self.start_button:
                        print('self.start_game()')
                    elif button == self.clear_button:
                        print('self.clear_map()')
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x,y=mouse_pos
                if x <= MAP_WIDTH*ELEMENT_SIZE and y <= MAP_HEIGHT*ELEMENT_SIZE:
                    self.map_elements[(x-1)//ELEMENT_SIZE][(y-1)//ELEMENT_SIZE]=Track_segment(x, y, 'L', 'U', ELEMENT_SIZE)
                    #self.map_elements[map_x//element_size][map_y//element_size]=Track_segment(map_x, map_y, 'L', 'U', element_size)
                        
        return True

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw grid lines
        for x in range(0, MAP_WIDTH*ELEMENT_SIZE+1, ELEMENT_SIZE):
            pygame.draw.line(self.screen, pygame.Color('black'), (x, 0), (x, MAP_HEIGHT*ELEMENT_SIZE), 1)
        for y in range(0, MAP_WIDTH*ELEMENT_SIZE+1, ELEMENT_SIZE):
            pygame.draw.line(self.screen, pygame.Color('black'), (0, y), (MAP_WIDTH*ELEMENT_SIZE, y), 1)

        for row in self.map_elements:
            for element in row:
                if element is not None:
                    element.draw(self.screen)
        
        for button in self.buttons:
            button.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            # self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
    