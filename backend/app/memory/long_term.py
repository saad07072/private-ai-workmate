from app.memory.database import get_connection


def add_memory(content: str, category: str = "general", user_id: str = "") -> int:
    """
    Add a long-term memory to SQLite.

    Returns:
        The newly created memory ID.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO memories (content, category, user_id)
        VALUES (?, ?, ?)
        """,
        (content, category, user_id),
    )

    memory_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return memory_id


def get_memories(user_id: str):
    """
    Return all long-term memories.
    """

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, content, category, created_at
        FROM memories
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,),
    )

    memories = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return memories


def delete_memory(memory_id: int, user_id: str) -> bool:
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
        WHERE id = ? AND user_id = ?
        """,
        (memory_id, user_id),
    )

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted


def memory_belongs_to_user(memory_id: int, user_id: str) -> bool:
    connection = get_connection()
    row = connection.execute(
        "SELECT 1 FROM memories WHERE id = ? AND user_id = ?",
        (memory_id, user_id),
    ).fetchone()
    connection.close()
    return row is not None