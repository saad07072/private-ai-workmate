from app.rag.vector_store import search_documents
from app.auth import get_authenticated_user_id


def retrieve_relevant_documents(
    query: str,
    limit: int = 5,
    user_id: str = "",
):
    """
    Retrieve the most relevant document chunks.
    """

    results = search_documents(
        query=query,
        limit=limit,
        user_id=user_id or get_authenticated_user_id(),
    )

    # Ignore extremely weak matches.
    results = [
        result
        for result in results
        if result["score"] >= 0.35
    ]

    return results