"""PDF extraction, chunking, and embedding for ChromaDB."""

import os
import re
import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_PERSIST_DIR, PDF_DIR

model = None


def get_model():
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF. Falls back to OCR for scanned/image PDFs."""
    # First try pdfplumber (fast, works for text-based PDFs)
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"

    if text.strip():
        return text.strip()

    # Fallback: OCR via PyMuPDF + pytesseract
    print(f"    (Using OCR fallback...)")
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        # Render page to image at 300 DPI
        pix = page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        page_text = pytesseract.image_to_string(img)
        if page_text:
            text += page_text + "\n\n"
    doc.close()
    return text.strip()


def classify_pdf(filename: str, subdir: str) -> dict:
    """Classify a PDF by its metadata based on filename and directory."""
    filename_lower = filename.lower()

    # Determine doc_type from directory
    if "drug_monographs" in subdir:
        doc_type = "drug_monograph"
    elif "cycle_sheets" in subdir:
        doc_type = "cycle_sheet"
    elif "handbooks" in subdir:
        doc_type = "handbook"
    else:
        doc_type = "unknown"

    # Determine drug from filename
    drug = ""
    if "tmz" in filename_lower or "temozolomide" in filename_lower:
        drug = "tmz"
    elif "bevacizumab" in filename_lower:
        drug = "bevacizumab"
    elif "lomustine" in filename_lower:
        drug = "lomustine"
    elif "etoposide" in filename_lower:
        drug = "etoposide"
    elif "vorasidenib" in filename_lower:
        drug = "vorasidenib"

    # Determine handbook type
    handbook_type = ""
    if "adult" in filename_lower:
        handbook_type = "adult_patient"
    elif "caregiver" in filename_lower:
        handbook_type = "caregiver"
    elif "non_malignant" in filename_lower or "non malignant" in filename_lower:
        handbook_type = "non_malignant"
    elif "pediatric" in filename_lower:
        handbook_type = "pediatric"

    return {
        "doc_type": doc_type,
        "drug": drug,
        "handbook_type": handbook_type,
        "source": filename,
    }


def chunk_by_sections(text: str, metadata: dict) -> list:
    """Chunk drug monographs by section headers."""
    # Common section headers in drug monographs
    section_pattern = r'\n(?=[A-Z][A-Z\s/&]+(?:\n|:))'
    sections = re.split(section_pattern, text)

    chunks = []
    for section in sections:
        section = section.strip()
        if len(section) < 50:  # Skip very short sections
            continue

        # Get section title from first line
        lines = section.split("\n")
        section_title = lines[0].strip() if lines else ""

        chunk_meta = {**metadata, "section": section_title}
        chunks.append({"text": section, "metadata": chunk_meta})

    return chunks


def chunk_sliding_window(text: str, metadata: dict, chunk_size: int = 500, overlap: int = 100) -> list:
    """Chunk text using sliding window (token-approximate using words)."""
    words = text.split()
    chunks = []

    if len(words) <= chunk_size:
        chunks.append({"text": text, "metadata": metadata})
        return chunks

    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_text = " ".join(words[start:end])

        # Try to detect chapter context
        chapter = ""
        preceding = " ".join(words[max(0, start - 50):start])
        chapter_match = re.search(r'(?:Chapter|CHAPTER|Section)\s+\d+[:\s]*([^\n]+)', preceding)
        if chapter_match:
            chapter = chapter_match.group(0).strip()

        chunk_meta = {**metadata}
        if chapter:
            chunk_meta["chapter"] = chapter

        chunks.append({"text": chunk_text, "metadata": chunk_meta})

        if end >= len(words):
            break
        start += chunk_size - overlap

    return chunks


def process_pdf(pdf_path: str, subdir: str) -> list:
    """Process a single PDF into chunks."""
    filename = os.path.basename(pdf_path)
    metadata = classify_pdf(filename, subdir)

    text = extract_text_from_pdf(pdf_path)
    if not text:
        print(f"  Warning: No text extracted from {filename}")
        return []

    if metadata["doc_type"] == "drug_monograph":
        chunks = chunk_by_sections(text, metadata)
    elif metadata["doc_type"] == "cycle_sheet":
        # Single chunk per cycle sheet
        chunks = [{"text": text, "metadata": metadata}]
    elif metadata["doc_type"] == "handbook":
        chunks = chunk_sliding_window(text, metadata)
    else:
        chunks = chunk_sliding_window(text, metadata)

    return chunks


def ingest_all_pdfs():
    """Process all PDFs and store in ChromaDB."""
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    # Delete existing collection if it exists
    try:
        client.delete_collection("neuronav_docs")
    except Exception:
        pass

    collection = client.create_collection(
        name="neuronav_docs",
        metadata={"hnsw:space": "cosine"},
    )

    embed_model = get_model()
    all_chunks = []

    # Track Bevacizumab to skip duplicate
    seen_bevacizumab = False

    for subdir in ["drug_monographs", "cycle_sheets", "handbooks"]:
        dir_path = os.path.join(PDF_DIR, subdir)
        if not os.path.exists(dir_path):
            print(f"  Skipping {subdir} — directory not found")
            continue

        for filename in sorted(os.listdir(dir_path)):
            if not filename.lower().endswith(".pdf"):
                continue

            # Skip duplicate Bevacizumab
            if "bevacizumab" in filename.lower():
                if seen_bevacizumab:
                    print(f"  Skipping duplicate: {filename}")
                    continue
                seen_bevacizumab = True

            pdf_path = os.path.join(dir_path, filename)
            print(f"  Processing: {filename}")
            chunks = process_pdf(pdf_path, subdir)
            all_chunks.extend(chunks)
            print(f"    → {len(chunks)} chunks")

    if not all_chunks:
        print("No chunks to ingest!")
        return

    print(f"\nTotal chunks: {len(all_chunks)}")
    print("Generating embeddings...")

    texts = [c["text"] for c in all_chunks]
    embeddings = embed_model.encode(texts, show_progress_bar=True).tolist()

    print("Storing in ChromaDB...")

    # ChromaDB has a batch limit, insert in batches
    batch_size = 100
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        batch_texts = texts[i:i + batch_size]
        batch_embeddings = embeddings[i:i + batch_size]
        batch_ids = [f"chunk_{i + j}" for j in range(len(batch))]
        batch_metadatas = [c["metadata"] for c in batch]

        collection.add(
            ids=batch_ids,
            documents=batch_texts,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
        )

    print(f"Done! {collection.count()} chunks stored in ChromaDB.")


if __name__ == "__main__":
    ingest_all_pdfs()
