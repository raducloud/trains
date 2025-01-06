import pygame
from enum import Enum, auto
from typing import List, Tuple, Dict
from game_utils import *
from game_config import *
from game_utils import *
from game_ui_utils import *
from map_elements import *
from map import *

# This is a game of routing colored trains to stations of same color.
# The trains advance by themselves at constant speeds, all originating at the single base station form which they spawn at some time intervals and following tracks.
# What the player does is act on some switches which are placed at track intersections,
#     each switch having one fixed end and one mobile end, the mobile end can be switched between 2 positions by the user click/touch.
# If the player manages to direct a train to the station with the same color as the train, they receieve a point.

class Game:

    def __init__(self):

        pygame.init()
        pygame.display.set_caption("Train Routing Puzzle")
        self.clock = pygame.time.Clock()

        # map-related gameplay items:
        self.map = Map()
        self.trains = []
        self.colors = [] # all colors used after all stations have been placed
        # map state:
        self.trains_en_route = 0
        self.trains_at_destination = 0
        self.time_since_last_train_spawn = -1

        # Others:
        # UI elements:
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        toolbar_y = MAP_HEIGHT * ELEMENT_SIZE + 10
        self.base_station_button = ToggleButton(BUTTON_MARGIN, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Base")
        self.station_button = ToggleButton(BUTTON_MARGIN * 2 + BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Station")
        self.track_button = ToggleButton(BUTTON_MARGIN * 3 + BUTTON_WIDTH * 2, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Track")
        self.switch_button = ToggleButton(BUTTON_MARGIN * 4 + BUTTON_WIDTH * 3, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Switch")
        self.start_button = Button(WINDOW_WIDTH - BUTTON_MARGIN - BUTTON_WIDTH, toolbar_y, BUTTON_WIDTH, BUTTON_HEIGHT, "Start")
        self.palette_buttons = [self.base_station_button, self.station_button, self.track_button, self.switch_button]
        self.control_buttons = [self.start_button]
        self.popup_active = False
        self.popup_message = None
        #state:
        self.game_state = Game_state.SETUP


    def handle_events(self):
        for event in pygame.event.get():

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN) and self.popup_active == True:
                self.popup_active = False
                return True
            
            if event.type == pygame.QUIT:
                return False
    
            #handle clicks on buttons:
            for button in self.palette_buttons:
                if button.handle_event(event): # if button was pressed:
                     # pop all other buttons (they might be toggle buttons)
                    for other_button in self.palette_buttons:
                        if other_button!=button:
                            other_button.is_selected = False
                    return True

            if self.start_button.handle_event(event) and self.game_state == Game_state.SETUP:
                if not(self.map.base_station): self.show_message("Place the base station before starting the game.")
                elif len(self.map.stations) == 0: self.show_message("Place at least one destination station before starting the game.")
                else:
                    self.game_state = Game_state.RUNNING  # signal to run_app that it needs to call update_map
                    for button in self.control_buttons + self.palette_buttons: 
                        button.is_enabled = False
                        button.is_selected = False
                return True

            # handle clicks on map area:
            if event.type == pygame.MOUSEBUTTONDOWN:
                x,y = pygame.mouse.get_pos()
                if x <= MAP_WIDTH*ELEMENT_SIZE and y <= MAP_HEIGHT*ELEMENT_SIZE:
                    
                    self.map.set_click_location(x, y)

                    if (self.game_state == Game_state.SETUP):
                    
                        if (self.station_button.is_selected and self.map.clicked_element is None):
                            self.map.add_station()
                            if len(self.map.stations) == len(ELEMENT_POSSIBLE_COLORS):
                                self.show_message('This was the last station available.')
                                self.station_button.is_enabled = False
                                self.station_button.is_selected = False

                        if (self.base_station_button.is_selected and self.map.clicked_element is None):
                            self.map.add_base_station()

                        if (self.track_button.is_selected and self.map.clicked_element is None):
                            self.map.add_track_click()

                        if (self.switch_button.is_selected and # the switch can be placed on an empty tile or overwrite a track segment
                            (self.map.clicked_element is None or isinstance(self.map.clicked_element,Track_segment))):
                            self.map.add_switch()

                    elif self.game_state == Game_state.RUNNING and isinstance(self.map.clicked_element, Switch):
                        self.map.clicked_element.toggle()

                return True
 

            # Handle track placement. This is a bit different than the above elements placement, as we use a dragging mechanism so we have to consider the mouse movement event too.
            # We have 2 separate events for which we lay segments: 
            #    MOUSEBUTTONDOWN (for the first segment in a chain) - for connecting the segment, we look for neighbors 
            #    MOUSEMOTION (for next segments in a chain) - for connecting the segment, we ignore neighbors and just connect along the line dragged by the user, to avoid possibly unwanted neighbor connections
            if self.game_state == Game_state.SETUP and self.map.is_dragging_track and self.track_button.is_selected:
                
                if event.type == pygame.MOUSEMOTION:
                    self.map.add_track_drag()
                    return True

                if event.type == pygame.MOUSEBUTTONUP:
                    self.map.is_dragging_track = False
                    self.map.previous_track_tile_position = None
                    self.map.current_track_chain = []
                    return True

        return True

    def update_map(self):
        for train in self.trains: train.advance()
            
    
    def show_message(self, message):
        self.popup_active = True
        self.popup_message = message
    
    def draw_popup(self):
        popup_rect = pygame.Rect(0, WINDOW_HEIGHT//2, WINDOW_WIDTH, int(100 * GAME_SPACE_SCALE_FACTOR))
        pygame.draw.rect(self.screen, (200, 200, 200), popup_rect)  # Light gray background
        font_popup_size = int(24 * GAME_SPACE_SCALE_FACTOR)
        font_popup = pygame.font.Font(None, font_popup_size)
        text = font_popup.render(self.popup_message, True, (0, 0, 0))
        self.screen.blit(text, (popup_rect.x + int(4 * GAME_SPACE_SCALE_FACTOR), popup_rect.y + int(20 * GAME_SPACE_SCALE_FACTOR) ))
        
    
    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw grid lines
        for x in range(0, MAP_WIDTH*ELEMENT_SIZE+1, ELEMENT_SIZE): pygame.draw.line(self.screen, pygame.Color('black'), (x, 0), (x, MAP_HEIGHT*ELEMENT_SIZE), 1)
        for y in range(0, MAP_WIDTH*ELEMENT_SIZE+1, ELEMENT_SIZE): pygame.draw.line(self.screen, pygame.Color('black'), (0, y), (MAP_WIDTH*ELEMENT_SIZE, y), 1)

        for row in self.map.map_elements:
            for element in row:
                if element is not None:
                    element.draw(self.screen)
        
        for button in (self.palette_buttons + self.control_buttons): button.draw(self.screen)

        if self.popup_active: self.draw_popup()
                
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
