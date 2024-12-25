from typing import List, Tuple, Dict
import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Train Station Game")

# Colors
BACKGROUND_COLOR = (34, 139, 34)
TRACK_COLOR = (0, 0, 0)
STATION_COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "purple": (128, 0, 128),
    "black": (0, 0, 0)
}
SWITCH_COLOR = (173, 255, 47)  # Light green for switches

# Define positions for stations and switches
station_positions = {
    "red": (600, 100),
    "green": (100, 500),
    "blue": (400, 500),
    "yellow": (100, 100),
    "purple": (500, 400),
    "black": (600, 400)
}

# Define switch positions
switches = [
    (200, 200),
    (400, 200),
    (200, 400),
    (400, 300)
]

# Define track segments based on station keys and switches
# Each tuple represents a pair of endpoints for a track segment
track_segments = [
    ("start", switches[0]),       # Start point to first switch
    (switches[0], switches[1]),   # First switch to second switch
    (switches[1], "red"),         # Second switch to red station
    (switches[0], switches[2]),   # First switch to third switch
    (switches[2], "green"),       # Third switch to green station
    (switches[2], switches[3]),   # Third switch to fourth switch
    (switches[3], "purple"),      # Fourth switch to purple station
    (switches[3], "blue")         # Fourth switch to blue station
]

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

stations = {key: Station(x, y, STATION_COLORS[key]) for key, (x, y) in station_positions.items()}

# Helper function to get position
def get_position(key):
    if isinstance(key, tuple):  # If it's a tuple (switch), return it directly
        return key
    elif key == "start":  # Hard-coded start position for trains
        return (0, 0)
    else:  # Otherwise, it's a station key
        return station_positions[key]

# Draw function to handle tracks, stations, and switches
def draw_elements():
    # Draw tracks based on segment definitions
    for start_key, end_key in track_segments:
        start_pos = get_position(start_key)
        end_pos = get_position(end_key)
        pygame.draw.line(window, TRACK_COLOR, start_pos, end_pos, 5)

    # Draw stations as colored circles
    for station in stations.values():
        station.draw(window)

    # Draw switches as light green circles
    for pos in switches:
        pygame.draw.circle(window, SWITCH_COLOR, pos, 15)

# Main game loop
def main():
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the background
        window.fill(BACKGROUND_COLOR)

        # Draw tracks, stations, and switches
        draw_elements()

        pygame.display.flip()
        clock.tick(60)  # Limit FPS to 60

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
