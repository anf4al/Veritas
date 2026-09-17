import os
from pathlib import Path
from typing import List, Tuple
import pypdf
import docx

def extract_text_from_file(file_path: Path) -> List[Tuple[int, str]]:
    """Extract text from file as a list of (page_number, text) tuples.
    Supports .txt, .md, .pdf, .docx.
    """
    suffix = file_path.suffix.lower()
    results: List[Tuple[int, str]] = []

    if suffix in (".txt", ".md"):
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
            # Split plain text files into logical pages if form feeds present, else page 1
            pages = content.split("\x0c") if "\x0c" in content else [content]
            for idx, p in enumerate(pages, start=1):
                if p.strip():
                    results.append((idx, p.strip()))

    elif suffix == ".pdf":
        try:
            reader = pypdf.PdfReader(str(file_path))
            for idx, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    results.append((idx, page_text.strip()))
        except Exception as e:
            # Fallback for plain text if PDF parsing fails
            with open(file_path, "rb") as f:
                raw = f.read().decode("latin-1", errors="replace")
                results.append((1, raw[:4000]))

    elif suffix in (".docx", ".doc"):
        try:
            doc = docx.Document(str(file_path))
            full_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            results.append((1, full_text))
        except Exception as e:
            with open(file_path, "rb") as f:
                raw = f.read().decode("latin-1", errors="replace")
                results.append((1, raw[:4000]))
    else:
        # Generic text fallback
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            results.append((1, f.read()))

    if not results:
        results = [(1, "")]
    return results
