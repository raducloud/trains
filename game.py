import random
import pygame
from enum import Enum, auto
from typing import List, Tuple, Dict
from tkinter import Tk, messagebox
from trains_config import *
from trains_utils import *
from trains_ui import *
from map_elements import *

# This is a game of routing colored trains to stations of same color.
# The trains advance by themselves at constant speeds, all originating at the single base station form which they spawn at some time intervals and following tracks.
# What the player does is act on some switches which are placed at track intersections,
#     each switch having one fixed end and one mobile end, the mobile end can be switched between 2 positions by the user click/touch.
# If the player manages to direct a train to the station with the same color as the train, they receieve a point.

class Game_state(Enum):
    SETUP = auto()
    RUNNING = auto()
    PAUSED = auto()
    OVER = auto()

class Game: # Game mechanics, will have only 1 instance

    def __init__(self):

        pygame.init()
        pygame.display.set_caption("Train Routing Puzzle")
        self.clock = pygame.time.Clock()

        # map-related:
        self.map_elements = [[None for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]
        self.base_station = None
        self.base_station_tile_position = (-1,-1) # -1 means "doesn't exist"
        self.stations = []
        self.trains = []
        self.colors = [] # all colors used after all stations have been placed
        # map state:
        self.trains_en_route = 0
        self.trains_at_destination = 0
        self.time_since_last_train_spawn = -1

        # tracking track/switch placement:
        self.is_dragging_track = False
        self.previous_track_tile_position = None
        self.current_track_chain = []  # Store connected track segments while dragging
        self.current_tile_x = None
        self.current_tile_y = None
        # click coordinates snapped to map grid (to center of tiles more exactly):
        self.map_x = None
        self.map_y = None
        self.clicked_element = None

        # Others:
        # elements:
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        toolbar_y = MAP_HEIGHT * ELEMENT_SIZE + 10
        self.base_station_button = ToggleButton(BUTTON_MARGIN, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Base")
        self.station_button = ToggleButton(BUTTON_MARGIN * 2 + BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Station")
        self.track_button = ToggleButton(BUTTON_MARGIN * 3 + BUTTON_WIDTH * 2, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Track")
        self.switch_button = ToggleButton(BUTTON_MARGIN * 4 + BUTTON_WIDTH * 3, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Switch")
        self.start_button = Button(WINDOW_WIDTH - BUTTON_MARGIN - BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Start")
        self.palette_buttons = [self.base_station_button, self.station_button, self.track_button, self.switch_button]
        self.control_buttons = [self.start_button]
        #state:
        self.game_state = Game_state.SETUP

    def get_neighbor(self, map_tile_x:int, map_tile_y:int, direction:str, exclude:list=[]) -> Tuple[str, Map_element]:
         # Returns the first unconnected neighbor element found and its relative position in format l/R/U/D.
         # It is useful during laying track/switch chains, for connecting0
         # direction parameter should be "upstraem" or "downstream".
         # exclude parameter is used for cases like a neighbor being able to connect both to UPSTREAM and DOWNSTREAM, to not create an infinite cycle, exclude it at second search

        neighbors = {}
        if map_tile_x > 0 : 
            neighbor = self.map_elements[map_tile_x-1][map_tile_y]
            if neighbor: neighbors['L']=neighbor
        if map_tile_x < MAP_WIDTH - 1 : 
            neighbor = self.map_elements[map_tile_x+1][map_tile_y]
            if neighbor: neighbors['R']=neighbor
        if map_tile_y > 0 :
            neighbor = self.map_elements[map_tile_x][map_tile_y-1]
            if neighbor: neighbors['U']=neighbor
        if map_tile_y < MAP_WIDTH - 1 :
            neighbor = self.map_elements[map_tile_x][map_tile_y+1]
            if neighbor: neighbors['D']=neighbor
        
        # filter out excluded elements:
        neighbors = {end:element for end, element in neighbors.items() if element not in exclude}

        if direction==UPSTREAM:
            # The below map element types are ordered by priority of connection, in case multiple neighbor types exist. This order can be changed by the likes of the players.
            for relative_position, buddy in neighbors.items():
                if (isinstance(buddy, Base_station) and buddy.next_segment is None) : return (relative_position, buddy)
            for relative_position, buddy in neighbors.items():
                if (isinstance(buddy, Track_segment) or isinstance(buddy, Switch)) and buddy.next_segment is None : return (relative_position, buddy)
            for relative_position, buddy in neighbors.items():
                if isinstance(buddy, Switch) and buddy.next_segment_inactive is None : return (relative_position, buddy)
        elif direction==DOWNSTREAM:
            for relative_position, buddy in neighbors.items():
                if (isinstance(buddy, Track_segment) or isinstance(buddy, Switch)) and buddy.previous_segment is None : return (relative_position, buddy)
            for relative_position, buddy in neighbors.items():
                if (isinstance(buddy, Station) and buddy.previous_segment is None) : return (relative_position, buddy)
        else: raise ValueError("get_neighbor expects direction='{UPSTREAM}'/'{DOWNSTREAM}', but received '{direction}'") 
        return None # nothing found

    def handler_click_place_track(self):

        x, y = pygame.mouse.get_pos()
        if x <= MAP_WIDTH*ELEMENT_SIZE and y <= MAP_HEIGHT*ELEMENT_SIZE:
            current_tile = ((x-1)//ELEMENT_SIZE, (y-1)//ELEMENT_SIZE)
            current_tile_x, current_tile_y = current_tile
            
            if self.map_elements[current_tile_x][current_tile_y] is None: # tracks should not overwrite other elements

                self.is_dragging_track = True
                
                current_track_segment = Track_segment(x = current_tile_x * ELEMENT_SIZE + ELEMENT_SIZE//2, y = current_tile_y * ELEMENT_SIZE + ELEMENT_SIZE//2)
                
                # scan for unconnected upstream neigbors if any, and connect the first found:
                neighbors_connected = []
                neighbor_info = self.get_neighbor(current_tile_x, current_tile_y, UPSTREAM) 
                if neighbor_info:
                    neighbor_relative_position, neighbor = neighbor_info
                    if neighbor.next_segment is None:
                        neighbor.next_segment = current_track_segment
                        neighbor.end2 = Utils.get_opposite_end(neighbor_relative_position)
                        current_track_segment.end1 = neighbor_relative_position
                        current_track_segment.previous_segment = neighbor
                    # if the neighbor is a Switch, also consider the special "next_segment_inactive" and "end2_inactive" connections:
                    elif isinstance(neighbor, Switch) and neighbor.next_segment_inactive is None:
                        neighbor.next_segment_inactive = current_track_segment
                        neighbor.end2_inactive = Utils.get_opposite_end(neighbor_relative_position)
                        current_track_segment.end1 = neighbor_relative_position
                        current_track_segment.previous_segment = neighbor
                    neighbors_connected.append(neighbor)
                else: # no upstream neighbors
                    current_track_segment.end1 = 'L' # default
                
                # same for downstram:
                neighbor_info = self.get_neighbor(current_tile_x, current_tile_y, DOWNSTREAM, exclude=neighbors_connected) 
                if neighbor_info:
                    neighbor_relative_position, neighbor = neighbor_info
                    neighbor.previous_segment = current_track_segment
                    neighbor.end1 = Utils.get_opposite_end(neighbor_relative_position)
                    current_track_segment.end2 = neighbor_relative_position
                    current_track_segment.next_segment = neighbor
                    neighbors_connected.append(neighbor)
                else: # no downstream neighbors
                    current_track_segment.end2='R' #default

                # add the track segment to the map and current temp chain:
                self.map_elements[current_tile_x][current_tile_y] = current_track_segment
                self.current_track_chain.append(current_track_segment)
                #prepare for next iteration:
                self.previous_track_tile_position = current_tile                            
    
    def handle_click_place_switch(self):
        new_switch = Switch(self.map_x, self.map_y)
        
        # Connect the new_switch:
        # If, when placing it, we break a chain, reconnect the chain witih this new switch in it.
        # Otherwise, connect this new switch to whatever neighbors are unconnected, if any.
        neighbors_connected = []
        if self.clicked_element and self.clicked_element.previous_segment: # upstream connectoin
            self.clicked_element.previous_segment.next_segment = new_switch
            new_switch.end1 = self.clicked_element.end1
            new_switch.previous_segment = self.clicked_element.previous_segment
            neighbors_connected.append(self.clicked_element.previous_segment)
        else: # otherwise, search for any upstream unconnected neighbors:
            neighbor_info = self.get_neighbor(self.current_tile_x, self.current_tile_y, UPSTREAM, exclude=neighbors_connected) 
            if neighbor_info:
                neighbor_relative_position, neighbor = neighbor_info
                if neighbor.next_segment is None:
                    neighbor.next_segment = new_switch
                    neighbor.end2 = Utils.get_opposite_end(neighbor_relative_position)
                    new_switch.end1 = neighbor_relative_position
                    new_switch.previous_segment = neighbor
                # if neighbor's next_segment was already connected but that neighbor is a Switch, also consider checking if its secondary "next_segment_inactive" is unconnected:
                elif isinstance(neighbor, Switch) and neighbor.next_segment_inactive is None:
                    neighbor.next_segment_inactive = new_switch
                    neighbor.end2_inactive = Utils.get_opposite_end(neighbor_relative_position)
                    new_switch.end1 = neighbor_relative_position
                    new_switch.previous_segment = neighbor
                neighbors_connected.append(neighbor)
                # no need for "else:", because since get_neighbor returned something, for sure that something has an unconnected end.
            
        # Now the same for downstream. First search if our new element was placed on an existing chain:
        if self.clicked_element and self.clicked_element.next_segment:
            self.clicked_element.next_segment.previous_segment = new_switch
            new_switch.end2 = self.clicked_element.end2
            new_switch.next_segment = self.clicked_element.next_segment
            neighbors_connected.append(self.clicked_element.next_segment)
        else: #otherwise, search for downstream unconnected neighbors:
            neighbor_info = self.get_neighbor(self.current_tile_x, self.current_tile_y, DOWNSTREAM, exclude=neighbors_connected) 
            if neighbor_info:
                neighbor_relative_position, neighbor = neighbor_info
                neighbor.previous_segment = new_switch
                neighbor.end1 = Utils.get_opposite_end(neighbor_relative_position)
                new_switch.end2 = neighbor_relative_position
                new_switch.next_segment = neighbor
                neighbors_connected.append(neighbor)
            else:
                new_switch.end2 = 'R' # default
        # Now the same but for the new switch's next_segment_inactive, maybe we find a connection for it too:
        neighbor_info = self.get_neighbor(self.current_tile_x, self.current_tile_y, DOWNSTREAM, exclude=neighbors_connected) 
        if neighbor_info:
            neighbor_relative_position, neighbor = neighbor_info
            neighbor.previous_segment = new_switch
            neighbor.end1 = Utils.get_opposite_end(neighbor_relative_position)
            new_switch.end2_inactive = neighbor_relative_position
            new_switch.next_segment_inactive = neighbor
            neighbors_connected.append(neighbor)
        
        # If either end is unconnected, chose some default orientations for end1/2/2_inactive: 
        all_ends_desc = {'end1', 'end2', 'end2_inactive'}
        all_ends_possible_values = {'L','R','U','D'}
        need_defaults = True
        while need_defaults:
            # take first found unconnected end, if any
            unconnected_end_desc = next((end_desc for end_desc in all_ends_desc if getattr(new_switch, end_desc) is None), None)
            if unconnected_end_desc:
                connected_ends = {getattr(new_switch, end_desc) for end_desc in all_ends_desc if getattr(new_switch, end_desc)}
                if len(connected_ends) > 0:
                    setattr(new_switch, unconnected_end_desc, 
                            next(iter(all_ends_possible_values - connected_ends))) # assigns the first unused orientation found
                else: # none of the 3 ends is connected, set a hardcoded default - this will happen a single time in this loop
                    setattr(new_switch, unconnected_end_desc, 'L')
            else: # all connected, finish:
                need_defaults = False
        
        self.map_elements[self.current_tile_x][self.current_tile_y] = new_switch


    def handle_drag_track(self):
        x, y = pygame.mouse.get_pos()
        if x <= MAP_WIDTH*ELEMENT_SIZE and y <= MAP_HEIGHT*ELEMENT_SIZE:
            current_tile = ((x-1)//ELEMENT_SIZE, (y-1)//ELEMENT_SIZE)
            current_tile_x, current_tile_y = current_tile
            
            # Only create new track if we've moved to a different tile
            if (current_tile != self.previous_track_tile_position 
                and self.previous_track_tile_position is not None
                # don't overwrite something else on the map
                and self.map_elements[current_tile_x][current_tile_y] is None):

                # Determine track orientation based on movement
                previous_tile_x, previous_tile_y = self.previous_track_tile_position
                
                # Determine track endpoints
                if current_tile_x > previous_tile_x:
                    current_ends = ('L', 'R') # end2 is just a default
                    self.current_track_chain[-1].end2 = 'R' # previous' end2 might be changed by the direction of the new segment, so update it
                elif current_tile_x < previous_tile_x:
                    current_ends = ('R', 'L')
                    self.current_track_chain[-1].end2 = 'L'
                elif current_tile_y > previous_tile_y:
                    current_ends = ('U', 'D')
                    self.current_track_chain[-1].end2 = 'D'
                else:
                    current_ends = ('D', 'U')
                    self.current_track_chain[-1].end2 = 'U'
                
                map_current_x = current_tile_x * ELEMENT_SIZE + ELEMENT_SIZE//2
                map_current_y = current_tile_y * ELEMENT_SIZE + ELEMENT_SIZE//2
                current_track_segment = Track_segment(map_current_x, map_current_y, current_ends[0], current_ends[1], previous_segment=self.current_track_chain[-1])

                # also forward link the previous to this one:
                self.current_track_chain[-1].next_segment = current_track_segment
                
                # Add to map and track chain
                self.map_elements[current_tile_x][current_tile_y] = current_track_segment
                self.current_track_chain.append(current_track_segment)
                #prepare for next iteration:
                self.previous_track_tile_position = current_tile


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
    
            #handle clicks on buttons:
            for button in self.palette_buttons:
                if button.handle_event(event): # if button was pressed:
                     # pop all other buttons (they might be toggle buttons)
                    for other_button in self.palette_buttons:
                        if other_button!=button:
                            other_button.is_selected = False
            if self.start_button.handle_event(event) and self.game_state == Game_state.SETUP:
                for button in self.palette_buttons: button.is_selected = False
                if not(self.base_station):
                    Tk().wm_withdraw() 
                    messagebox.showinfo('Info',"Place the base station before starting the game.")
                elif len(self.stations) == 0:
                    Tk().wm_withdraw() 
                    messagebox.showinfo('Info',"Place at least one destination station before starting the game.")
                else:
                    self.game_state == Game_state.RUNNING  # signal to run_app that it needs to call update_map
                

            # handle clicks on map area:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                if x <= MAP_WIDTH*ELEMENT_SIZE and y <= MAP_HEIGHT*ELEMENT_SIZE:
                    self.current_tile_x = (x-1)//ELEMENT_SIZE
                    self.current_tile_y = (y-1)//ELEMENT_SIZE
                    # click coordinates snapped to map grid (to center of tiles more exactly):
                    self.map_x = (x-1)//ELEMENT_SIZE*ELEMENT_SIZE+ELEMENT_SIZE//2
                    self.map_y = (y-1)//ELEMENT_SIZE*ELEMENT_SIZE+ELEMENT_SIZE//2
                    self.clicked_element = self.map_elements[self.current_tile_x][self.current_tile_y]

                    if (self.game_state == Game_state.SETUP and self.station_button.is_selected and self.clicked_element is None):
                        
                        new_color = random.choice([color for color in ELEMENT_POSSIBLE_COLORS if color not in [station.color for station in self.stations]]) # chose a color not previously used
                        new_station = Station(x=self.map_x,y=self.map_y,color=new_color)
                        self.stations.append(new_station)
                        if len(self.stations) == len(ELEMENT_POSSIBLE_COLORS):
                            Tk().wm_withdraw() # draw back the main window for showing pop-up
                            messagebox.showinfo('Info',"This is the last station available")
                            self.station_button.is_enabled = False
                            self.station_button.is_selected = False
                        self.map_elements[self.current_tile_x][self.current_tile_y]=new_station

                    if (self.game_state == Game_state.SETUP and self.base_station_button.is_selected
                        and self.clicked_element is None):

                        self.base_station=Base_station(self.map_x,self.map_y)
                        if (self.base_station_tile_position != (-1,-1)):  # if the base station already existed, clear it from its old place - there can be only one:
                            self.map_elements[self.base_station_tile_position[0]][self.base_station_tile_position[1]] = None
                        self.map_elements[self.current_tile_x][self.current_tile_y]=self.base_station
                        self.base_station_tile_position = (self.current_tile_x, self.current_tile_y)

                    if (self.game_state == Game_state.SETUP and self.switch_button.is_selected and
                           # the switch can be placed on an empty tile or overwrite a track segment
                           (self.clicked_element is None or isinstance(self.clicked_element,Track_segment))):
                        self.handle_click_place_switch()
                        
 

            # Handle track placement. This is a bit different than the above elements placement, as we use a dragging mechanism so we have to consider the mouse movement event too.
            # We have 2 separate events for which we lay segments: 
            #    MOUSEBUTTONDOWN (for the first segment in a chain) - for connecting the segment, we look for neighbors 
            #    MOUSEMOTION (for next segments in a chain) - for connecting the segment, we ignore neighbors and just connect along the line dragged by the user, to avoid possibly unwanted neighbor connections
            if self.game_state == Game_state.SETUP and self.track_button.is_selected:
                
                if event.type == pygame.MOUSEBUTTONDOWN: #first segment in a chain. 
                    self.handler_click_place_track()

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.is_dragging_track = False
                    self.previous_track_tile_position = None
                    # Here you could finalize the track placement if needed
                    self.current_track_chain = []


                elif event.type == pygame.MOUSEMOTION and self.is_dragging_track:
                    self.handle_drag_track()

        return True

    def update_map():
        pass
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw grid lines
        for x in range(0, MAP_WIDTH*ELEMENT_SIZE+1, ELEMENT_SIZE): pygame.draw.line(self.screen, pygame.Color('black'), (x, 0), (x, MAP_HEIGHT*ELEMENT_SIZE), 1)
        for y in range(0, MAP_WIDTH*ELEMENT_SIZE+1, ELEMENT_SIZE): pygame.draw.line(self.screen, pygame.Color('black'), (0, y), (MAP_WIDTH*ELEMENT_SIZE, y), 1)

        for row in self.map_elements:
            for element in row:
                if element is not None:
                    element.draw(self.screen)
        
        for button in (self.palette_buttons + self.control_buttons): button.draw(self.screen)
                
        pygame.display.flip()

    def run_app(self):
        app_running = True
        while app_running:
            app_running = self.handle_events()
            if self.game_state == Game_state.RUNNING:
                self.update_map()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run_app()
