#!/bin/bash

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
if [ ! -d "frameenv" ]; then
  python3 -m venv frameenv
  source frameenv/bin/activate
  pip install --upgrade pip
  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  else
    echo "requirements.txt not found. Please ensure dependencies are listed."
  fi
  deactivate
else
  echo "Virtual environment already exists."
fi
