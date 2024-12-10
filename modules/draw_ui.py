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

def show_splash(screen, clock):
  splash_folder = "splash"
  splash_files = [f for f in os.listdir(splash_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

  if not splash_files:
    print("No splash images found in the splash folder.")
    return

  splash_image_path = os.path.join(splash_folder, random.choice(splash_files))
  print("Displaying", splash_image_path)
  splash_image = pygame.image.load(splash_image_path).convert()
  
  start_rect = get_scaled_rect(splash_image, screen)
  splash_image, scaled_rect = scale_image(splash_image, start_rect)
  
  # Display splash screen for 5 seconds
  start_time = time.time()
  fade_duration = 2  # seconds for fade out

  while True:
    elapsed = time.time() - start_time

    if elapsed > 5 + fade_duration:
      break

    screen.fill((0, 0, 0))

    if elapsed <= 5:
      screen.blit(splash_image, scaled_rect)
    else:
      alpha = max(0, 255 - int(255 * (elapsed - 5) / fade_duration))
      temp_surface = splash_image.copy()
      temp_surface.set_alpha(alpha)
      screen.blit(temp_surface, scaled_rect)

    font = pygame.font.Font(None, 72)
    text_surface = font.render("I love you", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)
  