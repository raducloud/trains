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
FONT = None # just to define the giobal variable, initialization cannot be done here as it's a bit complicated

# Non-playable elements:
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

    def handle_event(self, event): # by convention, button pressing is signaled by handle_event returning True
        if self.is_enabled:
            if event.type == pygame.MOUSEMOTION:
                self.is_hovered = self.rect.collidepoint(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return self.rect.collidepoint(event.pos) # True only if the click was on this game button

class ToggleButton(Button):
    def handle_event(self, event): # returning True = button pressed
        if self.is_enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.is_selected = not self.is_selected
            return True
        return super().handle_event(event)

#playable elements:
class Map_element:

    def __init__(self, x, y, color=pygame.Color('white'), size=ELEMENT_SIZE):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, screen):
       pass # abstract function

class Station(Map_element):
    
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

class Base_station(Map_element): # a black square - like a tunnel hole from which all trains appear
    
    def __init__(self,x,y):
        Map_element.__init__(self, x, y, color=pygame.Color('black'));

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, 
                        (self.x - self.size//2, 
                         self.y - self.size//2,
                         self.size, self.size))

class Train(Map_element):
    
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
        
class Track_segment(Map_element):
    def __init__(self, x:int, y:int, end1:str=None, end2:str=None, previous_segment=None, next_segment=None, color=pygame.Color('white'), size=ELEMENT_SIZE):
        Map_element.__init__(self, x, y, color=color, size=size);
        self.end1=end1
        self.end2=end2
        self.previous_segment=previous_segment
        self.next_segment=next_segment

    def draw(self, screen):
       
        points = {  # points where the track can connect - left, right, up or down
            'L': (self.x - self.size//2, self.y),
            'R': (self.x + self.size//2, self.y),
            'U': (self.x, self.y - self.size//2),
            'D': (self.x, self.y + self.size//2)
        }
        
        start_point = points[self.end1]
        end_point = points[self.end2]
        
        pygame.draw.line(screen, self.color, start_point, end_point, 3)  # later we can make a curve instead

class Game: # Game mechanics, will have only 1 instance

    def __init__(self):

        pygame.init()
        pygame.display.set_caption("Train Routing Puzzle")
        self.clock = pygame.time.Clock()
        global FONT
        FONT = pygame.font.Font(None, 20)
        #map-related:
        self.base_station = Base_station(0,0) # however we don't put in map_elements here in init; so it will not be part of the map till the user places it
        self.stations = []
        self.base_station_tile_position = (-1,-1) # -1 means "doesn't exist"
        self.map_elements = [[None for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]
        # tracking track placement:
        self.is_dragging_track = False
        self.previous_track_tile_position = None
        self.current_track_chain = []  # Store connected track segments while dragging
        #others:
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        toolbar_y = MAP_HEIGHT * ELEMENT_SIZE + 10
        self.base_station_button = ToggleButton(BUTTON_MARGIN, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Base")
        self.station_button = ToggleButton(BUTTON_MARGIN * 2 + BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Station")
        self.track_button = ToggleButton(BUTTON_MARGIN * 3 + BUTTON_WIDTH * 2, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Track")
        self.start_button = Button(WINDOW_WIDTH - BUTTON_MARGIN * 2 - BUTTON_WIDTH * 2, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Start")
        self.clear_button = Button(WINDOW_WIDTH - BUTTON_MARGIN - BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Clear")
        self.clear_button.is_enabled = False
        self.buttons = [self.base_station_button, self.station_button, self.track_button,self.start_button, self.clear_button]
   
    def scan_neighbors(self, map_tile_x:int, map_tile_y:int) -> Tuple[str, Map_element]:
         # Returns the first neighbor element found and it's position in format l/R/U/D.
         # Since it is mostly useful for laying and detecting track segments, it first scans for track segments:
        left_buddy = right_buddy = up_buddy = down_buddy = None
        if map_tile_x > 0 : left_buddy = self.map_elements[map_tile_x-1][map_tile_y]
        if map_tile_x < MAP_WIDTH - 1 : right_buddy = self.map_elements[map_tile_x+1][map_tile_y]
        if map_tile_y > 0 : up_buddy = self.map_elements[map_tile_x][map_tile_y-1]
        if map_tile_y < MAP_WIDTH - 1 : down_buddy = self.map_elements[map_tile_x][map_tile_y+1]
        
        neighbors = {'L':left_buddy, 'R':right_buddy, 'U':up_buddy, 'D':down_buddy}

        for relative_position, buddy in neighbors.items():
            if isinstance(buddy, Track_segment): return (relative_position, buddy);
        for relative_position, buddy in neighbors.items():
            if isinstance(buddy, Base_station): return (relative_position, buddy);
        for relative_position, buddy in neighbors.items():
            if isinstance(buddy, Station): return (relative_position, buddy);
        return None # nothing found

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
                    map_prepvious_x = (x-1)//ELEMENT_SIZE*ELEMENT_SIZE+ELEMENT_SIZE//2
                    map_previous_y = (y-1)//ELEMENT_SIZE*ELEMENT_SIZE+ELEMENT_SIZE//2



                    if self.station_button.is_selected:
                        new_color = random.choice([color for color in ELEMENT_POSSIBLE_COLORS if color not in [station.color for station in self.stations]]) # chose a color not previously used
                        new_station = Station(map_prepvious_x,map_previous_y,new_color)
                        self.stations.append(new_station)
                        if len(self.stations) == len(ELEMENT_POSSIBLE_COLORS):
                            Tk().wm_withdraw() # draw back the main window for showing pop-up
                            messagebox.showinfo('Info',"This is the last station available")
                            self.station_button.is_enabled = False
                            self.station_button.is_selected = False
                        if self.map_elements[map_tile_x][map_tile_y] == self.base_station: # Base station overwritten
                            self.base_station_tile_position = (-1,-1)
                        if self.map_elements[map_tile_x][map_tile_y] in self.stations: # Previous station overwritten:
                            self.stations.remove(self.map_elements[map_tile_x][map_tile_y])
                        self.map_elements[map_tile_x][map_tile_y]=new_station



                    if self.base_station_button.is_selected:
                        self.base_station=Base_station(map_prepvious_x,map_previous_y)
                        if (self.base_station_tile_position != (-1,-1)):  # if the base station already existed, clear it from its old place - there can be only one:
                            self.map_elements[self.base_station_tile_position[0]][self.base_station_tile_position[1]] = None
                        if self.map_elements[map_tile_x][map_tile_y] in self.stations: # Previous station overwritten:
                            self.stations.remove(self.map_elements[map_tile_x][map_tile_y])
                            self.station_button.is_enabled = True # in case it had been disabled out of lack of stations
                        self.map_elements[map_tile_x][map_tile_y]=self.base_station
                        self.base_station_tile_position = (map_tile_x, map_tile_y)



            # Handle track placement by dragging:
            if self.track_button.is_selected:
                
                if event.type == pygame.MOUSEBUTTONDOWN: #first segment in a chain. 
                    x, y = pygame.mouse.get_pos()
                    if x <= MAP_WIDTH*ELEMENT_SIZE and y <= MAP_HEIGHT*ELEMENT_SIZE:
                        self.is_dragging_track = True
                        
                        current_tile = ((x-1)//ELEMENT_SIZE, (y-1)//ELEMENT_SIZE)
                        current_tile_x, current_tile_y = current_tile
                        neighbor_info = self.scan_neighbors(current_tile_x, current_tile_y)  #scan for tracks or stations nearby:
                        if neighbor_info:
                            neighbor_relative_position, neighbor = neighbor_info
                            current_end1 = neighbor_relative_position
                            current_end2 = {'L':'R', 'R':'L', 'U':'D', 'D':'U'}.get(current_end1)  # make end2 the opposite of end1 for now, of course might be overwritten later
                        else: # No neighbors, put some defaults:
                            neighbor=None
                            current_end1='L' #defauot
                            current_end2='R' #default
                        current_track_segment = Track_segment(current_tile_x * ELEMENT_SIZE + ELEMENT_SIZE//2, current_tile_y * ELEMENT_SIZE + ELEMENT_SIZE//2, current_end1, current_end2)
                        
                        # if the neighbor if an unfinished track, connect it:
                        if neighbor and isinstance(neighbor, Track_segment) and (not neighbor.next_segment):
                            neighbor.next_segment = current_track_segment
                            neighbor.end2 = current_end2 # we actually need the reverse neighbor_relative_position, which we've already calculated in current_end2, even if current_end2 is just temporary
                            current_track_segment.previous_segment = neighbor 

                        # add the track segment to the map and chain:
                        self.map_elements[current_tile_x][current_tile_y] = current_track_segment
                        self.current_track_chain.append(current_track_segment)
                        #prepare for next iteration:
                        self.previous_track_tile_position = current_tile                            


                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_dragging_track = False
                    self.previous_track_tile_position = None
                    # Here you could finalize the track placement if needed
                    self.current_track_chain = []


                elif event.type == pygame.MOUSEMOTION and self.is_dragging_track:
                    x, y = pygame.mouse.get_pos()
                    if x <= MAP_WIDTH*ELEMENT_SIZE and y <= MAP_HEIGHT*ELEMENT_SIZE:
                        current_tile = ((x-1)//ELEMENT_SIZE, (y-1)//ELEMENT_SIZE)
                        
                        # Only create new track if we've moved to a different tile
                        if current_tile != self.previous_track_tile_position and self.previous_track_tile_position is not None:
                            # Determine track orientation based on movement
                            previous_tile_x, previous_tile_y = self.previous_track_tile_position
                            current_tile_x, current_tile_y = current_tile
                            
                            # Determine track endpoints
                            if current_tile_x > previous_tile_x:
                                previous_ends = ('L', 'R')
                            elif current_tile_x < previous_tile_x:
                                previous_ends = ('R', 'L')
                            elif current_tile_y > previous_tile_y:
                                previous_ends = ('U', 'D')
                            else:
                                previous_ends = ('D', 'U')
                            
                            # Create new track segment
                            map_current_x = current_tile_x * ELEMENT_SIZE + ELEMENT_SIZE//2
                            map_current_y = current_tile_y * ELEMENT_SIZE + ELEMENT_SIZE//2
                            previous_track_segment = Track_segment(map_prepvious_x, map_previous_y, previous_ends[0], previous_ends[1])
                            
                            # Add to map and track chain
                            self.map_elements[previous_tile_x][previous_tile_y] = previous_track_segment
                            self.current_track_chain.append(previous_track_segment)
                            #prepare for next iteration:
                            self.previous_track_tile_position = current_tile

        return True

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw grid lines
        for x in range(0, MAP_WIDTH*ELEMENT_SIZE+1, ELEMENT_SIZE): pygame.draw.line(self.screen, pygame.Color('black'), (x, 0), (x, MAP_HEIGHT*ELEMENT_SIZE), 1)
        for y in range(0, MAP_WIDTH*ELEMENT_SIZE+1, ELEMENT_SIZE): pygame.draw.line(self.screen, pygame.Color('black'), (0, y), (MAP_WIDTH*ELEMENT_SIZE, y), 1)

        for row in self.map_elements:
            for element in row:
                if element is not None:
                    element.draw(self.screen)
        
        for button in self.buttons: button.draw(self.screen)
        
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
    