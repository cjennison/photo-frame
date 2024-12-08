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
BUILD_DIR="build"
DIST_DIR="dist"
AZURE_CONTAINER="builds"
SAS_TOKEN="$SAS_TOKEN"  

# Check if SAS_TOKEN is defined
if [ -z "$SAS_TOKEN" ]; then
  echo "Error: SAS_TOKEN not found in .env file."
  exit 0
fi

# Get the current version from version.txt
if [ ! -f $VERSION_FILE ]; then
  echo "Error: $VERSION_FILE not found."
  exit 0
fi
CURRENT_VERSION=$(cat $VERSION_FILE | tr -d '\n')

if [ -z "$CURRENT_VERSION" ]; then
  echo "Error: VERSION not found in $VERSION_FILE."
  exit 0
fi

# Prepare build directory
echo "Preparing build directory..."
rm -rf $BUILD_DIR $DIST_DIR
mkdir -p $BUILD_DIR $DIST_DIR

# Package the project
echo "Packaging project version $CURRENT_VERSION..."

# Copy only necessary files
rsync -av --progress ./ $BUILD_DIR --exclude frameenv --exclude __pycache__ --exclude '*.pyc' --exclude '*.pyo' --exclude $DIST_DIR --exclude $BUILD_DIR

# Ensure pictures and videos directories exist
mkdir -p $BUILD_DIR/pictures
mkdir -p $BUILD_DIR/videos

cd $BUILD_DIR
zip -r "../$DIST_DIR/${PROJECT_NAME}_$CURRENT_VERSION.zip" .
cd ..

# Update version.txt
echo "Updating version.txt..."
echo "$CURRENT_VERSION" > $DIST_DIR/$VERSION_FILE

# Deploy to Azure
echo "Deploying build to Azure..."
azcopy copy "$DIST_DIR/${PROJECT_NAME}_$CURRENT_VERSION.zip" "https://photoframejennison.blob.core.windows.net/$AZURE_CONTAINER/${PROJECT_NAME}_$CURRENT_VERSION.zip?$SAS_TOKEN"
azcopy copy "$DIST_DIR/$VERSION_FILE" "https://photoframejennison.blob.core.windows.net/$AZURE_CONTAINER/version.txt?$SAS_TOKEN"

# Clean up
echo "Cleaning up..."
rm -rf $BUILD_DIR $DIST_DIR

echo "Build and deployment complete."
