from app.memory.semantic import search_semantic_memories


def retrieve_relevant_memories(
    query: str,
    limit: int = 5,
):
    """
    Retrieve long-term memories using semantic similarity.
    """

    results = search_semantic_memories(
        query,
        limit,
    )

    return [
        {
            "content": result["content"],
            "category": result["category"],
            "score": result["score"],
        }
        for result in results
    ]