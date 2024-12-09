#!/bin/bash

# Developer Script

# Quickly repulls the current version of the project and restarts the service
# This script is intended to be run from the project directory

git pull origin master

pip install -r requirements.txt

systemctl restart photo-frame.service
