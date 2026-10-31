#!/usr/bin/env bash
# =============================================================================
# SolarFlow 360 — Production Database & Filestore Backup (Linux/Bash)
# =============================================================================
set -euo pipefail

BACKUP_DIR="${1:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DUMP_FILE="${BACKUP_DIR}/solarflow_backup_${TIMESTAMP}.dump"

mkdir -p "${BACKUP_DIR}"

echo ">>> Starting SolarFlow 360 Database Backup..."
docker exec -t solarflow_db pg_dump -U odoo -d solarflow -F c -b -v -f "/tmp/backup.dump"
docker cp "solarflow_db:/tmp/backup.dump" "${DUMP_FILE}"
docker exec solarflow_db rm -f /tmp/backup.dump

echo ">>> [SUCCESS] Database backup created at: ${DUMP_FILE}"

