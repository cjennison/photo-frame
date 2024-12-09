#!/bin/bash

USERNAME=$(whoami)

# Validate that the user exists
if ! id "$USERNAME" &>/dev/null; then
    echo "Error: User '$USERNAME' does not exist."
    exit 1
fi

# Define working directory and service file path
WORKING_DIR="/home/$USERNAME/Applications/photo-frame"

# Check for updates on GitHub
REPO="cjennison/photo-frame"
LOCAL_VERSION=$(cat "$WORKING_DIR/version.txt" 2>/dev/null || echo "0.0.0")
LATEST_VERSION=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")')

echo "Local version: $LOCAL_VERSION"
echo "v$LOCAL_VERSION == $LATEST_VERSION"
if [ "v$LOCAL_VERSION" != "$LATEST_VERSION" ]; then
    echo "New version available: $LATEST_VERSION. Updating..."

    # Download the latest release
    DOWNLOAD_URL=$(curl -s "https://api.github.com/repos/$REPO/releases/latest" | grep -Po '"tarball_url": "\K.*?(?=")')
    curl -L "$DOWNLOAD_URL" -o "$WORKING_DIR/latest.tar.gz"

    # Extract and overwrite files
    tar -xzf "$WORKING_DIR/latest.tar.gz" -C "$WORKING_DIR" --strip-components=1
    rm "$WORKING_DIR/latest.tar.gz"

    # Reinstall requirements
    source "$WORKING_DIR/venv/bin/activate"
    pip install -r "$WORKING_DIR/requirements.txt"
else
    echo "No updates available. Current version: $LOCAL_VERSION."
fi