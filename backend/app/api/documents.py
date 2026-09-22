from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.rag.database import get_documents
from app.rag.service import (
    ingest_document,
    remove_document,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


BASE_DIR = Path(__file__).resolve().parents[3]

DOCUMENT_DIR = BASE_DIR / "data" / "documents"

DOCUMENT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
}


MAX_FILE_SIZE = 10 * 1024 * 1024


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    original_name = Path(
        file.filename
    ).name

    extension = Path(
        original_name
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Supported formats: PDF, DOCX, TXT."
            ),
        )

    content = await file.read()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size must be 10 MB or less.",
        )

    unique_name = (
        f"{uuid4().hex}_{original_name}"
    )

    file_path = DOCUMENT_DIR / unique_name

    file_path.write_bytes(content)

    try:
        result = ingest_document(
            file_path=str(file_path),
            filename=original_name,
            file_type=extension.lstrip("."),
        )

        return {
            "message": "Document uploaded and indexed successfully.",
            **result,
        }

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {exc}",
        )


@router.get("")
def list_documents():
    return {
        "documents": get_documents(),
    }


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
):
    deleted = remove_document(
        document_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
    }