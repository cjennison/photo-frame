# ui_draw.py
import pygame
import time
from utils.loadsvgs import load_svg_as_surface

def draw_transparent_rect(screen, rect, color, alpha):
    # Create a new surface with the same dimensions as the rectangle
    temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    # Fill the surface with the color and alpha
    temp_surface.fill((*color, alpha))
    # Blit this surface onto the screen at the rectangle's position
    screen.blit(temp_surface, (rect.x, rect.y))

def draw_icon(screen, icon, position):
    if icon:
        screen.blit(icon, position)

def draw_ui(screen, buttons, ui_state, screen_size, right_tap_area, loaded_icons):
    # Hide the UI after 5 seconds
    if ui_state['UI_LAST_VISIBLE'] and time.time() - ui_state['UI_LAST_VISIBLE'] > 5:
        ui_state['UI_VISIBLE'] = False

    if not ui_state['UI_VISIBLE']:
        return

    font = pygame.font.Font(None, 36)
    transition_text = "Transitions: On" if ui_state['ENABLE_TRANSITION'] else "Transitions: Off"
    buttons[1].text = transition_text

    for button in buttons:
        button.draw(screen, font)

    # Draw right side tap area
    rect = pygame.Rect(
        screen_size[0] - screen_size[0] * right_tap_area,
        0,
        screen_size[0] * right_tap_area,
        screen_size[1]
    )
    color = (0, 0, 0)  # Black
    alpha = 128  # 50% transparency
    draw_transparent_rect(screen, rect, color, alpha)

    # Icons
    draw_icon(screen, loaded_icons.get("skip"), (screen_size[0] - screen_size[0] * right_tap_area + 36, screen_size[1] / 2 - 24))
    draw_icon(screen, loaded_icons.get("play" if ui_state['ENABLE_SLIDESHOW'] else "pause"), (24, screen_size[1] - 72))
