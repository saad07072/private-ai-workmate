from app.rag.vector_store import search_documents


def retrieve_relevant_documents(
    query: str,
    limit: int = 5,
):
    """
    Retrieve the most relevant document chunks.
    """

    results = search_documents(
        query=query,
        limit=limit,
    )

    # Ignore extremely weak matches.
    results = [
        result
        for result in results
        if result["score"] >= 0.35
    ]

    return results