import random
import pygame
from enum import Enum
from typing import List, Tuple, Dict
from tkinter import *
from tkinter import messagebox

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
BUTTON_DISABLED_TEXT_COLOR = (100, 100, 100)

ELEMENT_POSSIBLE_COLORS = [pygame.Color('red'),
                           pygame.Color('blue'),
                           pygame.Color('yellow'),
                           pygame.Color('green'),
                           pygame.Color('purple'),
                           pygame.Color('orange'),
                           pygame.Color('cyan')]
FPS = 60
TRAIN_SPAWN_INTERVAL = 5  # seconds
FONT = None

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.is_selected = False
        self.is_enabled = True

    def draw(self, surface):
        color = BUTTON_SELECTED_COLOR if self.is_selected else BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)  # border
        text_surface = FONT.render(self.text, True, BUTTON_TEXT_COLOR if self.is_enabled else BUTTON_DISABLED_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if self.is_enabled:
            if event.type == pygame.MOUSEMOTION:
                self.is_hovered = self.rect.collidepoint(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.rect.collidepoint(event.pos) # True only if the click was on this game button

class ToggleButton(Button):
    def handle_event(self, event):
        if self.is_enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_selected = not self.is_selected
                return True
        return super().handle_event(event)

class Game_element:

    def __init__(self, x, y, color=pygame.Color('white'), size=ELEMENT_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, screen):
       pass

class Station(Game_element):
    
    def draw(self, screen):
        scale_factor = 0.8
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.size//2 * scale_factor, 
                         self.y - self.size//2 * scale_factor,
                         self.size * scale_factor, self.size * scale_factor))
        # Draw little roof triangle
        points = [(self.x - self.size//2 * scale_factor, self.y - self.size//2 * scale_factor),
                 (self.x + self.size//2 * scale_factor, self.y - self.size//2 * scale_factor),
                 (self.x, self.y - self.size * scale_factor)]
        pygame.draw.polygon(screen, self.color, points)

class Base_station(Game_element): # a black square - like a tunnel hole from which all trains appear
    
    def __init__(self,x,y):
        Game_element.__init__(self, x, y, color=pygame.Color('black'));

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.size//2, 
                         self.y - self.size//2,
                         self.size, self.size))

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
        pygame.display.set_caption("Train Routing Puzzle")
        self.clock = pygame.time.Clock()
        global FONT
        FONT = pygame.font.Font(None, 20)
        #map:
        self.base_station = Base_station(0,0) # however we don't put in map_elements here in init; so it will not be part of the map till the user places it
        self.stations = []
        self.base_station_position = (-1,-1) # -1 means "doesn't exist"
        self.map_elements = [[None for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        #others:
        toolbar_y = MAP_HEIGHT * ELEMENT_SIZE + 10
        self.base_station_button = ToggleButton(BUTTON_MARGIN, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Base")
        self.station_button = ToggleButton(BUTTON_MARGIN * 2 + BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Station")
        self.track_button = ToggleButton(BUTTON_MARGIN * 3 + BUTTON_WIDTH * 2, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Track")
        self.start_button = Button(WINDOW_WIDTH - BUTTON_MARGIN * 2 - BUTTON_WIDTH * 2, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Start")
        self.clear_button = Button(WINDOW_WIDTH - BUTTON_MARGIN - BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Clear")
        self.clear_button.is_enabled = False
        self.buttons = [self.base_station_button, self.station_button, self.track_button,self.start_button, self.clear_button]

    def set_cursor(self, cursor_type='default'):
        if cursor_type in ['-','\\','|','/']:
            size = 16
            hotspot = (size // 2, size // 2)
            surface = pygame.Surface((size, size), pygame.SRCALPHA)
            surface.fill((0,0,0,0))  # Transparent background
            match cursor_type:
                case '-':  start_pos = (0,size//2); end_pos = (size,size//2)
                case '\\': start_pos = (0,0); end_pos = (size,size)
                case '|': start_pos = (size//2,0); end_pos = (size//2,size)
                case '/': start_pos = (size,0); end_pos = (0,size)
            pygame.draw.line(surface, (255,255,255,255), start_pos, end_pos, width=2)
            cursor_data = pygame.cursors.Cursor((hotspot), surface)
            pygame.mouse.set_cursor(cursor_data)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
    
            #handle clicks on buttons:
            for button in self.buttons:
                if button.handle_event(event): # if button was pressed:
                     # pop all other buttons (they might be toggle buttons)
                    for other_button in self.buttons:
                        if other_button!=button:
                            other_button.is_selected = False
                    # further custom game actions besides the generic ones in button's handle_event:
                    if button == self.track_button:
                            self.set_cursor(cursor_type='-')
                    else:
                            self.set_cursor()
                    match button:
                        case self.start_button:
                            None

            # handle clicks on map area:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                if x <= MAP_WIDTH*ELEMENT_SIZE and y <= MAP_HEIGHT*ELEMENT_SIZE:
                    map_tile_x = (x-1)//ELEMENT_SIZE
                    map_tile_y = (y-1)//ELEMENT_SIZE
                    # click coordinates snapped to map grid (to center of tiles more exactly):
                    map_x = (x-1)//ELEMENT_SIZE*ELEMENT_SIZE+ELEMENT_SIZE//2
                    map_y = (y-1)//ELEMENT_SIZE*ELEMENT_SIZE+ELEMENT_SIZE//2

                    if self.station_button.is_selected:
                        new_color = random.choice([color for color in ELEMENT_POSSIBLE_COLORS if color not in [station.color for station in self.stations]]) # chose a color not previously used
                        new_station = Station(map_x,map_y,new_color)
                        self.stations.append(new_station)
                        if len(self.stations) == len(ELEMENT_POSSIBLE_COLORS):
                            Tk().wm_withdraw() #to hide the main window
                            messagebox.showinfo('Info',"This is the last station available")
                            self.station_button.is_enabled = False
                            self.station_button.is_selected = False
                        if self.map_elements[map_tile_x][map_tile_y] == self.base_station: # Base station overwritten
                            self.base_station_position = (-1,-1)
                        if self.map_elements[map_tile_x][map_tile_y] in self.stations: # Previous station overwritten:
                            self.stations.remove(self.map_elements[map_tile_x][map_tile_y])
                        self.map_elements[map_tile_x][map_tile_y]=new_station

                    if self.base_station_button.is_selected:
                        self.base_station=Base_station(map_x,map_y)
                        if (self.base_station_position != (-1,-1)):  # if the base station already existed, clear it from its old place - there can be only one:
                            self.map_elements[self.base_station_position[0]][self.base_station_position[1]] = None
                        if self.map_elements[map_tile_x][map_tile_y] in self.stations: # Previous station overwritten:
                            self.stations.remove(self.map_elements[map_tile_x][map_tile_y])
                            self.station_button.is_enabled = True # in case it had been disabled out of lack of stations
                        self.map_elements[map_tile_x][map_tile_y]=self.base_station
                        self.base_station_position = (map_tile_x, map_tile_y)
                    # if self.
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
    