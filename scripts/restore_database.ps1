# =============================================================================
# SolarFlow 360 — Production Database Restore Automation
# =============================================================================
# Usage: ./scripts/restore_database.ps1 -DumpFile "./backups/solarflow_backup_XXXX.dump"
# =============================================================================

param (
    [Parameter(Mandatory=$true)]
    [string]$DumpFile
)

if (!(Test-Path $DumpFile)) {
    Write-Host ">>> [ERROR] Specified dump file does not exist: $DumpFile" -ForegroundColor Red
    exit 1
}

Write-Host ">>> WARNING: Restoring will overwrite existing database records in 'solarflow'!" -ForegroundColor Yellow
$confirm = Read-Host "Are you sure you want to proceed? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host ">>> Restore aborted by user."
    exit 0
}

Write-Host ">>> Uploading dump to database container..." -ForegroundColor Cyan
docker cp $DumpFile "solarflow_db:/tmp/restore.dump"

Write-Host ">>> Restoring PostgreSQL database via pg_restore..." -ForegroundColor Cyan
docker exec -t solarflow_db pg_restore -U odoo -d solarflow --clean --if-exists -v "/tmp/restore.dump"

docker exec solarflow_db rm -f /tmp/restore.dump
Write-Host ">>> [SUCCESS] Database restoration complete!" -ForegroundColor Green

