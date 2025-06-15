import pygame
from game_config import *


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.is_hovered = False
        self.is_selected = False
        self.is_enabled = True
        self.font = pygame.font.Font(None, SMALL_TEXT_SIZE)
        self.alt_pressed = False  # True if Alt was pressed during last click

    def draw(self, surface):
        color = BUTTON_SELECTED_COLOR if self.is_selected else BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)  # border
        text_surface = self.font.render(self.text, True, BUTTON_TEXT_COLOR if self.is_enabled else BUTTON_DISABLED_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event): # by convention, button pressing is signaled by handle_event returning True
        if self.is_enabled:
            if event.type == pygame.MOUSEMOTION:
                self.is_hovered = self.rect.collidepoint(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check for Alt key
                alt_down = False
                if hasattr(event, 'mod'):
                    alt_down = bool(event.mod & pygame.KMOD_ALT)
                else:
                    alt_down = bool(pygame.key.get_mods() & pygame.KMOD_ALT)
                self.alt_pressed = alt_down
                return self.rect.collidepoint(event.pos) # True only if the click was on this game button

class ToggleButton(Button):
    def handle_event(self, event): # returning True = button pressed
        if self.is_enabled and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.is_selected = not self.is_selected
            return True
        return super().handle_event(event)
