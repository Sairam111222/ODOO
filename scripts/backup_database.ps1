# =============================================================================
# SolarFlow 360 — Production Database & Filestore Backup Automation
# =============================================================================
# Usage: ./scripts/backup_database.ps1 [-BackupDir "./backups"]
# =============================================================================

param (
    [string]$BackupDir = "./backups"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$dumpFile = "$BackupDir/solarflow_backup_$timestamp.dump"

if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

Write-Host ">>> Starting SolarFlow 360 Database Backup..." -ForegroundColor Cyan

# Execute pg_dump inside the solarflow_db container
docker exec -t solarflow_db pg_dump -U odoo -d solarflow -F c -b -v -f "/tmp/backup.dump"
if ($LASTEXITCODE -eq 0) {
    docker cp "solarflow_db:/tmp/backup.dump" $dumpFile
    docker exec solarflow_db rm -f /tmp/backup.dump
    Write-Host ">>> [SUCCESS] Database backup saved to: $dumpFile" -ForegroundColor Green
} else {
    Write-Host ">>> [ERROR] Database backup failed!" -ForegroundColor Red
}

