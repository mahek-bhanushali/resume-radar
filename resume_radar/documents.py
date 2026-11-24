"""Reading resume / job description files."""
from pathlib import Path


def read_document(path) -> str:
    """Read a .txt, .md or .pdf file and return its text."""
    file = Path(path)
    if not file.exists():
        raise FileNotFoundError(f"File not found: {file}")

    suffix = file.suffix.lower()
    if suffix in {".txt", ".md"}:
        return file.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            raise RuntimeError("Reading PDF files needs pypdf. Run: pip install pypdf")
        reader = PdfReader(str(file))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    raise ValueError(f"Unsupported file type '{suffix}'. Use .txt, .md or .pdf")
