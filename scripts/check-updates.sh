#!/bin/bash

USERNAME=$(whoami)

# Validate that the user exists
if ! id "$USERNAME" &>/dev/null; then
    echo "Error: User '$USERNAME' does not exist."
    exit 1
fi

# Load environment variables from .env
ENV_FILE="/home/$USERNAME/Applications/photo-frame/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "Warning: .env file not found at $ENV_FILE. Proceeding without GITHUB_TOKEN."
fi

# Define working directory and service file path
WORKING_DIR="/home/$USERNAME/Applications/photo-frame"

# Check for updates on GitHub
# GitHub API Authentication
GITHUB_API_URL="https://api.github.com/repos"
REPO="cjennison/photo-frame"
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Warning: GITHUB_TOKEN is not set. API requests may be throttled (limited to 60 requests/hour)."
    AUTH_HEADER=""
else
    AUTH_HEADER="-H \"Authorization: token $GITHUB_TOKEN\""
fi

LOCAL_VERSION=$(cat "$WORKING_DIR/version.txt" 2>/dev/null || echo "0.0.0")

# Retry logic for fetching the latest version
MAX_RETRIES=5  # 12 attempts (60 seconds total with 5-second intervals)
RETRY_INTERVAL=5
LATEST_VERSION=""

for ((i=1; i<=MAX_RETRIES; i++)); do
    LATEST_VERSION=$(eval curl -s $AUTH_HEADER \
        "$GITHUB_API_URL/$REPO/releases/latest" | grep -Po '"tag_name": "\K.*?(?=")')
    echo "Result: $LATEST_VERSION"
    if [ -n "$LATEST_VERSION" ]; then
        break
    fi
    echo "Attempt $i/$MAX_RETRIES: Unable to determine the latest version. Retrying in $RETRY_INTERVAL seconds..."
    sleep $RETRY_INTERVAL
done

if [ -z "$LATEST_VERSION" ]; then
    echo "Error: Unable to fetch the latest version after $((MAX_RETRIES * RETRY_INTERVAL)) seconds."
    exit 0
fi

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

    # Ensure the target build directory exists and is empty
    mkdir -p "$WORKING_DIR/webapp/client/build"
    rm -rf "$WORKING_DIR/webapp/client/build/*"

    # Move the contents of webapp-client-build into the build directory
    mv "$WORKING_DIR/webapp-client-build/"* "$WORKING_DIR/webapp/client/build/"

    # Reinstall requirements
    source "$WORKING_DIR/venv/bin/activate"
    pip install -r "$WORKING_DIR/requirements.txt"
else
    echo "No updates available. Current version: $LOCAL_VERSION."
fi