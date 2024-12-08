#!/bin/bash

# Variables
SERVICE_NAME="photo_frame"

# Disable auto-start for the service
echo "Disabling auto-start for $SERVICE_NAME service..."
sudo systemctl disable $SERVICE_NAME

# Verify the status of the service
echo "Verifying $SERVICE_NAME service status..."
systemctl is-enabled $SERVICE_NAME && echo "$SERVICE_NAME is still enabled." || echo "$SERVICE_NAME is now disabled."

echo "Auto-start for $SERVICE_NAME has been disabled. The service definition remains intact."
