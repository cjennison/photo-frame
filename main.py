import pygame
import random
import sys
import time
import os
import cairosvg  # type: ignore

from pygame.locals import * # type: ignore
from modules.photo_display import display_photo
from modules.video_display import play_video  
from classes.uibutton import UIButton
from utils.loadsvgs import load_svg_as_surface
from utils.loadfiles import load_files

SCREEN_SIZES = {
  "7inch": (800, 480),
  "10inch": (1280, 800),
  "15inch": (1920, 1080),
}

SCREEN_SIZE = "7inch"

LOCAL_PHOTO_DIR = "pictures"
LOCAL_VIDEO_DIR = "videos"
IMAGES = []
VIDEOS = []

ICON_PATHS = {
  "play": "icons/play.svg",
  "pause": "icons/pause.svg",
  "skip": "icons/skip.svg"
}

FULL_SCREEN = True

# Configuration
ENABLE_SLIDESHOW = True
ENABLE_TRANSITION = True

UI_VISIBLE = True
UI_LAST_VISIBLE = time.time()

RIGHT_TAP_AREA = 1/6

config = {}
loaded_icons = {}

## ---------------- UI ----------------

### Buttons
def toggle_slideshow():
  global ENABLE_SLIDESHOW, ui_last_shown
  ENABLE_SLIDESHOW = not ENABLE_SLIDESHOW
  ui_last_shown = time.time()

def toggle_transition():
  global ENABLE_TRANSITION, ui_last_shown
  ENABLE_TRANSITION = not ENABLE_TRANSITION
  ui_last_shown = time.time()

buttons = [
  UIButton((24, SCREEN_SIZES[SCREEN_SIZE][1] - 72, 48, 48), "", toggle_slideshow),
  UIButton((80, SCREEN_SIZES[SCREEN_SIZE][1] - 72, 200, 48), "", toggle_transition),
]

## Tap Ares
def draw_transparent_rect(screen, rect, color, alpha):
  # Create a new surface with the same dimensions as the rectangle
  temp_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
  # Fill the surface with the color and alpha
  temp_surface.fill((*color, alpha))
  # Blit this surface onto the screen at the rectangle's position
  screen.blit(temp_surface, (rect.x, rect.y))

## Icons
def draw_icon(screen, icon_key, position):
  icon = loaded_icons.get(icon_key)
  if icon:
    screen.blit(icon, position)

# UI DRAW LOOP
def draw_ui(screen, buttons):
  global UI_VISIBLE, UI_LAST_VISIBLE, ENABLE_SLIDESHOW, ENABLE_TRANSITION
  transition_text = "Transitions: On" if ENABLE_TRANSITION else "Transitions: Off"
  
  # Hide the UI after 5 seconds
  if UI_LAST_VISIBLE and time.time() - UI_LAST_VISIBLE > 5:
    UI_VISIBLE = False
      
  if not UI_VISIBLE:
    return
  font = pygame.font.Font(None, 36)

  buttons[1].text = transition_text
  
  for button in buttons:
    button.draw(screen, font)
    
  # Draw right side tap area
  rect = pygame.Rect(
    SCREEN_SIZES[SCREEN_SIZE][0] - SCREEN_SIZES[SCREEN_SIZE][0] * RIGHT_TAP_AREA, 
    0, 
    SCREEN_SIZES[SCREEN_SIZE][0] * RIGHT_TAP_AREA,
    SCREEN_SIZES[SCREEN_SIZE][1])  # Rectangle dimensions
  color = (0, 0, 0)  # Black
  alpha = 128  # 50% transparency
  draw_transparent_rect(screen, rect, color, alpha)
  
  # Icons
  draw_icon(screen, "skip", (SCREEN_SIZES[SCREEN_SIZE][0] - SCREEN_SIZES[SCREEN_SIZE][0] * RIGHT_TAP_AREA + 36, SCREEN_SIZES[SCREEN_SIZE][1] / 2 - 24))

  # Display Play or Pause depending
  draw_icon(screen, "play" if ENABLE_SLIDESHOW else "pause", (24, SCREEN_SIZES[SCREEN_SIZE][1] - 72))

