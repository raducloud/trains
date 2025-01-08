import random
import pygame
from enum import Enum, auto
from typing import List, Tuple, Dict
from game_config import *
from game_utils import *
from game_ui_utils import *
from map_elements import *

class Map:
    def __init__(self):
        self.map_elements = [[None for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]
        self.base_station = None
        self.base_station_tile_position = (-1,-1) # -1 means "doesn't exist"
        self.stations = []
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

    def set_click_location(self, x, y):
        self.current_tile_x = (x-1)//ELEMENT_SIZE
        self.current_tile_y = (y-1)//ELEMENT_SIZE
        # click coordinates snapped to map grid (to center of tiles more exactly):
        self.map_x = (x-1)//ELEMENT_SIZE*ELEMENT_SIZE+ELEMENT_SIZE//2
        self.map_y = (y-1)//ELEMENT_SIZE*ELEMENT_SIZE+ELEMENT_SIZE//2
        self.clicked_element = self.map_elements[self.current_tile_x][self.current_tile_y]

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

    # calls get neighbor and, if found, connects it downstream
    def scan_connect_downstream(self, element_to_be_connected, current_tile_x, current_tile_y, excluded_neighbors=[], is_inactive_end=False):

        neighbor_info = self.get_neighbor(current_tile_x, current_tile_y, DOWNSTREAM, exclude=excluded_neighbors) 
        if neighbor_info:
            neighbor_relative_position, neighbor = neighbor_info
            neighbor.previous_segment = element_to_be_connected
            neighbor.end1 = Utils.get_opposite_end(neighbor_relative_position)
            if is_inactive_end:
                element_to_be_connected.end2_inactive = neighbor_relative_position
                element_to_be_connected.next_segment_inactive = neighbor
            else:
                element_to_be_connected.end2 = neighbor_relative_position
                element_to_be_connected.next_segment = neighbor
            return neighbor
        else: # no downstream neighbors found
            element_to_be_connected.end2='R' #default
            return None


    def add_station(self):

        new_color = random.choice([color for color in ELEMENT_POSSIBLE_COLORS if color not in [station.color for station in self.stations]]) # chose a color not previously used
        new_station = Station(x=self.map_x,y=self.map_y,color=new_color)
        self.stations.append(new_station)
        self.map_elements[self.current_tile_x][self.current_tile_y]=new_station
    
    def add_base_station(self):

        self.base_station=Base_station(self.map_x,self.map_y)
        if (self.base_station_tile_position != (-1,-1)):  # if the base station already existed, clear it from its old place - there can be only one:
            self.map_elements[self.base_station_tile_position[0]][self.base_station_tile_position[1]] = None
        self.map_elements[self.current_tile_x][self.current_tile_y]=self.base_station
        self.base_station_tile_position = (self.current_tile_x, self.current_tile_y)
        

    def add_track_click(self):

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
                downstream_neighbor = self.scan_connect_downstream(element_to_be_connected=current_track_segment, current_tile_x=current_tile_x, current_tile_y=current_tile_y, excluded_neighbors=neighbors_connected)
                # if downstream_neighbor: neighbors_connected.append(neighbor)

                # add the track segment to the map and current temp chain:
                self.map_elements[current_tile_x][current_tile_y] = current_track_segment
                self.current_track_chain.append(current_track_segment)
                #prepare for next iteration:
                self.previous_track_tile_position = current_tile                            
    
    def add_switch(self):
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


    def add_track_drag(self):
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

