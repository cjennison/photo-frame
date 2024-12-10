import os
import json
import tkinter as tk
from tkinter import simpledialog
from azure.storage.blob import BlobServiceClient  # type: ignore # Azure Storage SDK
from dotenv import load_dotenv

load_dotenv()

def prompt_for_env_variable(env_var_name, prompt_text):
    import tkinter as tk
    from tkinter import simpledialog
    
    value = os.getenv(env_var_name)
    if not value:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        value = simpledialog.askstring("Input Required", prompt_text)
        if value:
            os.environ[env_var_name] = value
            # Ensure newline is correctly written
            with open(".env", "a", newline="\n") as env_file:
                env_file.write(f"{env_var_name}={value}\n")
        root.destroy()
    return value

if not os.getenv("AZURE_CONNECTION_STRING") or not os.getenv("AZURE_CONTAINER_NAME"):
  # Prompt user to provide both the Azure connection string and container name
  # and then write a .env file
  
  print("Please provide your Azure Storage connection string and container name.")
  print("You can find these details in the Azure Portal.")
  print("1. Navigate to your Azure Storage account.")
  print("2. Under Settings, select Access keys.")
  print("3. Copy the Connection string value.")
  print("4. Create a new container under Blob service and copy the name.")
  print("5. Paste the Connection string and Container name below.")
  
  AZURE_CONNECTION_STRING = prompt_for_env_variable("AZURE_CONNECTION_STRING", "Azure Storage Connection String: ")
  AZURE_CONTAINER_NAME = prompt_for_env_variable("AZURE_CONTAINER_NAME", "Azure Storage Container Name: ")
else:
  print("Azure Storage connection details found in .env file.")
  AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
  AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")

print(AZURE_CONNECTION_STRING, AZURE_CONTAINER_NAME)

LOCAL_PHOTO_DIR = "pictures"
LOCAL_VIDEO_DIR = "videos"
LOCAL_SPLASH_DIR = "splash"
METADATA_FILE = "metadata.json"

os.makedirs(LOCAL_PHOTO_DIR, exist_ok=True)
os.makedirs(LOCAL_VIDEO_DIR, exist_ok=True)
os.makedirs(LOCAL_SPLASH_DIR, exist_ok=True)

def load_files():
  metadata = {}
  try:
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

    for blob in container_client.list_blobs():
      local_path = None
      if blob.name.startswith("photos/"):
        local_path = os.path.join(LOCAL_PHOTO_DIR, os.path.basename(blob.name))
      elif blob.name.startswith("videos/"):
        local_path = os.path.join(LOCAL_VIDEO_DIR, os.path.basename(blob.name))
      elif blob.name.startswith("splash/"):
        local_path = os.path.join(LOCAL_SPLASH_DIR, os.path.basename(blob.name))

      if local_path:
        if not os.path.exists(local_path):
          with open(local_path, "wb") as file:
            print(f"Downloading {blob.name} to {local_path}")
            file.write(container_client.download_blob(blob).readall())
        else:
          print(f"Skipping {blob.name}, already exists at {local_path}")

        # Explicitly fetch metadata for each blob
        blob_client = container_client.get_blob_client(blob.name)
        blob_metadata = blob_client.get_blob_properties().metadata
        
        # Save metadata
        if "contents" in blob_metadata:
          metadata[local_path] = { "contents": blob_metadata["contents"] }
    
    # Save metadata locally to a JSON file
    with open(METADATA_FILE, "w") as meta_file:
        json.dump(metadata, meta_file, indent=4)
        print(f"Metadata saved to {METADATA_FILE}")
          
  except Exception as e:
    print(f"Error downloading media from Azure: {e}")
    
def load_metadata():
    """Load metadata from the local JSON file."""
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, "r") as meta_file:
            return json.load(meta_file)
    return {}

def get_unique_content_keys(metadata):
  if not metadata:
    return {}
  # iterate over the metadata and return a dictionary of unique content keys, all are defaulted to true
  # metadata.contents example: "contents": "people,beach,sky"
  # expected result: { "people": True, "beach": True, "sky": True }
  unique_content_keys = {}
  for meta in metadata.values():
    if "contents" not in meta:
      continue
    contents = meta["contents"].split(",")
    for content in contents:
      unique_content_keys[content] = True
    
  return unique_content_keys

def write_options_json(options={}):
  with open("options.json", "w") as options_file:
    json.dump(options, options_file, indent=2)
    
def read_options_json():
  if os.path.exists("options.json"):
    with open("options.json", "r") as options_file:
      return json.load(options_file)
  return {}