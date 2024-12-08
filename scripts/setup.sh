#!/bin/bash

# Variables
AZCOPY_URL="https://aka.ms/downloadazcopy-v10-linux-arm64"
AZCOPY_ARCHIVE="azcopy_linux_arm64.tar.gz"
REQUIRED_PACKAGES=("git" "curl" "unzip")

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
  git clone https://github.com/your-repo/photo_frame.git
else
  echo "Project repository already exists. Pulling latest changes..."
  cd photo_frame && git pull && cd ..
fi

# Final steps
echo "Setup complete. You can now navigate to the 'photo_frame' directory and start the application."