#!/bin/bash

# Variables
VERSION_FILE="version.txt"

# Check if version file exists
if [ ! -f $VERSION_FILE ]; then
  echo "Error: $VERSION_FILE not found."
  exit 1
fi

# Read the version from the file
VERSION=$(cat $VERSION_FILE | tr -d '\n')
if [ -z "$VERSION" ]; then
  echo "Error: Version not found in $VERSION_FILE."
  exit 1
fi

# Create a new Git tag
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
  echo "Tag v$VERSION already exists."
else
  echo "Creating new tag: v$VERSION"
  git tag -a "v$VERSION" -m "Release version $VERSION"

  # Push the tag to GitHub
  echo "Pushing tag v$VERSION to GitHub..."
  git push origin "v$VERSION"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to push tag to GitHub."
    exit 1
  fi
  echo "Tag v$VERSION created and pushed successfully."
fi