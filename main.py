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
from classes.uicheckbox import UICheckbox
from utils.loadsvgs import load_svg_as_surface
from utils.loadfiles import get_unique_content_keys, load_files, load_metadata, write_options_json, read_options_json
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
FILTER_KEYS = {}

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

## ---------------- System ----------------

def write_new_options():
  options = {
    "ENABLE_SLIDESHOW": ENABLE_SLIDESHOW,
    "ENABLE_TRANSITION": ENABLE_TRANSITION,
    "FILTER_KEYS": FILTER_KEYS
  }
  
  write_options_json(options)

def get_options():
  global ENABLE_SLIDESHOW, ENABLE_TRANSITION, FILTER_KEYS
  options = read_options_json()
  current_filter_keys = FILTER_KEYS
  incoming_filter_keys = {}
  if options:
    ENABLE_SLIDESHOW = options.get("ENABLE_SLIDESHOW", True)
    ENABLE_TRANSITION = options.get("ENABLE_TRANSITION", True)
    incoming_filter_keys = options.get("FILTER_KEYS", {})
    
  # Merge incoming filter keys with current filter keys
  FILTER_KEYS = {**current_filter_keys, **incoming_filter_keys}

## ---------------- UI ----------------

### Buttons
def toggle_slideshow():
  global ENABLE_SLIDESHOW, UI_LAST_VISIBLE
  ENABLE_SLIDESHOW = not ENABLE_SLIDESHOW
  UI_LAST_VISIBLE = time.time()
  write_new_options()

def toggle_transition():
  global ENABLE_TRANSITION, UI_LAST_VISIBLE
  ENABLE_TRANSITION = not ENABLE_TRANSITION
  UI_LAST_VISIBLE = time.time()
  write_new_options()
  
def toggle_filter_key(key):
  print(f"Toggle filter key: {key}")
  global FILTER_KEYS, UI_LAST_VISIBLE
  FILTER_KEYS[key] = not FILTER_KEYS[key]
  UI_LAST_VISIBLE = time.time()
  write_new_options()

buttons = [
  UIButton((24, SCREEN_SIZES[SCREEN_SIZE][1] - 72, 48, 48), "", toggle_slideshow),
  UIButton((80, SCREEN_SIZES[SCREEN_SIZE][1] - 72, 200, 48), "", toggle_transition),
]

checkboxes = []

def display_splash(screen):  
  global splash_active, splash_start_time, splash_image
  return show_splash_overlay(screen, splash_image, splash_start_time)
  
def draw(screen):
  global splash_active
  if splash_active:
    splash_active = display_splash(screen)
  else:
    draw_ui(screen, buttons, checkboxes, {
      "UI_VISIBLE": UI_VISIBLE,
      "UI_LAST_VISIBLE": UI_LAST_VISIBLE,
      "ENABLE_SLIDESHOW": ENABLE_SLIDESHOW,
      "ENABLE_TRANSITION": ENABLE_TRANSITION
    }, SCREEN_SIZES[SCREEN_SIZE], RIGHT_TAP_AREA, loaded_icons, FILTER_KEYS, toggle_filter_key)

## ---------------- MAIN ----------------
def generate_content_order(images, videos):
  content_order = [("image", img) for img in images] + [("video", vid) for vid in videos]
  random.shuffle(content_order)
  return content_order

# Check if there exists any content in the content list that matches the filter keys
def check_any_content_matches(metadata, content_list, filter_keys):
  print(content_list, filter_keys)
  some_content_matches = False
  for _, media_path in content_list:
    if media_path in metadata and "contents" in metadata[media_path]:
      contents = metadata[media_path]["contents"]  # "dog,cat,beach"
      meta_contents_list = contents.split(",")
      
      missing_content = False
      for content in meta_contents_list: # dog in "dog", "cat"
        if content in filter_keys and filter_keys[content] == False:
          print(f"Content {content} is filtered out due to filter keys.")
          missing_content = True
          break
        
      if not missing_content:
        print(f"Content {contents} matches the filter keys.")
        some_content_matches = True
        break
        
  return some_content_matches

