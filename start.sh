#!/bin/bash
set -e

# Initialize database
cd /app/backend
python -c "from database import init_db; init_db()"

# Start the server (HF Spaces uses PORT=7860)
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}
