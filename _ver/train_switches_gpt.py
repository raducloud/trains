import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600  # Adjust this as needed
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Train Station Game")

# Colors
BACKGROUND_COLOR = (34, 139, 34)  # Forest green as a placeholder background

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

        # Placeholder for tracks, stations, and switches setup
        # (We’ll add them step-by-step in future parts)

        pygame.display.flip()
        clock.tick(60)  # Limit FPS to 60

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
