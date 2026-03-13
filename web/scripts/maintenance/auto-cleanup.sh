#!/bin/bash

# Configuration
MEMORY_THRESHOLD_GB=7
TIME_INTERVAL_MIN=20
LAST_RUN_FILE="/tmp/last_cleanup_run"
LOG_FILE="/tmp/auto_cleanup.log"

# Function to get free memory in GB
get_free_memory() {
    # vm_stat output is in pages (4KB on Intel, 16KB on Apple Silicon)
    PAGE_SIZE=$(sysctl -n hw.pagesize)
    FREE_PAGES=$(vm_stat | grep "Pages free" | awk '{print $3}' | sed 's/\.//')
    SPECULATIVE_PAGES=$(vm_stat | grep "Pages speculative" | awk '{print $3}' | sed 's/\.//')
    
    TOTAL_FREE_BYTES=$(( (FREE_PAGES + SPECULATIVE_PAGES) * PAGE_SIZE ))
    echo "scale=2; $TOTAL_FREE_BYTES / (1024 * 1024 * 1024)" | bc
}

# Function to perform cleanup
perform_cleanup() {
    echo "$(date): Starting scheduled cleanup..." >> "$LOG_FILE"
    
    # 1. Clear ~/Library/Caches
    # Use 2>/dev/null to skip system-locked files
    rm -rf ~/Library/Caches/* 2>/dev/null
    
    # 2. NPM Cache
    npm cache clean --force >> "$LOG_FILE" 2>&1
    
    # 3. PNPM Store
    pnpm store prune >> "$LOG_FILE" 2>&1
    
    # 4. Project Cache (Optional: comment out if not desired)
    # rm -rf .next
    
    echo "$(date): Cleanup completed." >> "$LOG_FILE"
    date +%s > "$LAST_RUN_FILE"
}

# Main Loop
echo "Starting Auto-Cleanup Monitor (Threshold: ${MEMORY_THRESHOLD_GB}GB, Interval: ${TIME_INTERVAL_MIN}min)"
echo "Logs available at: $LOG_FILE"

while true; do
    FREE_MEM=$(get_free_memory)
    CURRENT_TIME=$(date +%s)
    
    if [ ! -f "$LAST_RUN_FILE" ]; then
        LAST_RUN=0
    else
        LAST_RUN=$(cat "$LAST_RUN_FILE")
    fi
    
    ELAPSED=$(( (CURRENT_TIME - LAST_RUN) / 60 ))
    
    echo "Monitoring... Free Mem: ${FREE_MEM}GB | Last Run: ${ELAPSED}min ago"
    
    # Trigger conditions
    if (( $(echo "$FREE_MEM < $MEMORY_THRESHOLD_GB" | bc -l) )); then
        echo "Memory below threshold (${FREE_MEM}GB < ${MEMORY_THRESHOLD_GB}GB). Triggering cleanup."
        perform_cleanup
    elif [ "$ELAPSED" -ge "$TIME_INTERVAL_MIN" ]; then
        echo "Time interval reached (${ELAPSED}min >= ${TIME_INTERVAL_MIN}min). Triggering cleanup."
        perform_cleanup
    fi
    
    sleep 60 # Check every minute
done
