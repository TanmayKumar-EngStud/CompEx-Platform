#!/bin/bash
# Automated Database Backup Script for Compex
# Backs up PostgreSQL database from server via SSH
# Keeps 15 days of backups

set -e

# === CONFIGURATION ===
SERVER_HOST="65.20.81.237"
SERVER_USER="root"
SSH_KEY="./deploy_key"
DB_NAME="compex-db"
DB_USER="compexe_admin"
DB_PASSWORD="QuiZA.0310!"
LOCAL_BACKUP_DIR="./backups"
REMOTE_TEMP_DIR="/tmp"
RETENTION_DAYS=15

# === COLORS FOR OUTPUT ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🗄️  Starting database backup...${NC}"
echo "=========================================="

# === CREATE LOCAL BACKUP DIRECTORY ===
mkdir -p "$LOCAL_BACKUP_DIR"

# === GENERATE TIMESTAMP ===
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${DB_NAME}_${TIMESTAMP}.sql.gz"
REMOTE_BACKUP_PATH="${REMOTE_TEMP_DIR}/${BACKUP_FILE}"

# === RUN BACKUP ON SERVER ===
echo -e "${YELLOW}📦 Creating backup on server...${NC}"

if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$SERVER_USER@$SERVER_HOST" << EOF
    echo "Starting pg_dump..."
    PGPASSWORD="$DB_PASSWORD" pg_dump -h 127.0.0.1 -U "$DB_USER" "$DB_NAME" | gzip > "$REMOTE_BACKUP_PATH"
    echo "Backup created at $REMOTE_BACKUP_PATH"
    ls -lh "$REMOTE_BACKUP_PATH"
EOF
then
    # === DOWNLOAD BACKUP TO LOCAL ===
    echo -e "${YELLOW}📥 Downloading backup to local machine...${NC}"
    if scp -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$SERVER_USER@$SERVER_HOST:$REMOTE_BACKUP_PATH" "$LOCAL_BACKUP_DIR/"; then
        # === VERIFY LOCAL BACKUP ===
        LOCAL_PATH="$LOCAL_BACKUP_DIR/$BACKUP_FILE"
        if [ -f "$LOCAL_PATH" ]; then
            echo -e "${GREEN}✅ Backup saved: $LOCAL_PATH${NC}"
            ls -lh "$LOCAL_PATH"
        else
            echo -e "${RED}❌ ERROR: Backup file not found locally!${NC}"
        fi
    else
        echo -e "${RED}⚠️  Failed to download backup from server.${NC}"
    fi

    # === CLEANUP REMOTE BACKUP ===
    echo -e "${YELLOW}🧹 Cleaning up remote temporary backup...${NC}"
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$SERVER_USER@$SERVER_HOST" "rm -f $REMOTE_BACKUP_PATH" || true
else
    echo -e "${RED}⚠️  Connection to backup server timed out or failed. Skipping remote backup for this session.${NC}"
    echo -e "${YELLOW}💡 Tip: Ensure you are on the correct network or the server is reachable.${NC}"
fi

# === DELETE OLD LOCAL BACKUPS (older than 15 days) ===
echo -e "${YELLOW}🗑️  Removing backups older than $RETENTION_DAYS days...${NC}"
OLD_BACKUPS=$(find "$LOCAL_BACKUP_DIR" -name "${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -type f)
if [ -n "$OLD_BACKUPS" ]; then
    echo "$OLD_BACKUPS" | xargs rm -v
    echo -e "${GREEN}✅ Old backups cleaned up${NC}"
else
    echo "No old backups to remove"
fi

# === SUMMARY ===
echo ""
echo "=========================================="
echo -e "${GREEN}✅ BACKUP COMPLETE!${NC}"
echo "=========================================="
echo "📁 Backup location: $LOCAL_PATH"
echo "📊 Backup size: $(ls -lh "$LOCAL_PATH" | awk '{print $5}')"
echo "🕐 Timestamp: $TIMESTAMP"
echo "📅 Retention: $RETENTION_DAYS days"
echo ""
echo "To restore this backup:"
echo "  gunzip -k $LOCAL_PATH"
echo "  psql -h localhost -U compexe_admin -d compex-db < ${LOCAL_PATH%.gz}"
echo ""
