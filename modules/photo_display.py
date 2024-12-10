import pygame
import sys
import os
import time
import random

from pygame.locals import * # type: ignore

ZOOM_DURATION = 10  # in seconds
TRANSLATE_DURATION = 10  # in seconds

def load_image(image_path):
  if not os.path.exists(image_path):
    print(f"Error: Image '{image_path}' not found.")
    sys.exit(1)
  return pygame.image.load(image_path).convert()

def get_scaled_rect(image, screen):
  img_width, img_height = image.get_size()
  screen_width, screen_height = screen.get_size()
  img_aspect = img_width / img_height
  screen_aspect = screen_width / screen_height

  if img_aspect > screen_aspect:
    scale_height = screen_height
    scale_width = int(scale_height * img_aspect)
  else:
    scale_width = screen_width
    scale_height = int(scale_width / img_aspect)

  scaled_rect = pygame.Rect(0, 0, scale_width, scale_height)
  scaled_rect.center = (screen_width // 2, screen_height // 2)
  return scaled_rect

def scale_image(image, start_rect, zoom_factor=1.2):
  zoom_width = int(start_rect.width * zoom_factor)
  zoom_height = int(start_rect.height * zoom_factor)
  zoomed_rect = pygame.Rect(0, 0, zoom_width, zoom_height)
  zoomed_rect.center = start_rect.center
  zoomed_image = pygame.transform.smoothscale(image, (zoom_width, zoom_height))
  
  return zoomed_image, zoomed_rect

def zoom_image(image, start_rect, zoom_factor, screen, enable_effects):
  if (not enable_effects):
    zoomed_image, zoomed_rect = scale_image(image, start_rect)
    return zoomed_image, zoomed_rect
  else:
    zoomed_image, zoomed_rect = scale_image(image, start_rect, zoom_factor)

  # Ensure the zoomed_rect stays centered relative to the screen
  screen_rect = screen.get_rect()
  cropped_rect = zoomed_rect.clip(screen_rect)
  cropped_rect.center = screen_rect.center
  cropped_image = zoomed_image.subsurface(cropped_rect)

  return cropped_image, cropped_rect

def translate_image(image, start_rect, translate_factor, direction, enable_effects):
  scaled_image, scaled_rect = scale_image(image, start_rect)
  if (not enable_effects):
    return scaled_image, scaled_rect
  
  # Apply translation
  translate_offset = int((scaled_rect.width - start_rect.width) * translate_factor)
  translated_rect = scaled_rect.copy()
    
  if direction == "left":
    translated_rect.x = -translate_offset
  elif direction == "right":
    translated_rect.x = translate_offset - (scaled_rect.width - start_rect.width)
      
  return scaled_image, translated_rect

def display_photo(screen, clock, image_path, config, handle_keypress, draw_ui):
  image = load_image(image_path)
  start_rect = get_scaled_rect(image, screen)
  start_time = time.time()

  # Randomly choose between zoom or translate
  effect_type = random.choice(["zoom", "translate"])
  direction = random.choice(["left", "right"]) if effect_type == "translate" else ""

  while True:
    elapsed_time = time.time() - start_time

    if effect_type == "zoom":
      zoom_factor = 1 + (elapsed_time / ZOOM_DURATION) * 0.1
      if elapsed_time >= ZOOM_DURATION:
        break
      # Zoom and draw image
      zoomed_image, zoomed_rect = zoom_image(image, start_rect, zoom_factor, screen, config["ENABLE_TRANSITION"])
      screen.fill((0, 0, 0))
      screen.blit(zoomed_image, zoomed_rect)

    elif effect_type == "translate":
      translate_factor = (elapsed_time / TRANSLATE_DURATION)
      if elapsed_time >= TRANSLATE_DURATION:
        break
      translated_image, translated_rect = translate_image(image, start_rect, translate_factor, direction, config["ENABLE_TRANSITION"])
      screen.fill((0, 0, 0))
      screen.blit(translated_image, translated_rect)
   
    # UI Draw
    draw_ui(screen)
    pygame.display.flip()
    
    for event in pygame.event.get():
      print(event)
      cancel_loop = False
      if hasattr(event, "key"):
        cancel_loop = handle_keypress(event.type, event.key)
      else:
        cancel_loop = handle_keypress(event, None, event)
      
      # Exit the dispaly loop if cancel_loop is True
      if cancel_loop:
        return
      
    clock.tick(60)