def main():
  global config, loaded_icons, splash_image_path, splash_image, FILTER_KEYS

  # Check for X server availability
  wait_for_server_available()

  # Initialize Pygame
  pygame.init()
  if FULL_SCREEN:
    screen = pygame.display.set_mode(SCREEN_SIZES[SCREEN_SIZE], pygame.FULLSCREEN | pygame.NOFRAME)
  else:
    screen = pygame.display.set_mode(SCREEN_SIZES[SCREEN_SIZE])
  pygame.display.set_caption("Digital Photo Frame")
  pygame.mouse.set_visible(not FULL_SCREEN)
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
  
  # Load icons
  loaded_icons = {
    key: load_svg_as_surface(path, (50, 50))  # Resize icons to 50x50
    for key, path in ICON_PATHS.items()
  }
  
  # #Download files
  load_files()
  
  # Load downloaded media
  IMAGES = [os.path.join(LOCAL_PHOTO_DIR, f) for f in os.listdir(LOCAL_PHOTO_DIR) if f.endswith(('.jpg', '.jpeg', '.png'))]
  VIDEOS = [os.path.join(LOCAL_VIDEO_DIR, f) for f in os.listdir(LOCAL_VIDEO_DIR) if f.endswith(('.mp4', '.avi', '.mov'))]
  
  metadata = load_metadata()
  FILTER_KEYS = get_unique_content_keys(metadata)
  print(metadata)
  
  # Set options
  get_options()
  
  ###### Run the main loop ######
  
  # Setup checkboxes
  checklist_x = 50  # X position for the checklist
  checklist_y = 50  # Starting Y position for the checklist
  item_height = 40  # Height of each checklist item
  for i, key in enumerate(FILTER_KEYS.keys()):
    rect = (checklist_x, checklist_y + i * item_height, 30, 30)
    checkboxes.append(UICheckbox(rect, key, key, toggle_filter_key))
  
  media_index = -1
  media_type = None  
  media_path = None
  
  # Prevents a double advance if the loop ends due to interruption
  triggered_button_event = False
  
  # Generate content order
  content_order = generate_content_order(IMAGES, VIDEOS) # [('video', 'path_to/video.mp4'), ('image', 'path_to/image.jpg')]
  def advance_media():
    nonlocal content_order
    nonlocal media_index, media_type, media_path 
    
    media_index += 1
    media_type, media_path = content_order[media_index % len(content_order)]
    print(f"Advancing to {media_type} {media_path}, index: {media_index}")
        
    # Check the metadata of this media
    if media_path in metadata and "contents" in metadata[media_path]:
      contents = metadata[media_path]["contents"]
      
      # Allow all photos with no contents
      if not contents:
        return True
      
      content_list = contents.split(",") # ["dog", "cat", "beach"]
      
      # Check if any content keys are filtered out
      content_filtered_out = False
      for content in content_list:
        if content in FILTER_KEYS and FILTER_KEYS[content] == False:
          content_filtered_out = True
          break
      
      if content_filtered_out:
        if check_any_content_matches(metadata, content_order, FILTER_KEYS):
          return advance_media()
        else:
          print("No more content matches the filter keys.")
  
    return True
  
  def handle_keypress(eventType, eventKey, event=None):
    global UI_VISIBLE, UI_LAST_VISIBLE, config
    nonlocal triggered_button_event
    
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
        print("Tapped right side")
        advance_media()
        triggered_button_event = True
        return True
      
      # Check button collision
      for button in buttons:
          button.handle_event(event)
      
      # Check button collision
      for checkbox in checkboxes:
          checkbox.handle_event(event)
        
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
        triggered_button_event = True
        return True
  
  print("Starting main loop...")
  advance_media()
  running = True
  while running:
    try:
      print(f"Displaying {media_type} {media_path}")
      triggered_button_event = False
      config = {
        "ENABLE_SLIDESHOW": ENABLE_SLIDESHOW,
        "ENABLE_TRANSITION": ENABLE_TRANSITION,
        "SCREEN_SIZE": SCREEN_SIZES[SCREEN_SIZE]
      }
      
      display_splash(screen)

      if media_type == "image" and media_path:
        display_photo(screen, clock, media_path, config, handle_keypress, draw)
      elif media_type == "video" and media_path:
        play_video(screen, clock, media_path, config, handle_keypress, draw)

      if ENABLE_SLIDESHOW and not triggered_button_event:
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
