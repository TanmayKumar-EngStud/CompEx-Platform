#!/bin/bash

# Configuration
SERVER_IP="10.100.0.1"
KEY_FILE="deploy_key"
REMOTE_BACKUP_DIR="/home/deploy/backups"
LOCAL_BACKUP_DIR="../../backups/remote"

echo "Checking for latest backup on $SERVER_IP..."

# Get latest backup filename
LATEST_BACKUP=$(ssh -i $KEY_FILE root@$SERVER_IP "ls -t $REMOTE_BACKUP_DIR | head -n 1")

if [ -z "$LATEST_BACKUP" ]; then
    echo "No backups found on server."
    exit 1
fi

echo "Found latest backup: $LATEST_BACKUP"

# Create local backup dir
mkdir -p "$LOCAL_BACKUP_DIR"

# Download
echo "Downloading $LATEST_BACKUP to $LOCAL_BACKUP_DIR..."
scp -i $KEY_FILE root@$SERVER_IP:"$REMOTE_BACKUP_DIR/$LATEST_BACKUP" "$LOCAL_BACKUP_DIR/"

if [ $? -eq 0 ]; then
    echo "Download complete: $LOCAL_BACKUP_DIR/$LATEST_BACKUP"
else
    echo "Error: Download failed."
    exit 1
fi
