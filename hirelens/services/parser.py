# hirelens/services/parser.py
import os, re
from typing import List, Dict, Iterable
from pypdf import PdfReader
import docx2txt

ALLOWED_EXTS = (".pdf", ".docx", ".doc", ".txt")

def _read_pdf(path: str) -> str:
    try:
        reader = PdfReader(path)
        chunks = []
        for page in reader.pages:
            # pypdf returns text or None
            txt = page.extract_text() or ""
            chunks.append(txt)
        return "\n".join(chunks)
    except Exception:
        return ""  # if encrypted or broken, return empty

def _read_docx(path: str) -> str:
    try:
        return docx2txt.process(path) or ""
    except Exception:
        return ""

def _read_txt(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return ""

def read_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return _read_pdf(path)
    if ext in (".docx", ".doc"):
        return _read_docx(path)
    return _read_txt(path)

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def _iter_resume_files(folder: str) -> Iterable[str]:
    for root, _, files in os.walk(folder):
        for fn in files:
            if fn.lower().endswith(ALLOWED_EXTS):
                yield os.path.join(root, fn)

def load_resumes(folder: str) -> List[Dict]:
    items: List[Dict] = []
    for path in _iter_resume_files(folder):
        text = _clean(read_file(path))
        name = os.path.splitext(os.path.basename(path))[0]
        items.append({"id": os.path.basename(path), "name": name, "path": path, "text": text})
    return items
