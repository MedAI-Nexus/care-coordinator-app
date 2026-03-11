#!/bin/bash
set -e

CHROMA_DIR="${CHROMA_PERSIST_DIR:-/data/chroma_data}"

# Ingest PDFs into ChromaDB if not already done
if [ ! -d "$CHROMA_DIR" ] || [ -z "$(ls -A "$CHROMA_DIR" 2>/dev/null)" ]; then
    echo "Ingesting PDFs into ChromaDB..."
    cd /app/backend
    python -c "
import sys
sys.path.insert(0, '.')
from rag.ingest import ingest_all_pdfs
ingest_all_pdfs()
"
    echo "PDF ingestion complete."
else
    echo "ChromaDB data already exists, skipping ingestion."
fi

# Initialize database
cd /app/backend
python -c "from database import init_db; init_db()"

# Start the server
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
