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
stations = {
    "red": (600, 100),
    "green": (100, 500),
    "blue": (400, 500),
    "yellow": (100, 100),
    "purple": (500, 400),
    "black": (600, 400)
}

switches = [
    (200, 200),
    (400, 200),
    (200, 400),
    (400, 300)
]

# Draw function to handle tracks, stations, and switches
def draw_elements():
    # Draw tracks as lines
    pygame.draw.line(window, TRACK_COLOR, (0, 0), (200, 200), 5)
    pygame.draw.line(window, TRACK_COLOR, (200, 200), (400, 200), 5)
    pygame.draw.line(window, TRACK_COLOR, (400, 200), (600, 100), 5)
    pygame.draw.line(window, TRACK_COLOR, (200, 200), (200, 400), 5)
    pygame.draw.line(window, TRACK_COLOR, (200, 400), (100, 500), 5)
    pygame.draw.line(window, TRACK_COLOR, (200, 400), (400, 300), 5)
    pygame.draw.line(window, TRACK_COLOR, (400, 300), (500, 400), 5)
    pygame.draw.line(window, TRACK_COLOR, (400, 300), (400, 500), 5)

    # Draw stations as colored circles
    for color, position in stations.items():
        pygame.draw.circle(window, STATION_COLORS[color], position, 20)

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
