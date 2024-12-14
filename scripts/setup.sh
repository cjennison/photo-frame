#!/bin/bash

# Variables

REQUIRED_PACKAGES=("curl" "unzip" "python3" "python3-venv" "npm" "nodejs")
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

# Log the Raspberry Pi's current local IP address
echo "Fetching current Raspberry Pi IP address..."
PI_IP=$(hostname -I | awk '{print $1}')
if [ -z "$PI_IP" ]; then
    echo "Unable to determine IP address."
else
    echo "Your Raspberry Pi IP address is: http://$PI_IP:3000"
fi

chmod +x scripts/setup-webserver.sh
chmod +x scripts/create-autostart.sh

# Webserver instructions
echo "Installing web-server dependencies..."
npm install --prefix ./webapp

echo "To run the web-server, run the following command:"
echo "sudo source scripts/setup-webserver.sh"

# Ask the user if they want to run the program now
echo "Setup complete. Would you like to start the system now? (y/n)"
read -r RUN_NOW

if [ "$RUN_NOW" != "y" ]; then
  echo "Starting application..."
  source venv/bin/activate
  python3 $MAIN_SCRIPT
fi
