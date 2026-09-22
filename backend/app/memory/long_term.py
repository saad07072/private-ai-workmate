from app.memory.database import get_connection


def add_memory(content: str, category: str = "general") -> int:
    """
    Add a long-term memory to SQLite.

    Returns:
        The newly created memory ID.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories (content, category)
        VALUES (?, ?)
        """,
        (content, category),
    )

    memory_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return memory_id


def get_memories():
    """
    Return all long-term memories.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, content, category, created_at
        FROM memories
        ORDER BY created_at DESC
        """
    )

    memories = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return memories


def delete_memory(memory_id: int) -> bool:
    """
    Delete a long-term memory by ID.

    Returns:
        True if a memory was deleted, otherwise False.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM memories
        WHERE id = ?
        """,
        (memory_id,),
    )

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted