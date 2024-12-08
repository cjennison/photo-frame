#!/bin/bash

# Variables
VERSION_FILE="version.txt"
if [ -f $VERSION_FILE ]; then
  LOCAL_VERSION=$(cat $VERSION_FILE | tr -d '\n')
else
  LOCAL_VERSION=""
fi

VERSION=$LOCAL_VERSION
WORKING_DIR="/home/$(whoami)/Applications/photo-frame-$VERSION"
RUN_SCRIPT="$WORKING_DIR/run.sh"
CRONTAB_BACKUP="/home/$(whoami)/crontab.bak"

# Create run.sh file
mkdir -p "$WORKING_DIR"
echo "Creating run.sh in $WORKING_DIR..."
cat > "$RUN_SCRIPT" <<EOL
#!/bin/bash
# Wait for the system to fully initialize
sleep 30
echo "Running as: \$(whoami)" > /home/$(whoami)/debug_crontab.log
env >> /home/$(whoami)/debug_crontab.log

# Set XDG_RUNTIME_DIR
export XDG_RUNTIME_DIR=/run/user/1000

# Navigate to the project directory
cd $WORKING_DIR

# Activate the virtual environment
source venv/bin/activate

# Run the Python script
python3 main.py >> /home/$(whoami)/app.log 2>&1
EOL

chmod +x "$RUN_SCRIPT"

# Remove existing crontab entries and add the new one
echo "Configuring crontab..."
crontab -l > "$CRONTAB_BACKUP" 2>/dev/null || true
(crontab -l 2>/dev/null | grep -v "$RUN_SCRIPT"; echo "@reboot $RUN_SCRIPT") | crontab -

# Final output
echo "run.sh created in $WORKING_DIR and crontab configured."