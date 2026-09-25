from app.memory.database import get_connection


def add_document(
    filename: str,
    file_type: str,
    file_path: str,
    user_id: str,
) -> int:
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO documents (
            user_id,
            filename,
            file_type,
            file_path
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            filename,
            file_type,
            file_path,
        ),
    )

    document_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return document_id


def update_document_chunk_count(
    document_id: int,
    chunk_count: int,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE documents
        SET chunk_count = ?
        WHERE id = ?
        """,
        (
            chunk_count,
            document_id,
        ),
    )

    connection.commit()

    connection.close()


def get_documents(user_id: str):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            filename,
            file_type,
            chunk_count,
            created_at
        FROM documents
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,),
    )

    documents = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return documents


def get_document(document_id: int, user_id: str):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM documents
        WHERE id = ? AND user_id = ?
        """,
        (document_id, user_id),
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


def delete_document_record(document_id: int, user_id: str) -> bool:
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM documents
        WHERE id = ? AND user_id = ?
        """,
        (document_id, user_id),
    )

    deleted = cursor.rowcount > 0

    connection.commit()

    connection.close()

    return deleted