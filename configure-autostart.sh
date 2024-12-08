#!/bin/bash

# Variables
SERVICE_NAME="photo_frame"
PYTHON_EXEC="$(which python3)"
SCRIPT_PATH="/home/$(whoami)/src/photo-frame/main.py"  # Replace with the actual path
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
USER_NAME="$(whoami)"
WORKING_DIR="$(dirname $SCRIPT_PATH)"

chmod +x SCRIPT_PATH

# Create systemd service file
echo "Creating systemd service file at $SERVICE_FILE..."
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Photo Frame Application
After=network.target

[Service]
ExecStart=$PYTHON_EXEC $SCRIPT_PATH
WorkingDirectory=$WORKING_DIR
Restart=always
User=$USER_NAME
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$USER_NAME/.Xauthority
StandardInput=tty
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd, enable and start the service
echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Enabling $SERVICE_NAME service..."
sudo systemctl enable $SERVICE_NAME

# Start the service
echo "Starting $SERVICE_NAME service..."
sudo systemctl start $SERVICE_NAME

# Check service status
echo "Checking $SERVICE_NAME service status..."
systemctl status $SERVICE_NAME
