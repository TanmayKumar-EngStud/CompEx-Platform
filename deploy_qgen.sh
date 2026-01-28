#!/bin/bash

# Configuration
SERVER_IP="10.100.0.1" # VPN IP
USER="deploy"
APP_DIR="/home/deploy/QGen-py-compex"
KEY_FILE="deploy_key"

echo "Deploying QGen to $SERVER_IP..."

# Note: This script assumes the repository exists on the server.
# If not, the first run will fail at 'cd' and requires a manual 'git clone'.

ssh -i $KEY_FILE root@$SERVER_IP "sudo -i -u $USER bash -c '
  echo \"Current Directory: \$(pwd)\"
  
  # Navigate to App Directory
  if [ ! -d \"$APP_DIR\" ]; then
    echo \"Error: Directory $APP_DIR does not exist. Please clone the repo first.\"
    exit 1
  fi
  
  cd $APP_DIR || exit 1
  
  # Pull Latest Code
  echo \"Pulling latest code...\"
  git reset --hard origin/main || { echo \"Error: git reset failed.\"; exit 1; }
  git pull origin main || { echo \"Error: git pull failed.\"; exit 1; }
  
  # Build and Setup Container
  echo \"Building QGen container...\"
  # We use --no-cache to ensure all code changes are picked up
  docker-compose build question-gen
  
  # Setup but do NOT run as requested
  echo \"Cleaning up existing container (if any)...\"
  docker-compose stop question-gen || true
  docker-compose rm -f question-gen || true
  
  # Create the container but do not start it
  echo \"Creating container (stopped state)...\"
  docker-compose up --no-start question-gen
  
  echo \"Setup Complete! Container is ready but NOT running.\"
'"
