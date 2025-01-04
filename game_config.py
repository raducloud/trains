from enum import Enum, auto
import pygame

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
UPSTREAM = "upstream"
DOWNSTREAM = "downstream"

class Train_status(Enum):
    IN_BASE = "in_base"
    EN_ROUTE = "en_route"
    STRANDED = "stranded"
    IN_HOME_STATION = "in_home_station"
    IN_WRONG_STATION = "in_wrong_station"

class Game_state(Enum):
    SETUP = auto()
    RUNNING = auto()
    PAUSED = auto()
    OVER = auto()


ELEMENT_POSSIBLE_COLORS = [pygame.Color('red'),
                           pygame.Color('blue'),
                           pygame.Color('yellow'),
                           pygame.Color('green'),
                           pygame.Color('purple'),
                           pygame.Color('orange'),
                           pygame.Color('cyan')]
FPS = 60
TRAIN_SPAWN_INTERVAL = 5  # seconds

