from enum import Enum, auto
import pygame
import platform
import sys

if sys.platform.startswith('win'):
    print('Running on Windows')
    GAME_SPACE_SCALE_FACTOR = 1
elif platform.system() == 'Darwin':  # For iOS/macOS
    print('Running on iOS/macOS')
    GAME_SPACE_SCALE_FACTOR = 2
elif platform.system() == 'Linux':   # For Android/Linux
    print('Running on Android/Linux')
    GAME_SPACE_SCALE_FACTOR = 2

FPS_SETUP = 60
FPS_RUN = 20
TRAIN_SPAWN_INTERVAL = 5  # seconds
MAP_WIDTH = 10
MAP_HEIGHT = 10
ELEMENT_SIZE = int(50 * GAME_SPACE_SCALE_FACTOR)
BUTTON_WIDTH = int(80 * GAME_SPACE_SCALE_FACTOR)
BUTTON_HEIGHT = int(40 * GAME_SPACE_SCALE_FACTOR)
BUTTON_MARGIN = int(10 * GAME_SPACE_SCALE_FACTOR)
SCOREBOARD_HEIGHT = int(20 * GAME_SPACE_SCALE_FACTOR)
WINDOW_WIDTH = MAP_WIDTH * ELEMENT_SIZE 
WINDOW_HEIGHT = MAP_HEIGHT * ELEMENT_SIZE + SCOREBOARD_HEIGHT + BUTTON_HEIGHT + BUTTON_MARGIN * 2
LARGE_TEXT_SIZE = int(32 * GAME_SPACE_SCALE_FACTOR)
SMALL_TEXT_SIZE = int(20 * GAME_SPACE_SCALE_FACTOR)
VERY_SMALL_TEXT_SIZE = int(16 * GAME_SPACE_SCALE_FACTOR)
BACKGROUND_COLOR = (34, 89, 34)
BUTTON_COLOR = (200, 200, 200)
BUTTON_HOVER_COLOR = (180, 180, 180)
BUTTON_SELECTED_COLOR = (150, 150, 150)
BUTTON_TEXT_COLOR = (0, 0, 0)
BUTTON_DISABLED_TEXT_COLOR = (100, 100, 100)
TRAIN_SPEED = 1    # Only integers. ELEMENT_SIZE // FPS_RUN would result in 1 element per second
UPSTREAM = "upstream"
DOWNSTREAM = "downstream"

ELEMENT_POSSIBLE_COLORS = [pygame.Color('red'),
                           pygame.Color('blue'),
                           pygame.Color('yellow'),
                           pygame.Color('green'),
                           pygame.Color('purple'),
                           pygame.Color('orange'),
                           pygame.Color('cyan')]

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


