#!/usr/bin/env bash
set -e

# Build the SQLite registry DB if it doesn't already exist at DB_PATH.
# This matters on hosted platforms with ephemeral or freshly-provisioned
# disks: without this step every query_federated_registry() call fails
# with DB_ERROR and every audit silently degrades.
DB_FILE="${SUSTAINABILITY_DB_PATH:-sustainability.db}"

if [ ! -f "$DB_FILE" ]; then
    echo "[start.sh] $DB_FILE not found, building registry database..."
    python -m src.setup_db
else
    echo "[start.sh] $DB_FILE already exists, skipping build."
fi

echo "[start.sh] Launching API on port ${PORT:-8000}..."
exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}"