#!/bin/bash
set -e

CHROMA_DIR="${CHROMA_PERSIST_DIR:-/data/chroma_data}"

# Copy pre-built ChromaDB data to persistent disk if not already there
if [ "$CHROMA_DIR" != "/app/chroma_data" ]; then
    if [ ! -d "$CHROMA_DIR" ] || [ -z "$(ls -A "$CHROMA_DIR" 2>/dev/null)" ]; then
        echo "Copying pre-built ChromaDB data to persistent disk..."
        mkdir -p "$CHROMA_DIR"
        cp -r /app/chroma_data/* "$CHROMA_DIR"/
        echo "ChromaDB data copied."
    else
        echo "ChromaDB data already exists on persistent disk."
    fi
fi

# Initialize database
cd /app/backend
python -c "from database import init_db; init_db()"

# Start the server
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
