from Xlib import X, display
import time
import sys
import os

def is_x_server_available():
  try:
    # Attempt to connect to the X server
    d = display.Display(os.getenv("DISPLAY", ":0"))
    d.close()
    return True
  except Exception as e:
    print(f"X server not available: {e}")
    return False
  
def wait_for_server_available():
  x_timeout = 60  # Maximum wait time in seconds
  x_interval = 5  # Time to wait between retries
  start_time = time.time()
  
  while not is_x_server_available():
    if time.time() - start_time > x_timeout:
        print("X server did not become available within the timeout period. Exiting...")
        sys.exit(1)
    print("Waiting for X server to become available...")
    time.sleep(x_interval)