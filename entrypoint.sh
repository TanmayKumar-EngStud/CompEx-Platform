#!/bin/bash
set -e

# Loop forever
while true; do
    echo "[$(date)] Starting Question Generation (main.py)..."
    python -u main.py
    echo "[$(date)] Generation complete."
    
    echo "[$(date)] Sleeping for 24 hours (86400 seconds)..."
    sleep 86400
done
