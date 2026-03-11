FROM python:3.12-slim

# Install tesseract for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the embedding model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy backend code and PDFs
COPY backend/ ./backend/
COPY pdfs/ ./pdfs/

# Ingest PDFs into ChromaDB during build
ENV CHROMA_PERSIST_DIR=/app/chroma_data
ENV PDF_DIR=/app/pdfs
RUN cd /app/backend && python -c "import sys; sys.path.insert(0, '.'); from rag.ingest import ingest_all_pdfs; ingest_all_pdfs()"

# Make everything writable (HF Spaces runs as non-root user 1000)
RUN chmod -R 777 /app

# Set working directory to backend
WORKDIR /app/backend

EXPOSE 7860

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
