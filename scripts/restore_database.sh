#!/usr/bin/env bash
# =============================================================================
# SolarFlow 360 — Production Database Restore (Linux/Bash)
# =============================================================================
set -euo pipefail

DUMP_FILE="${1:-}"

if [[ -z "${DUMP_FILE}" || ! -f "${DUMP_FILE}" ]]; then
    echo ">>> [ERROR] Usage: $0 <path_to_dump_file>"
    exit 1
fi

echo ">>> WARNING: Restoring will overwrite existing database records in 'solarflow'!"
read -p "Are you sure you want to proceed? (yes/no): " confirm
if [[ "${confirm}" != "yes" ]]; then
    echo ">>> Restore cancelled."
    exit 0
fi

echo ">>> Copying dump to container..."
docker cp "${DUMP_FILE}" "solarflow_db:/tmp/restore.dump"

echo ">>> Restoring PostgreSQL database..."
docker exec -t solarflow_db pg_restore -U odoo -d solarflow --clean --if-exists -v "/tmp/restore.dump" || true

docker exec solarflow_db rm -f /tmp/restore.dump
echo ">>> [SUCCESS] Restoration complete!"

