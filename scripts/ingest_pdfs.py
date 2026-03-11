#!/usr/bin/env python3
"""One-time script: Process PDFs into ChromaDB."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from rag.ingest import ingest_all_pdfs

if __name__ == "__main__":
    print("=" * 50)
    print("NeuroNav PDF Ingestion")
    print("=" * 50)
    ingest_all_pdfs()
