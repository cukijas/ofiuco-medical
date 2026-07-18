#!/bin/bash
set -e

# PYTHONPATH=/app allows "from backend.app.*" imports
# (code lives at /app/backend/, parent /app is the package root)
export PYTHONPATH=/app

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
until python -c "
import asyncio, asyncpg, os, re
url = os.environ.get('DATABASE_URL', '')
url = re.sub(r'\+asyncpg', '', url)
async def check():
    try:
        conn = await asyncpg.connect(url)
        await conn.close()
        return True
    except Exception:
        return False
import sys; sys.exit(0 if asyncio.run(check()) else 1)
" 2>/dev/null; do
  echo "  PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "PostgreSQL is ready."

# Run Alembic migrations (alembic.ini is in WORKDIR /app/backend)
echo "Running database migrations..."
alembic upgrade head
echo "Migrations complete."

# Start uvicorn server
echo "Starting uvicorn server..."
exec uvicorn backend.app.api.main:app --host 0.0.0.0 --port 8000
