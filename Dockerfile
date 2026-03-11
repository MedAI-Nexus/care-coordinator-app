# ---- Build stage: ingest PDFs (has pytorch + sentence-transformers) ----
FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY backend/ ./backend/
COPY pdfs/ ./pdfs/

ENV CHROMA_PERSIST_DIR=/app/chroma_data
ENV PDF_DIR=/app/pdfs
RUN cd /app/backend && python -c "import sys; sys.path.insert(0, '.'); from rag.ingest import ingest_all_pdfs; ingest_all_pdfs()"

# ---- Runtime stage: lightweight (no pytorch) ----
FROM python:3.12-slim

RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install only runtime dependencies (no sentence-transformers/pytorch)
COPY backend/requirements-runtime.txt .
RUN pip install --no-cache-dir -r requirements-runtime.txt

# Copy backend code
COPY backend/ ./backend/

# Copy pre-built ChromaDB data from builder
COPY --from=builder /app/chroma_data ./chroma_data

# Make writable for HF Spaces (runs as user 1000)
RUN chmod -R 777 /app

WORKDIR /app/backend

ENV CHROMA_PERSIST_DIR=/app/chroma_data

EXPOSE 7860

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
CMD ["/app/start.sh"]
