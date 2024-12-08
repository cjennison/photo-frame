#!/bin/bash

# Variables
AZCOPY_URL="https://aka.ms/downloadazcopy-v10-linux-arm64"
AZCOPY_ARCHIVE="azcopy_linux_arm64.tar.gz"
REQUIRED_PACKAGES=("git" "curl" "unzip" "python3" "python3-venv")
REPO_URL="https://github.com/your-repo/photo_frame.git"
MAIN_SCRIPT="main.py"

# Update system and install required packages
echo "Updating system and installing required packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y ${REQUIRED_PACKAGES[@]}

# Check and install azcopy
if ! command -v azcopy &> /dev/null; then
  echo "AzCopy not found. Downloading and installing..."
  wget $AZCOPY_URL -O $AZCOPY_ARCHIVE
  tar -xvf $AZCOPY_ARCHIVE
  sudo mv azcopy_linux_arm64/azcopy /usr/local/bin
  rm -rf azcopy_linux_arm64 $AZCOPY_ARCHIVE
  echo "AzCopy installed successfully."
else
  echo "AzCopy is already installed."
fi

# Clone the project repository
echo "Cloning project repository..."
if [ ! -d "photo_frame" ]; then
  git clone $REPO_URL
else
  echo "Project repository already exists. Pulling latest changes..."
  cd photo_frame && git pull && cd ..
fi

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
cd photo_frame
if [ ! -d "venv" ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  else
    echo "requirements.txt not found. Please ensure dependencies are listed."
  fi
  deactivate
else
  echo "Virtual environment already exists."
fi

# Run the application
echo "Starting the application..."
source venv/bin/activate
python3 $MAIN_SCRIPT

deactivate
cd ..

# Final steps
echo "Setup and execution complete. Application is now running."