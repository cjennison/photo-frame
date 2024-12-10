import pygame
import random
import sys
import time
import os
import cairosvg  # type: ignore

from pygame.locals import * # type: ignore
from modules.photo_display import display_photo
from modules.video_display import play_video  
from modules.draw_ui import draw_ui, show_splash_overlay, preload_splash_image
from classes.uibutton import UIButton
from utils.loadsvgs import load_svg_as_surface
from utils.loadfiles import load_files
from utils.checkdeps import wait_for_server_available

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

# FULL_SCREEN is false if the directory has src in it, otherwise its true
FULL_SCREEN = not "src" in os.getcwd()

# Configuration
ENABLE_SLIDESHOW = True
ENABLE_TRANSITION = True

UI_VISIBLE = True
UI_LAST_VISIBLE = time.time()

RIGHT_TAP_AREA = 1/6

config = {}
loaded_icons = {}

# Splash screen
splash_image_path = None
splash_image = None
splash_active = True
splash_start_time = time.time()

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

def display_splash(screen):  
  global splash_active, splash_start_time, splash_image
  return show_splash_overlay(screen, splash_image, splash_start_time)
  
def draw(screen):
  global splash_active
  if splash_active:
    splash_active = display_splash(screen)
  else:
    draw_ui(screen, buttons, {
      "UI_VISIBLE": UI_VISIBLE,
      "UI_LAST_VISIBLE": UI_LAST_VISIBLE,
      "ENABLE_SLIDESHOW": ENABLE_SLIDESHOW,
      "ENABLE_TRANSITION": ENABLE_TRANSITION
    }, SCREEN_SIZES[SCREEN_SIZE], RIGHT_TAP_AREA, loaded_icons)

## ---------------- MAIN ----------------
def main():
  global config, loaded_icons, splash_image_path, splash_image

  wait_for_server_available()

  pygame.init()
  if FULL_SCREEN:
    screen = pygame.display.set_mode(SCREEN_SIZES[SCREEN_SIZE], pygame.FULLSCREEN | pygame.NOFRAME)
  else:
    screen = pygame.display.set_mode(SCREEN_SIZES[SCREEN_SIZE])
  pygame.display.set_caption("Digital Photo Frame")
  pygame.mouse.set_visible(False)
  clock = pygame.time.Clock()
  
  # Preload splash image
  splash_folder = "splash"
  splash_files = [f for f in os.listdir(splash_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
  if not splash_files:
    print("No splash images found in the splash folder.")
    splash_image = None
  else:
    splash_image_path = os.path.join(splash_folder, random.choice(splash_files))
    splash_image = preload_splash_image(splash_image_path, SCREEN_SIZES[SCREEN_SIZE])

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
  last_played_media = None
  
  def advance_media():
    nonlocal media_index
    nonlocal media_type
    nonlocal last_played_media
    media_type = random.choice(["image", "video"])
    if media_type == "image":
      media_index = random.randint(0, len(IMAGES) - 1)
    elif media_type == "video":
      media_index = random.randint(0, len(VIDEOS) - 1)
      
    if last_played_media and last_played_media == (media_type, media_index):
      # If we've already played this media, skip it
      advance_media()
      return False
    
    last_played_media = (media_type, media_index)
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
      # print(f"Displaying {media_type} {media_index % len(IMAGES)}")
      config = {
        "ENABLE_SLIDESHOW": ENABLE_SLIDESHOW,
        "ENABLE_TRANSITION": ENABLE_TRANSITION,
        "SCREEN_SIZE": SCREEN_SIZES[SCREEN_SIZE]
      }
      
      display_splash(screen)

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
