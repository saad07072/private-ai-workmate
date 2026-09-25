from pathlib import Path

from app.rag.chunker import chunk_text
from app.rag.database import (
    add_document,
    update_document_chunk_count,
    get_document,
    delete_document_record,
)
from app.rag.extractor import extract_text
from app.rag.vector_store import (
    store_document_chunks,
    delete_document_vectors,
)


def ingest_document(
    file_path: str,
    filename: str,
    file_type: str,
    user_id: str,
) -> dict:
    """
    Extract, chunk, embed and index a document.
    """

    pages = extract_text(file_path)

    if not pages:
        raise ValueError(
            "No readable text was found in the document."
        )

    chunks = []

    chunk_index = 0

    for page in pages:
        page_chunks = chunk_text(
            page["text"]
        )

        for text in page_chunks:
            chunks.append(
                {
                    "text": text,
                    "page": page.get("page"),
                    "chunk_index": chunk_index,
                }
            )

            chunk_index += 1

    if not chunks:
        raise ValueError(
            "The document did not contain usable text."
        )

    document_id = add_document(
        filename=filename,
        file_type=file_type,
        file_path=file_path,
        user_id=user_id,
    )

    try:
        store_document_chunks(
            document_id=document_id,
            filename=filename,
            chunks=chunks,
            user_id=user_id,
        )

        update_document_chunk_count(
            document_id=document_id,
            chunk_count=len(chunks),
        )

    except Exception:
        delete_document_record(
            document_id,
            user_id,
        )

        raise

    return {
        "document_id": document_id,
        "filename": filename,
        "file_type": file_type,
        "chunk_count": len(chunks),
    }


def remove_document(document_id: int, user_id: str) -> bool:
    document = get_document(document_id, user_id)

    if document is None:
        return False

    delete_document_vectors(
        document_id,
        user_id,
    )

    file_path = Path(
        document["file_path"]
    )

    if file_path.exists():
        file_path.unlink()

    delete_document_record(
        document_id,
        user_id,
    )

    return True