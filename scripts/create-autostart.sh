#!/bin/bash

#### Service Option
if [ $(id -u) -ne 0 ]; then
    echo "Error: This script must be run as root to create the service file."
    exit 1
fi

# Prompt for the username to run the service
read -p "Enter the username to run the service: " USERNAME

# Validate that the user exists
if ! id "$USERNAME" &>/dev/null; then
    echo "Error: User '$USERNAME' does not exist."
    exit 1
fi

# Define working directory and service file path
WORKING_DIR="/home/$USERNAME/Applications/photo-frame"
SERVICE_FILE="/etc/systemd/system/photo-frame.service"

# Create the systemd service file
echo "Creating service file $SERVICE_FILE..."

cat > "$SERVICE_FILE" <<EOL
[Unit]
Description=Photo Frame Application
After=network.target

[Service]
ExecStart=$WORKING_DIR/run.sh
WorkingDirectory=$WORKING_DIR
Restart=always
User=$USERNAME
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/$USERNAME/.Xauthority

[Install]
WantedBy=multi-user.target
EOL

# Set permissions for the service file
chmod 644 "$SERVICE_FILE"

# Reload systemd daemon and enable the service
systemctl daemon-reload
systemctl enable photo-frame.service

# Start the service
systemctl start photo-frame.service

echo "Service created and started successfully for user $USERNAME."
