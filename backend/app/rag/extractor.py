from pathlib import Path

from docx import Document
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


def extract_text(file_path: str) -> list[dict]:
    """
    Extract text from supported document formats.

    Returns:
        [
            {
                "text": "...",
                "page": 1
            }
        ]
    """

    path = Path(file_path)
    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if extension == ".pdf":
        return _extract_pdf(path)

    if extension == ".docx":
        return _extract_docx(path)

    if extension == ".txt":
        return _extract_txt(path)

    raise ValueError(
        "Unsupported document format."
    )


def _clean_text(text: str) -> str:
    """
    Normalize extracted Unicode text.

    PDF extraction can contain unusual whitespace
    and Unicode characters. Keep the original Unicode
    content while removing unnecessary whitespace.
    """

    text = text.replace("\x00", " ")

    lines = []

    for line in text.splitlines():
        line = " ".join(line.split())

        if line:
            lines.append(line)

    return "\n".join(lines).strip()


def _extract_pdf(path: Path) -> list[dict]:
    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):
        text = page.extract_text() or ""

        text = _clean_text(text)

        if text:
            pages.append(
                {
                    "text": text,
                    "page": page_number,
                }
            )

    return pages


def _extract_docx(path: Path) -> list[dict]:
    document = Document(str(path))

    paragraphs = []

    for paragraph in document.paragraphs:
        text = _clean_text(
            paragraph.text
        )

        if text:
            paragraphs.append(text)

    combined_text = "\n".join(
        paragraphs
    )

    if not combined_text:
        return []

    return [
        {
            "text": combined_text,
            "page": None,
        }
    ]


def _extract_txt(path: Path) -> list[dict]:
    # utf-8-sig handles normal UTF-8 as well as
    # UTF-8 files containing a BOM.
    text = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    text = _clean_text(text)

    if not text:
        return []

    return [
        {
            "text": text,
            "page": None,
        }
    ]