#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
  source .env
else
  echo "Error: .env file not found. Please create one with SAS_TOKEN defined."
  exit 0
fi


# Variables
PROJECT_NAME="photo_frame"
VERSION_FILE="version.txt"
LOCAL_BUILD_DIR="build"
AZURE_CONTAINER="builds"
SAS_TOKEN="$SAS_TOKEN"  # SAS token for authentication

# Check if azcopy is installed
if ! command -v azcopy &> /dev/null; then
  echo "Error: azcopy command not found. Please install azcopy before running this script."
  exit 1
fi

# Fetch the latest version from Azure
REMOTE_VERSION_FILE="https://photoframejennison.blob.core.windows.net/$AZURE_CONTAINER/version.txt?$SAS_TOKEN"
LATEST_VERSION=$(curl -s "$REMOTE_VERSION_FILE")

if [ -z "$LATEST_VERSION" ]; then
  echo "Error: Could not fetch the latest version from Azure."
  return
fi

# Check local version
if [ -f $VERSION_FILE ]; then
  LOCAL_VERSION=$(cat $VERSION_FILE | tr -d '\n')
else
  LOCAL_VERSION=""
fi

# Compare versions
if [ "$LATEST_VERSION" == "$LOCAL_VERSION" ]; then
  echo "You are already using the latest version: $LATEST_VERSION"
  return
else
  echo "New version available: $LATEST_VERSION (Current: $LOCAL_VERSION)"
fi

# Download the latest build
REMOTE_BUILD_FILE="https://photoframejennison.blob.core.windows.net/$AZURE_CONTAINER/${PROJECT_NAME}_$LATEST_VERSION.zip?$SAS_TOKEN"
LOCAL_BUILD_FILE="$LOCAL_BUILD_DIR/${PROJECT_NAME}_$LATEST_VERSION.zip"

mkdir -p $LOCAL_BUILD_DIR

echo "Downloading the latest build..."
azcopy copy "$REMOTE_BUILD_FILE" "$LOCAL_BUILD_FILE"

if [ $? -ne 0 ]; then
  echo "Error: Failed to download the latest build."
  return
fi

# Extract the build
echo "Extracting the latest build..."
unzip -o "$LOCAL_BUILD_FILE" -d "$LOCAL_BUILD_DIR"

if [ $? -ne 0 ]; then
  echo "Error: Failed to extract the latest build."
  return
fi

# Update the local version file
echo "$LATEST_VERSION" > $VERSION_FILE

# Clean up
rm "$LOCAL_BUILD_FILE"

echo "Update to version $LATEST_VERSION complete."
