from app.memory.database import (
    get_connection,
    initialize_database,
)


class ConversationStore:

    def __init__(self):
        initialize_database()

    def create_conversation(self, conversation_id: str):
        connection = get_connection()

        connection.execute(
            """
            INSERT OR IGNORE INTO conversations (id)
            VALUES (?)
            """,
            (conversation_id,),
        )

        connection.commit()
        connection.close()

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ):
        self.create_conversation(conversation_id)

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO messages
            (conversation_id, role, content)
            VALUES (?, ?, ?)
            """,
            (
                conversation_id,
                role,
                content,
            ),
        )

        connection.commit()
        connection.close()

    def get_messages(self, conversation_id: str):

        connection = get_connection()

        cursor = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
            """,
            (conversation_id,),
        )

        messages = [
            {
                "role": row["role"],
                "content": row["content"],
            }
            for row in cursor.fetchall()
        ]

        connection.close()

        return messages

    def clear_conversation(self, conversation_id: str):

        connection = get_connection()

        connection.execute(
            """
            DELETE FROM messages
            WHERE conversation_id = ?
            """,
            (conversation_id,),
        )

        connection.execute(
            """
            DELETE FROM conversations
            WHERE id = ?
            """,
            (conversation_id,),
        )

        connection.commit()
        connection.close()


conversation_store = ConversationStore()