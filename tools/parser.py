import os

try:
    from docx import Document
except ImportError:
    Document = None


def parse(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".docx":
        if Document is None:
            raise ImportError(
                "python-docx is required to parse .docx files. Install with: pip install python-docx"
            )
        document = Document(file_path)
        return "\n".join(p.text for p in document.paragraphs if p.text)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()