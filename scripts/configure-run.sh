#!/bin/bash

# Variables
WORKING_DIR="/home/$(whoami)/Applications/photo-frame"
RUN_SCRIPT="$WORKING_DIR/run.sh"
CRONTAB_BACKUP="/home/$(whoami)/crontab.bak"

# Create run.sh file
mkdir -p "$WORKING_DIR"
echo "Creating run.sh in $WORKING_DIR..."
cat > "$RUN_SCRIPT" <<'EOL'
#!/bin/bash
# Function to check if a service is running
is_service_active() {
  systemctl is-active --quiet "$1"
}

# Function to check if a directory exists
is_directory_ready() {
  [ -d "$1" ]
}

# Wait for essential services (e.g., networking, graphical interface)
echo "Checking if essential services are active..."
for service in networking dbus; do
  echo "Checking if $service service is active..."
  until is_service_active "$service"; do
    echo "$service service is not active. Waiting..."
    sleep 5
  done
  echo "$service service is active."
done

# Wait for the project directory to become available
PROJECT_DIR="/home/$(whoami)/Applications/photo-frame"
echo "Checking if project directory $PROJECT_DIR is available..."
until is_directory_ready "$PROJECT_DIR"; do
  echo "Project directory $PROJECT_DIR is not available. Waiting..."
  sleep 5
done
echo "Project directory $PROJECT_DIR is available."


echo "Checking if user directory XDG_RUNTIME_DIR is available..."
until is_directory_ready "/run/user/$(id -u)"; do
  echo "User directory /run/user/$(id -u) is not available. Waiting..."
  sleep 5
done

echo "Running as: $(whoami)" > /home/$(whoami)/debug_photo_frame.log
env >> /home/$(whoami)/debug_photo_frame.log

# Set XDG_RUNTIME_DIR
export XDG_RUNTIME_DIR=/run/user/1000

# Navigate to the project directory
cd $PROJECT_DIR

# Activate the virtual environment
source venv/bin/activate

# Check for updates
source scripts/check-updates.sh

# Force reinstall cairosvg
# Note: This works. I don't know why. But it works.
pip install cairosvg

# Run the Python script
python3 main.py >> /home/$(whoami)/app.log 2>&1
EOL

chmod +x "$RUN_SCRIPT"

#### CRONTAB OPTION
# Remove existing crontab entries and add the new one
# echo "Configuring crontab..."
#crontab -l > "$CRONTAB_BACKUP" 2>/dev/null || true
# (crontab -l 2>/dev/null | grep -v "$RUN_SCRIPT"; echo "@reboot $RUN_SCRIPT") | crontab -

# Final output
# echo "run.sh created in $WORKING_DIR and crontab configured."