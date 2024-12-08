#!/bin/bash

# Variables

REQUIRED_PACKAGES=("curl" "unzip" "python3" "python3-venv")
MAIN_SCRIPT="main.py"

# Update system and install required packages
echo "Updating system and installing required packages..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y ${REQUIRED_PACKAGES[@]}

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
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

# Final steps
echo "Setup and execution complete. Application is now running."
