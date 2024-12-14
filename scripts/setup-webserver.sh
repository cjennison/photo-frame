#!/bin/bash

SERVICE_NAME="photo-frame-webserver"
NODE_EXEC="/usr/bin/npm"
SERVER_SCRIPT="index.js"

LOG_DIR="/var/log/$SERVICE_NAME"
STDOUT_LOG="$LOG_DIR/webserver.log"
STDERR_LOG="$LOG_DIR/webserver-error.log"

# Ensure the script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root: sudo bash setup-webserver.sh"
  exit 1
fi

# Prompt for the username to run the service
read -p "Enter the username to run the service: " USERNAME

# Validate that the user exists
if ! id "$USERNAME" &>/dev/null; then
    echo "Error: User '$USERNAME' does not exist."
    exit 1
fi

WORKING_DIR="/home/$USERNAME/Applications/photo-frame/webapp"

# Create log directory
echo "Creating log directory at $LOG_DIR..."
mkdir -p "$LOG_DIR"
chown $USERNAME:$USERNAME "$LOG_DIR"

echo "Creating systemd service file at $SERVICE_FILE..."

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"

cat <<EOL > $SERVICE_FILE
[Unit]
Description=Node.js Web Server
After=network.target

[Service]
ExecStart=$NODE_EXEC run-install
WorkingDirectory=$WORKING_DIR
Restart=always
User=$USERNAME
Environment=NODE_ENV=production
StandardOutput=append:$STDOUT_LOG
StandardError=append:$STDERR_LOG

[Install]
WantedBy=multi-user.target
EOL

# Set permissions
chmod 644 $SERVICE_FILE
# Reload systemd, enable, and start the service
echo "Reloading systemd..."
systemctl daemon-reload

echo "Enabling the $SERVICE_NAME service to start on boot..."
systemctl enable $SERVICE_NAME

echo "Starting the $SERVICE_NAME service..."
systemctl start $SERVICE_NAME

# Confirm the service status
echo "Checking service status..."
systemctl status $SERVICE_NAME --no-pager

echo "Setup complete. Logs can be found at:"
echo "  Standard Output: $STDOUT_LOG"
echo "  Standard Error:  $STDERR_LOG"