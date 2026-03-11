import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Database — use /app/neuronav.db on Render (persistent disk), or local path
_DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "neuronav.db"))
DATABASE_URL = f"sqlite:///{os.path.abspath(_DB_PATH)}"

# ChromaDB — use /app/chroma_data on Render, or local path
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_data"))

# PDFs
PDF_DIR = os.getenv("PDF_DIR", os.path.join(os.path.dirname(__file__), "..", "pdfs"))

CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Frontend URL for CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
