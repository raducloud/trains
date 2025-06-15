import random
from typing import Tuple

from game_ui_utils import *
from game_utils import *
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

    def get_neighbor(self, map_tile_x:int, map_tile_y:int, direction:str, exclude:list=None) -> Tuple[str, Map_element]:
         # Returns the first unconnected neighbor element found and its relative position in format l/R/U/D.
         # It is useful during laying track/switch chains, for connecting0
         # direction parameter should be "upstraem" or "downstream".
         # exclude parameter is used for cases like a neighbor being able to connect both to UPSTREAM and DOWNSTREAM, to not create an infinite cycle, exclude it at second search

        neighbors = {}
        if not exclude: exclude = []

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
                if isinstance(buddy, Base_station) and buddy.next_segment is None: return relative_position, buddy
            for relative_position, buddy in neighbors.items():
                if (isinstance(buddy, Track_segment) or isinstance(buddy, Switch)) and buddy.next_segment is None : return relative_position, buddy
            for relative_position, buddy in neighbors.items():
                if isinstance(buddy, Switch) and buddy.next_segment_inactive is None : return relative_position, buddy
        elif direction==DOWNSTREAM:
            for relative_position, buddy in neighbors.items():
                if (isinstance(buddy, Track_segment) or isinstance(buddy, Switch)) and buddy.previous_segment is None : return relative_position, buddy
            for relative_position, buddy in neighbors.items():
                if isinstance(buddy, Station) and buddy.previous_segment is None: return relative_position, buddy
        else: raise ValueError("get_neighbor expects direction='{UPSTREAM}'/'{DOWNSTREAM}', but received '{direction}'") 
        return None # nothing found

    def scan_connect_upstream(self, element_to_be_connected, current_tile_x, current_tile_y, excluded_neighbors:list=None) -> Map_element:

        if not excluded_neighbors: excluded_neighbors = []
        # never allow connecting the downstream also to upstream:
        if element_to_be_connected.next_segment: excluded_neighbors.append(element_to_be_connected.next_segment)
        if isinstance(element_to_be_connected, Switch) and element_to_be_connected.next_segment_inactive: excluded_neighbors.append(element_to_be_connected.next_segment_inactive)

        neighbor_info = self.get_neighbor(current_tile_x, current_tile_y, UPSTREAM, exclude=excluded_neighbors)
        if neighbor_info:
            neighbor_relative_position, neighbor = neighbor_info
            if neighbor.next_segment is None:
                neighbor.next_segment = element_to_be_connected
                neighbor.end2 = Utils.get_opposite_end(neighbor_relative_position)
            # if the neighbor is a Switch, also consider the special "next_segment_inactive" and "end2_inactive" connections:
            elif isinstance(neighbor, Switch) and neighbor.next_segment_inactive is None:
                neighbor.next_segment_inactive = element_to_be_connected
                neighbor.end2_inactive = Utils.get_opposite_end(neighbor_relative_position)
            element_to_be_connected.end1 = neighbor_relative_position
            element_to_be_connected.previous_segment = neighbor
            # in case the current element or the neighbor still have unconnected ends, straighten them in case they got curled after this connection:
            self.assign_free_end_defaults(neighbor)
            self.assign_free_end_defaults(element_to_be_connected)
            return neighbor
        else: return None # no upstream neighbor found

    # calls get neighbor and, if found, connects it downstream
    def scan_connect_downstream(self, element_to_be_connected, current_tile_x, current_tile_y, excluded_neighbors:list=None, is_inactive_end=False) -> Map_element:

        if not excluded_neighbors: excluded_neighbors = []
        # never allow connecting the upstream also to downstream:
        if element_to_be_connected.previous_segment: excluded_neighbors.append(element_to_be_connected.previous_segment)

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
            # in case the current element or the neighbor still have unconnected ends, straighten them in case they got curled after this connection:
            self.assign_free_end_defaults(neighbor)
            self.assign_free_end_defaults(element_to_be_connected)
            return neighbor
        else: return None # no downstream neighbors found

    def assign_free_end_defaults(self, map_element):
        # If either end is unconnected, chose some default orientations for end1/2/2_inactive, from the orientations which are not already used by the elemnt's other endings.
        if isinstance(map_element, Switch):
            # We have many end pair combinations for switch.
            # So, to not do repetitive writing, and as a programming exercise, we dynamically loop through all attributes of the map_element with getattr()
            all_ends_desc = {'end1', 'end2','end2_inactive'}
            all_ends_possible_values = {'L','R','U','D'}
            # reset any default orientations (which were set WITHOUT having an actual neighbor on that side), to recalculate them below
            if not map_element.previous_segment: map_element.end1 = None
            if not map_element.next_segment: map_element.end2 = None
            if not map_element.next_segment_inactive: map_element.end2_inactive = None

            need_defaults = True
            while need_defaults:
                # take first found unconnected end, if any
                unconnected_end_desc = next((end_desc for end_desc in all_ends_desc if getattr(map_element, end_desc) is None), None)
                if unconnected_end_desc:
                    connected_ends = {getattr(map_element, end_desc) for end_desc in all_ends_desc if getattr(map_element, end_desc)}
                    if len(connected_ends) > 0:
                        setattr(map_element, unconnected_end_desc,
                                next(iter(all_ends_possible_values - connected_ends))) # assigns the first unused orientation found
                    else: # none of the 3 ends is connected, set a hardcoded default - this will happen a single time in this loop
                        setattr(map_element, unconnected_end_desc, 'L')
                else: # all connected, finish:
                    need_defaults = False
        else:  # just assign an opposite end, so straighten the segment:
            if not map_element.previous_segment: map_element.end1 = Utils.get_opposite_end(map_element.end2)
            if not map_element.next_segment: map_element.end2 = Utils.get_opposite_end(map_element.end1)

    def erase_element(self):

        # clear the element from the map state variables:
        if isinstance(self.clicked_element, Station): self.stations.remove(self.clicked_element)
        elif isinstance(self.clicked_element, Base_station): self.base_station = None

        # clear the element's connections:
        if self.clicked_element.next_segment:
            self.clicked_element.next_segment.previous_segment = None
        if isinstance(self.clicked_element, Switch) and self.clicked_element.next_segment_inactive:
            self.clicked_element.next_segment_inactive.previous_segment = None
        if self.clicked_element.previous_segment:  # this is a bit more complex because upstream we can find a Switch or not:
            if self.clicked_element.previous_segment.next_segment == self.clicked_element:
                self.clicked_element.previous_segment.next_segment = None
            elif isinstance(self.clicked_element.previous_segment, Switch) and self.clicked_element.previous_segment.next_segment_inactive == self.clicked_element:
                self.clicked_element.previous_segment.next_segment_inactive = None

        # finally, clear the element from the map:
        self.map_elements[self.current_tile_x][self.current_tile_y] = None


    def add_station(self):

        new_color = random.choice([color for color in ELEMENT_POSSIBLE_COLORS if color not in [station.color for station in self.stations]]) # chose a color not previously used
        new_station = Station(x=self.map_x,y=self.map_y,color=new_color)
        self.scan_connect_upstream(element_to_be_connected=new_station, current_tile_x=self.current_tile_x, current_tile_y=self.current_tile_y)
        self.stations.append(new_station)
        self.map_elements[self.current_tile_x][self.current_tile_y]=new_station
    
    def add_base_station(self):

        self.base_station=Base_station(self.map_x,self.map_y)
        if (self.base_station_tile_position != (-1,-1)):  # if the base station already existed, clear it from its old place - there can be only one:
            self.map_elements[self.base_station_tile_position[0]][self.base_station_tile_position[1]] = None
        self.scan_connect_downstream(element_to_be_connected = self.base_station, current_tile_x = self.current_tile_x, current_tile_y = self.current_tile_y)
        self.map_elements[self.current_tile_x][self.current_tile_y]=self.base_station
        self.base_station_tile_position = (self.current_tile_x, self.current_tile_y)
        

    def add_track_by_click(self):

        x, y = pygame.mouse.get_pos()
        if x <= MAP_WIDTH*ELEMENT_SIZE and y <= MAP_HEIGHT*ELEMENT_SIZE:
            current_tile = ((x-1)//ELEMENT_SIZE, (y-1)//ELEMENT_SIZE)
            current_tile_x, current_tile_y = current_tile
            
            if self.map_elements[current_tile_x][current_tile_y] is None: # tracks should not overwrite other elements

                self.is_dragging_track = True
                
                current_track_segment = Track_segment(x = current_tile_x * ELEMENT_SIZE + ELEMENT_SIZE//2, y = current_tile_y * ELEMENT_SIZE + ELEMENT_SIZE//2)
                
                # scan for unconnected upstream neigbors if any, and connect the first found:
                neighbors_connected = []
                upstream_neighbor = self.scan_connect_upstream(element_to_be_connected=current_track_segment, current_tile_x=current_tile_x, current_tile_y=current_tile_y, excluded_neighbors=neighbors_connected)
                if upstream_neighbor: neighbors_connected.append(upstream_neighbor)
                # same for downstram:
                self.scan_connect_downstream(element_to_be_connected=current_track_segment, current_tile_x=current_tile_x, current_tile_y=current_tile_y, excluded_neighbors=neighbors_connected)
                
                # add the track segment to the map and current temp chain:
                self.map_elements[current_tile_x][current_tile_y] = current_track_segment
                self.current_track_chain.append(current_track_segment)
                # prepare for mouse dragging, in case it will happen:
                self.previous_track_tile_position = current_tile                            
    
    def add_track_drag(self):
        # This is for placing tracks by DRAGGING the mouse. Unlike placing by simple click, here it's more simple for already knowing the previous tile to connect to, 
        #   but also more complicated because we have to ASSURE connectedness EVEN if:
        #          - the user draggs accros diagonaly (which is not supported in our neighbor logic)
        #          - or if the user drags so fast that the previous drawn segment is not adjacent to current tile.

        x_mouse, y_mouse = pygame.mouse.get_pos()
        end_tile_x = abs(x_mouse-1)//ELEMENT_SIZE # abs and -1 are to handle clicks on extreme edges
        end_tile_y = abs(y_mouse-1)//ELEMENT_SIZE 
        end_tile = (end_tile_x, end_tile_y)
         # Normally the start should be at the first tile the mouse hovered over AFTER the previous_track_tile_position (which was handled by add_track_by_clock), 
         # but for finding out that tile we would need extra maths so, for simplicity, we consider the dragged line as including the previous_track_tile_position, 
         # then do our calculations, then when laying out the track we skip that first one
        start_tile_x, start_tile_y = self.previous_track_tile_position
        is_first_tile_in_line = True
        
        if (x_mouse <= MAP_WIDTH*ELEMENT_SIZE and y_mouse <= MAP_HEIGHT*ELEMENT_SIZE
            and end_tile != self.previous_track_tile_position
            and self.previous_track_tile_position is not None):

            # A bit of math to calculate all the tiles along the way between click location (=previous_track_tile_position) and current (dragged) mouse position.
            # In most cases, there will be 1 tile only, sometimes 2 or 3 tiles, but in case the CPU is too loaded and our app refreshes with delay, there might be more.
            # The calculation is to cover those seldom cases.
            # Basically we have to intersect a line (y=a+b*x) with the grid of units delimiting the tiles

            # We simulate the linear function that passes through our points. We use a bit custom maths instead of the classic y = slope * x + intercept, because of our tile-Manhattan-like geometry https://en.wikipedia.org/wiki/Taxicab_geometry, so which does not support real diagonals.
            # We will loop through all x positions in the dragged range and for each x we'll get the range of cells to fill with tracks on the y axis.
            #     For finding this y range, we add increments to start_tile_y. An increment is the size of the entire y delta divided into how many x tiles we have, so that each x receives an equal segment on the y axis.

            incremenet_tiles_y = math.ceil(  (abs(end_tile_y - start_tile_y))  
                                           / (abs(end_tile_x - start_tile_x) + 1) ) # we add a unit because we work with inclusive start-end for x. For y, the "inclusiveness" will be handled below.
            print(f"1 incremenet_tiles_y = {incremenet_tiles_y}")
            if end_tile_y - start_tile_y != 0: incremenet_tiles_y *= Utils.sign(end_tile_y - start_tile_y)  # multipy by sign() to set direction - ascending or descending
            print(f"2 incremenet_tiles_y = {incremenet_tiles_y}")

            for current_tile_x in Utils.smart_range(start_tile_x, end_tile_x):
                print(f"x = {current_tile_x}")
                start_segment_y = start_tile_y + ( incremenet_tiles_y * abs(current_tile_x - start_tile_x) )
                end_segment_y   = start_tile_y + ( incremenet_tiles_y * (abs(current_tile_x - start_tile_x) + 1) )
                # In cases of (end_tile_y - start_tile_y) = odd number, this y_to will overshoot by a unit because of the math.ceil() and the +1 we use. 
                # This is fine for middle segments, as a workaround (literally around!) for not having diagonal layout of tracks (we have https://en.wikipedia.org/wiki/Taxicab_geometry), 
                #     but for the last segment of course we must not overshoot, as we need to stop exactly where the user stops the mouse/finger. 
                # So avoid overshoot in the last segment by:
                if current_tile_x == end_tile_x: end_segment_y = end_tile_y

                print(f"1 y_from = {start_segment_y}, y_to = {end_segment_y}")

                for current_tile_y in Utils.smart_range(start_segment_y, end_segment_y):  # do the actual map placement of track for that y segment:

                    if not (is_first_tile_in_line): # skip the first for the above mentioned reason (first was already drawn by add_track_by_click)
                    
                        map_current_x = current_tile_x * ELEMENT_SIZE + ELEMENT_SIZE//2
                        map_current_y = current_tile_y * ELEMENT_SIZE + ELEMENT_SIZE//2
                        current_endings = Utils.get_endings_by_prev_tile(*self.previous_track_tile_position, current_tile_x, current_tile_y)
                        current_track_segment = Track_segment(map_current_x, map_current_y, *current_endings, previous_segment=self.current_track_chain[-1])
                        # also forward link the previous one to current one:
                        self.current_track_chain[-1].end2 = Utils.get_opposite_end(current_endings[0])
                        self.current_track_chain[-1].next_segment = current_track_segment
                        # Add to map and to track chain list:
                        self.map_elements[current_tile_x][current_tile_y] = current_track_segment
                        self.current_track_chain.append(current_track_segment)
                        #prepare for next iteration:
                        self.previous_track_tile_position = (current_tile_x, current_tile_y)
                    
                    is_first_tile_in_line = False

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
            upstream_neighbor = self.scan_connect_upstream(new_switch, self.current_tile_x, self.current_tile_y, excluded_neighbors=neighbors_connected)
            if upstream_neighbor: neighbors_connected.append(upstream_neighbor)
            
        # Now the same for downstream. First search if our new element was placed on an existing chain:
        if self.clicked_element and self.clicked_element.next_segment:
            self.clicked_element.next_segment.previous_segment = new_switch
            new_switch.end2 = self.clicked_element.end2
            new_switch.next_segment = self.clicked_element.next_segment
            neighbors_connected.append(self.clicked_element.next_segment)
        else: #otherwise, search for downstream unconnected neighbors:
            downstream_neighbour = self.scan_connect_downstream(new_switch, self.current_tile_x, self.current_tile_y, excluded_neighbors=neighbors_connected)
            if downstream_neighbour: neighbors_connected.append(downstream_neighbour)
        # Now the same but for the new switch's next_segment_inactive, maybe we find a connection for it too:
        self.scan_connect_downstream(new_switch, self.current_tile_x, self.current_tile_y, excluded_neighbors=neighbors_connected, is_inactive_end=True)
        
        self.assign_free_end_defaults(new_switch)
        self.map_elements[self.current_tile_x][self.current_tile_y] = new_switch

    def __getstate__(self):
        """Return state values to be pickled."""
        state = self.__dict__.copy()
        # Remove any unpicklable attributes if needed
        return state

    def __setstate__(self, state):
        """Restore state from the unpickled state values."""
        self.__dict__.update(state)

