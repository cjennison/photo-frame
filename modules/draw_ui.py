# ui_draw.py
import pygame
import time
import os
import random
from utils.loadsvgs import load_svg_as_surface
from modules.photo_display import get_scaled_rect, scale_image

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

def preload_splash_image(splash_image_path, screen_size):
  splash_image = pygame.image.load(splash_image_path).convert()
  return pygame.transform.scale(splash_image, screen_size)

def show_splash_overlay(screen, splash_image, start_time, duration=7, fade_duration=4):
  elapsed = time.time() - start_time
  alpha = 255
  if elapsed > duration + fade_duration:
    return False  # Splash duration has ended

  if elapsed <= duration:
    screen.blit(splash_image, (0, 0))
  else:
    alpha = max(0, 255 - int(255 * (elapsed - duration) / fade_duration))
    temp_surface = splash_image.copy()
    temp_surface.set_alpha(alpha)
    screen.blit(temp_surface, (0, 0))

  font = pygame.font.Font(None, 72)
  text_surface = font.render("I love you", True, (255, 255, 255))
  text_surface.set_alpha(alpha)
  text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
  screen.blit(text_surface, text_rect)

  return True  # Splash is still active
  