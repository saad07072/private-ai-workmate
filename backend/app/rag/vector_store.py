import os
from uuid import uuid4

from dotenv import load_dotenv
from openai import OpenAI

from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.memory.qdrant import qdrant_client


load_dotenv()


NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")

if not NEBIUS_API_KEY:
    raise RuntimeError(
        "NEBIUS_API_KEY is not configured."
    )


NEBIUS_BASE_URL = (
    "https://api.tokenfactory.nebius.com/v1/"
)

EMBEDDING_MODEL = "Qwen/Qwen3-Embedding-8B"

COLLECTION_NAME = "workmate_documents"

VECTOR_SIZE = 4096


nebius_client = OpenAI(
    base_url=NEBIUS_BASE_URL,
    api_key=NEBIUS_API_KEY,
)


def initialize_document_collection():
    collections = qdrant_client.get_collections()

    exists = any(
        collection.name == COLLECTION_NAME
        for collection in collections.collections
    )

    if not exists:
        qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )


initialize_document_collection()


def create_embedding(
    text: str,
) -> list[float]:
    response = nebius_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def store_document_chunks(
    document_id: int,
    filename: str,
    chunks: list[dict],
    user_id: str = "",
):
    points = []

    for chunk in chunks:
        vector = create_embedding(
            chunk["text"]
        )

        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "user_id": user_id,
                    "filename": filename,
                    "text": chunk["text"],
                    "page": chunk.get("page"),
                    "chunk_index": chunk["chunk_index"],
                },
            )
        )

    if not points:
        return

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )


def search_documents(
    query: str,
    limit: int = 5,
    user_id: str = "",
):
    query_vector = create_embedding(query)

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=max(limit * 4, limit),
    )

    matches = []

    from app.rag.database import get_document

    for result in results.points:
        payload = result.payload or {}

        if not payload.get("document_id") or get_document(payload["document_id"], user_id) is None:
            continue

        matches.append(
            {
                "document_id": payload.get(
                    "document_id"
                ),
                "filename": payload.get(
                    "filename"
                ),
                "text": payload.get(
                    "text",
                    "",
                ),
                "page": payload.get(
                    "page"
                ),
                "chunk_index": payload.get(
                    "chunk_index"
                ),
                "score": result.score,
            }
        )

    return matches


def delete_document_vectors(
    document_id: int,
    user_id: str = "",
):
    qdrant_client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(
                        value=document_id
                    ),
                )
                ,
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id),
                )
            ]
        ),
    )