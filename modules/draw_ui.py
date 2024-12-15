# ui_draw.py
import pygame
import time
import os
import random
from utils.loadsvgs import load_svg_as_surface
from modules.photo_display import get_scaled_rect, scale_image
from dotenv import load_dotenv

load_dotenv()

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
        
def draw_filter_checklist(screen, font, filter_keys, toggle_filter_key):
  checklist_x = 50  # X position for the checklist
  checklist_y = 50  # Starting Y position for the checklist
  item_height = 40  # Height of each checklist item

  for i, (key, value) in enumerate(filter_keys.items()):
    # Draw a checkbox
    checkbox_rect = pygame.Rect(checklist_x, checklist_y + i * item_height, 30, 30)
    pygame.draw.rect(screen, (255, 255, 255), checkbox_rect, 2)

    if value:  # If the filter is active, fill the checkbox
      pygame.draw.rect(screen, (255, 255, 255), checkbox_rect)

    # Draw the key label
    label_surface = font.render(key, True, (255, 255, 255))
    screen.blit(label_surface, (checklist_x + 40, checklist_y + i * item_height))

    # Handle mouse click to toggle
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    if mouse_click[0] and checkbox_rect.collidepoint(mouse_x, mouse_y):
      toggle_filter_key(key)

def draw_ui(screen, buttons, checkboxes, ui_state, screen_size, right_tap_area, loaded_icons, filter_keys, toggle_filter_key):
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
        
    for checkbox in checkboxes:
        checkbox.draw(screen, font, filter_keys[checkbox.key])

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
    """
    Load and scale the splash image to fill the screen while maintaining aspect ratio.
    If necessary, crop the image to remove black bars.
    """
    splash_image = pygame.image.load(splash_image_path).convert()
    image_width, image_height = splash_image.get_size()
    screen_width, screen_height = screen_size

    # Calculate aspect ratios
    image_aspect = image_width / image_height
    screen_aspect = screen_width / screen_height

    # Determine scaling factor to fill the screen
    if image_aspect > screen_aspect:
        # Image is wider than the screen
        scale_factor = screen_height / image_height
    else:
        # Image is taller than or fits the screen width
        scale_factor = screen_width / image_width

    # Scale the image
    new_width = int(image_width * scale_factor)
    new_height = int(image_height * scale_factor)
    scaled_image = pygame.transform.scale(splash_image, (new_width, new_height))

    # Calculate cropping rectangle to center the image
    crop_x = (new_width - screen_width) // 2
    crop_y = (new_height - screen_height) // 2
    cropped_image = scaled_image.subsurface((crop_x, crop_y, screen_width, screen_height))

    return cropped_image

def show_splash_overlay(screen, splash_image, start_time, duration=7, fade_duration=4):
  text = os.getenv("SPLASH_MESSAGE")
  if not text:
    text = "EPIPhoto Frame"
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
  text_surface = font.render(text, True, (255, 255, 255))
  text_surface.set_alpha(alpha)
  text_rect = text_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
  screen.blit(text_surface, text_rect)

  return True  # Splash is still active
  
def show_first_run(screen, splash_image, start_time):
    # Text content
    text1 = "Welcome to the EPIPhoto Frame!"
    text2 = "Tap the bottom of the screen to open the UI."
    text3 = "You can change settings, skip photos, and more."
    text4 = os.getenv("CUSTOM_MESSAGE")
    if not text4:
        text4 = "Enjoy your memories!"

    # Font and colors
    font = pygame.font.Font(None, 48)
    text_color = (255, 255, 255)
    
    # Timing configuration (in seconds)
    phase1_duration = 10.0   # total time for text1,2,3 sequence
    fade_out_123 = 2.0      # fade out time for first three texts
    phase3_duration = 10.0  # time to show text4 and image
    fade_out_4 = 2.0        # fade out time for text4 and image

    # Calculate elapsed time
    elapsed = time.time() - start_time
    
    # Calculate phase boundaries
    phase1_end = phase1_duration           # 5s
    phase2_end = phase1_end + fade_out_123 # 6s
    phase3_end = phase2_end + phase3_duration # 16s
    phase4_end = phase3_end + fade_out_4   # 18s total
    
    # If we've exceeded the entire sequence time, return False
    if elapsed > phase4_end:
        return False

    # Clear screen
    screen.fill((0,0,0))

    if elapsed < phase2_end:
        # During phases 1 and 2, do not show splash 
        splash_alpha = 0
    elif elapsed < phase3_end:
        # Phase 3: splash fully visible
        splash_alpha = 255
    else:
        # Phase 4: fade out splash
        fade_elapsed = elapsed - phase3_end
        fade_fraction = fade_elapsed / fade_out_4
        splash_alpha = max(0, 255 - int(255 * fade_fraction))
    
    # Draw the splash image with the calculated alpha
    splash_surface = splash_image.copy()
    splash_surface.set_alpha(splash_alpha)
    screen.blit(splash_surface, (0, 0))

    # Phase 1: Show texts 1,2,3 in sequence
    # 0-1s: text1
    # 1-2s: text1, text2
    # 2-5s: text1, text2, text3
    # Then 5-6s fade out these three texts
    if elapsed < phase2_end:
        # Determine alpha for texts 1-3 based on whether we are in fade-out period
        if elapsed < phase1_end:
            # Before 5s: texts fully opaque
            alpha_123 = 255
        else:
            # In the fade-out window from 5s to 6s
            fade_fraction = (elapsed - phase1_end) / fade_out_123
            alpha_123 = max(0, 255 - int(255 * fade_fraction))

        # Conditions to show each text
        show_text1 = (elapsed >= 1.0)
        show_text2 = (elapsed >= 5.0)
        show_text3 = (elapsed >= 8.0)

        y_pos = screen.get_height() // 2 - 50
        line_spacing = 60

        if show_text1:
            surf1 = font.render(text1, True, text_color)
            surf1.set_alpha(alpha_123)
            rect1 = surf1.get_rect(center=(screen.get_width()//2, y_pos))
            screen.blit(surf1, rect1)

        if show_text2:
            surf2 = font.render(text2, True, text_color)
            surf2.set_alpha(alpha_123)
            rect2 = surf2.get_rect(center=(screen.get_width()//2, y_pos + line_spacing))
            screen.blit(surf2, rect2)

        if show_text3:
            surf3 = font.render(text3, True, text_color)
            surf3.set_alpha(alpha_123)
            rect3 = surf3.get_rect(center=(screen.get_width()//2, y_pos + 2*line_spacing))
            screen.blit(surf3, rect3)

    else:
        # Phase 3 and 4: Show text4 centered
        if elapsed < phase3_end:
            # text4 fully visible
            alpha_4 = 255
        else:
            # fading out text4
            fade_elapsed = elapsed - phase3_end
            fade_fraction = fade_elapsed / fade_out_4
            alpha_4 = max(0, 255 - int(255 * fade_fraction))

        surf4 = font.render(text4, True, text_color)
        surf4.set_alpha(alpha_4)
        rect4 = surf4.get_rect(center=(screen.get_width()//2, 50))
        screen.blit(surf4, rect4)
    
    return True