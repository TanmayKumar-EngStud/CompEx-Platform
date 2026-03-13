#!/bin/bash

# Configuration
SERVER_IP="10.100.0.1" # VPN IP
USER="deploy"
APP_DIR="/home/deploy/compex/compex"
KEY_FILE="deploy_key"

echo "Deploying to $SERVER_IP..."

ssh -i $KEY_FILE root@$SERVER_IP "sudo -i -u $USER bash -c '
  echo \"Current Directory: \$(pwd)\"
  
  # Navigate to App Directory
  cd $APP_DIR || exit 1
  
  # Pull Latest Code
  echo \"Pulling latest code...\"
  git reset --hard origin/main || { echo "Error: git reset failed."; exit 1; }
  git pull origin main || { echo "Error: git pull failed."; exit 1; }
  
  # Install Dependencies
  echo \"Installing dependencies...\"
  pnpm install
  
  # Build Application
  echo \"Building application...\"
  pnpm run build
  
  # Copy Standalone Files
  echo \"Preparing standalone build...\"
  cp -r .next/static .next/standalone/.next/
  cp -r public .next/standalone/
  
  # Run Migrations
  echo \"Running database migrations...\"
  npx prisma migrate deploy
  
  # Restart PM2
  echo \"Restarting application...\"
  pm2 restart compex || pm2 start /home/deploy/ecosystem.config.js
  
  echo \"Deployment Complete!\"
'"
