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
    echo \"Directory $APP_DIR does not exist. Cloning...\"
    GIT_SSH_COMMAND=\"ssh -i /home/deploy/.ssh/qgen_deploy_key -o StrictHostKeyChecking=no\" git clone git@github.com:TanmayKumar-EngStud/QGen-py-compex.git \"$APP_DIR\" || { echo \"Error: Clone failed.\"; exit 1; }
  fi
  
  cd \"$APP_DIR\" || exit 1
  
  # Pull Latest Code
  echo \"Pulling latest code...\"
  # Detect branch (main or master)
  BRANCH=\$(git rev-parse --abbrev-ref HEAD)
  echo \"Current branch: \$BRANCH\"
  git reset --hard origin/\$BRANCH || { echo \"Error: git reset failed.\"; exit 1; }
  GIT_SSH_COMMAND=\"ssh -i /home/deploy/.ssh/qgen_deploy_key -o StrictHostKeyChecking=no\" git pull origin \$BRANCH || { echo \"Error: git pull failed.\"; exit 1; }
  
  # Build and Setup Container
  echo \"Building QGen container...\"
  # We use --no-cache to ensure all code changes are picked up
  docker compose -f docker-compose.server.yml build question-gen
  
  # Setup but do NOT run as requested
  echo \"Cleaning up existing container (if any)...\"
  docker compose -f docker-compose.server.yml stop question-gen || true
  docker compose -f docker-compose.server.yml rm -f question-gen || true
  
  # Create the container but do not start it
  echo \"Creating container (stopped state)...\"
  docker compose -f docker-compose.server.yml up --no-start question-gen
  
  echo \"Setup Complete! Container is ready but NOT running.\"
'"
