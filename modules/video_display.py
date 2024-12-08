import os
import cv2 # type: ignore
import sys
import pygame
from pygame.locals import * # type: ignore

def play_video(screen, clock, video_path, config, handle_keypress, draw_ui):
  if not os.path.exists(video_path):
    print(f"Error: Video '{video_path}' not found.")
    sys.exit(1)

  cap = cv2.VideoCapture(video_path)
  while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
      break
    
    frame = cv2.resize(frame, config["SCREEN_SIZE"])
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))

    screen.fill((0, 0, 0))
    screen.blit(frame, (0, 0))
    
    # UI Draw
    draw_ui(screen)
    pygame.display.flip()

    for event in pygame.event.get():
      if event.type == QUIT:
        cap.release()
      elif event.type == KEYDOWN and event.key == K_ESCAPE:
        cap.release()
      
      cancel_loop = False
      if hasattr(event, "key"):
        cancel_loop = handle_keypress(event.type, event.key)
      else:
        cancel_loop = handle_keypress(event, None, event)
      
      # Exit the dispaly loop if cancel_loop is True
      if cancel_loop:
        return
    
    
    clock.tick(30)

  cap.release()
