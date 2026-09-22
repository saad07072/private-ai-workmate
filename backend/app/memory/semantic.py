import os
from uuid import uuid4

from dotenv import load_dotenv
from openai import OpenAI

from qdrant_client.models import (
    Distance,
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

COLLECTION_NAME = "workmate_memories"

VECTOR_SIZE = 4096


nebius_client = OpenAI(
    base_url=NEBIUS_BASE_URL,
    api_key=NEBIUS_API_KEY,
)


def initialize_collection():
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


initialize_collection()


def create_embedding(
    text: str,
) -> list[float]:
    response = nebius_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def store_semantic_memory(
    memory_id: int,
    content: str,
    category: str,
):
    vector = create_embedding(content)

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=str(uuid4()),
                vector=vector,
                payload={
                    "memory_id": memory_id,
                    "content": content,
                    "category": category,
                },
            )
        ],
    )


def search_semantic_memories(
    query: str,
    limit: int = 5,
):
    query_vector = create_embedding(query)

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
    )

    return [
        {
            "memory_id": result.payload["memory_id"],
            "content": result.payload["content"],
            "category": result.payload["category"],
            "score": result.score,
        }
        for result in results.points
    ]