from app.memory.semantic import search_semantic_memories
from app.auth import get_authenticated_user_id


def retrieve_relevant_memories(
    query: str,
    limit: int = 5,
    user_id: str = "",
):
    """
    Retrieve long-term memories using semantic similarity.
    """

    results = search_semantic_memories(
        query,
        limit,
        user_id or get_authenticated_user_id(),
    )

    return [
        {
            "content": result["content"],
            "category": result["category"],
            "score": result["score"],
        }
        for result in results
    ]