def draw(screen):
  draw_ui(screen, buttons)
  
## ---------------- MAIN ----------------
def main():
  global config, loaded_icons

  print("Starting photo frame...")

  pygame.init()
  if FULL_SCREEN:
    screen = pygame.display.set_mode(SCREEN_SIZES[SCREEN_SIZE], pygame.FULLSCREEN | pygame.NOFRAME)
  else:
    screen = pygame.display.set_mode(SCREEN_SIZES[SCREEN_SIZE])
  pygame.display.set_caption("Digital Photo Frame")
  clock = pygame.time.Clock()
  
  loaded_icons = {
    key: load_svg_as_surface(path, (50, 50))  # Resize icons to 50x50
    for key, path in ICON_PATHS.items()
  }
  
  # #Download files
  load_files()
  
  # Load downloaded media
  IMAGES = [os.path.join(LOCAL_PHOTO_DIR, f) for f in os.listdir(LOCAL_PHOTO_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
  VIDEOS = [os.path.join(LOCAL_VIDEO_DIR, f) for f in os.listdir(LOCAL_VIDEO_DIR) if f.endswith(('.mp4', '.avi', '.mov'))]
  
  media_index = -1
  media_type = None
  
  def advance_media():
    nonlocal media_index
    nonlocal media_type
    media_type = random.choice(["image", "video"])
    media_index += 1
    return True
  
  def handle_keypress(eventType, eventKey, event=None):
    global UI_VISIBLE, UI_LAST_VISIBLE, config
    
    # MouseDown events require special handling
    if event and event.type == MOUSEBUTTONDOWN:
      mouse_x, mouse_y = pygame.mouse.get_pos() # omit X position
      print(f"Mouse clicked at {mouse_y}")
      # Handle show UI
      if mouse_y >= SCREEN_SIZES[SCREEN_SIZE][1] * 1 / 3:  # Bottom 3rd
        UI_VISIBLE = True
        UI_LAST_VISIBLE = time.time()
        
      # Handle tap right side
      if mouse_x >= SCREEN_SIZES[SCREEN_SIZE][0] - SCREEN_SIZES[SCREEN_SIZE][0] * RIGHT_TAP_AREA:  # Right 5th
        print("Next media")
        advance_media()
        return True
      
      # Check button collision
      for button in buttons:
          button.handle_event(event)
        
    if eventType == QUIT:
      print("Exiting...")
      pygame.quit()
      sys.exit()
    if eventType == KEYDOWN:
      if eventKey == K_ESCAPE:
        pygame.quit()
        sys.exit()
      elif eventKey == K_RIGHT:
        print("Next media")
        advance_media()
        return True
  
  advance_media()
  running = True
  while running:
    try:
      print(f"Displaying {media_type} {media_index % len(IMAGES)}")
      config = {
        "ENABLE_SLIDESHOW": ENABLE_SLIDESHOW,
        "ENABLE_TRANSITION": ENABLE_TRANSITION,
        "SCREEN_SIZE": SCREEN_SIZES[SCREEN_SIZE]
      }

      if media_type == "image":
        image_path = IMAGES[media_index % len(IMAGES)]
        display_photo(screen, clock, image_path, config, handle_keypress, draw)
      elif media_type == "video":
        video_path = VIDEOS[media_index % len(VIDEOS)]
        play_video(screen, clock, video_path, config, handle_keypress, draw)

      if ENABLE_SLIDESHOW:
        advance_media()
    except SystemExit:
      running = False
      pygame.quit()
      sys.exit()
    except Exception as e:
      print(f"Exception: {e}")
      running = False
      
if __name__ == "__main__":
  main()
