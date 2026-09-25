from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.memory.long_term import (
    add_memory,
    get_memories,
    delete_memory,
)
from app.memory.semantic import store_semantic_memory
from app.auth import get_current_user


router = APIRouter(
    prefix="/api/memory",
    tags=["Memory"],
)


class MemoryRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    category: str = Field(
        default="general",
        max_length=100,
    )


@router.post("")
def create_memory(request: MemoryRequest, user: dict = Depends(get_current_user)):
    """
    Save a memory to SQLite and its semantic
    representation to Qdrant.
    """

    memory_id = add_memory(
        request.content,
        request.category,
        user["id"],
    )

    store_semantic_memory(
        memory_id,
        request.content,
        request.category,
        user["id"],
    )

    return {
        "message": "Memory saved successfully.",
        "memory_id": memory_id,
    }


@router.get("")
def list_memories(user: dict = Depends(get_current_user)):
    """
    Return all stored long-term memories.
    """

    return {
        "memories": get_memories(user["id"]),
    }


@router.delete("/{memory_id}")
def remove_memory(memory_id: int, user: dict = Depends(get_current_user)):
    """
    Delete a memory from SQLite.
    """

    deleted = delete_memory(memory_id, user["id"])

    if not deleted:
        return {
            "message": "Memory not found.",
        }

    return {
        "message": "Memory deleted successfully.",
        "memory_id": memory_id,
    }