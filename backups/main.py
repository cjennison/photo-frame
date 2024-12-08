# Test backup file for the photo frame project
# Video and Photo work correctly, but monolithic

import pygame
import sys
import os
import random
from pygame.locals import *
import time
import cv2 # type: ignore

# Image and screen configurations
IMAGES = [
    "pictures/willow1.jpg",
    "pictures/willow2.jpg",
    "pictures/willow3.jpg",
]

VIDEOS = [
    "videos/willow-video1.mp4",
]

SCREEN_SIZES = {
    "7inch": (800, 480),
    "10inch": (1280, 800),
    "15inch": (1920, 1080),
}

SCREEN_SIZE = "7inch"
PICTURE_FPS = 60
VIDEO_FPS = 30
ZOOM_DURATION = 10  # in seconds
TRANSLATE_DURATION = 10  # in seconds
TRANSLATE_DISTANCE = 0.1  # Translate by 10% of the image width

# Pygame initialization
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZES[SCREEN_SIZE])
pygame.display.set_caption("Digital Photo Frame")
clock = pygame.time.Clock()

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

def zoom_image(image, start_rect, zoom_factor):
    zoom_width = int(start_rect.width * zoom_factor)
    zoom_height = int(start_rect.height * zoom_factor)
    zoomed_rect = pygame.Rect(0, 0, zoom_width, zoom_height)
    zoomed_rect.center = start_rect.center
    zoomed_image = pygame.transform.smoothscale(image, (zoom_width, zoom_height))

    # Ensure the zoomed_rect stays centered relative to the screen
    screen_rect = screen.get_rect()
    cropped_rect = zoomed_rect.clip(screen_rect)
    cropped_rect.center = screen_rect.center
    cropped_image = zoomed_image.subsurface(cropped_rect)

    return cropped_image, cropped_rect

def translate_image(image, start_rect, translate_factor, direction="left"):
    # Pre-scale the image similar to zoom to fit the screen, with an additional scale to allow for translation without revealing the canvas
    zoom_factor = 1.2  # Zoom in by 20% to provide overflow for translation
    scaled_width = int(start_rect.width * zoom_factor)
    scaled_height = int(start_rect.height * zoom_factor)
    scaled_image = pygame.transform.smoothscale(image, (scaled_width, scaled_height))
    scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
    scaled_rect.center = start_rect.center
    
    # Apply translation
    translate_offset = int((scaled_rect.width - start_rect.width) * translate_factor)
    translated_rect = scaled_rect.copy()
    
    if direction == "left":
      translated_rect.x = -translate_offset
    elif direction == "right":
      translated_rect.x = translate_offset - (scaled_rect.width - start_rect.width)
      
    return scaled_image, translated_rect

def play_video(video_path):
    if not os.path.exists(video_path):
        print(f"Error: Video '{video_path}' not found.")
        sys.exit(1)
    
    cap = cv2.VideoCapture(video_path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.resize(frame, SCREEN_SIZES[SCREEN_SIZE])
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
        
        screen.fill((0, 0, 0))
        screen.blit(frame, (0, 0))
        pygame.display.flip()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == QUIT:
                cap.release()
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                cap.release()
                pygame.quit()
                sys.exit()
        
        clock.tick(VIDEO_FPS)
    
    cap.release()

def main():
    media_index = 0
    while True:
        # Randomly choose between image or video
        media_type = random.choice(["image", "video"])
        
        print(f"Displaying {media_type} {media_index % len(IMAGES)}")

        if media_type == "image":
            image_path = IMAGES[media_index % len(IMAGES)]
            image = load_image(image_path)
            start_rect = get_scaled_rect(image, screen)
            start_time = time.time()

            # Randomly choose between zoom or translate
            effect_type = random.choice(["zoom", "translate"])
            direction = random.choice(["left", "right"]) if effect_type == "translate" else ""
            
            print(f"Applying {effect_type} effect with direction: {direction}")

            while True:
                # Handle events
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                elapsed_time = time.time() - start_time

                if effect_type == "zoom":
                    # Calculate zoom factor
                    zoom_factor = 1 + (elapsed_time / ZOOM_DURATION) * 0.1  # Zoom in by 10% over ZOOM_DURATION seconds

                    # Break when zoom duration is reached
                    if elapsed_time >= ZOOM_DURATION:
                        break

                    # Zoom and draw image
                    zoomed_image, zoomed_rect = zoom_image(image, start_rect, zoom_factor)
                    screen.fill((0, 0, 0))
                    screen.blit(zoomed_image, zoomed_rect)

                elif effect_type == "translate":
                    # Calculate translate factor
                    translate_factor = (elapsed_time / TRANSLATE_DURATION)

                    # Break when translate duration is reached
                    if elapsed_time >= TRANSLATE_DURATION:
                        break

                    # Translate and draw image
                    if not isinstance(direction, str) or direction not in ["left", "right"]:
                        raise ValueError("Invalid direction value. Direction must be either 'left' or 'right'.")
                    translated_image, translated_rect = translate_image(image, start_rect, translate_factor, direction)
                    screen.fill((0, 0, 0))
                    screen.blit(translated_image, translated_rect)

                pygame.display.flip()

                # Cap the frame rate
                clock.tick(PICTURE_FPS)
        
        elif media_type == "video":
            video_path = VIDEOS[media_index % len(VIDEOS)]
            play_video(video_path)

        # Move to the next media
        media_index += 1

if __name__ == "__main__":
    main()
