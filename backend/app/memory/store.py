from app.memory.database import (
    get_connection,
    initialize_database,
)


class ConversationStore:

    def __init__(self):
        initialize_database()

    def create_conversation(self, conversation_id: str, user_id: str):
        connection = get_connection()

        connection.execute(
            """
            INSERT OR IGNORE INTO conversations (id, user_id)
            VALUES (?, ?)
            """,
            (conversation_id, user_id),
        )

        connection.commit()
        connection.close()

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        user_id: str,
    ):
        self.create_conversation(conversation_id, user_id)

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO messages
            (conversation_id, role, content)
            SELECT ?, ?, ?
            WHERE EXISTS (
                SELECT 1 FROM conversations
                WHERE id = ? AND user_id = ?
            )
            """,
            (
                conversation_id,
                role,
                content,
                conversation_id,
                user_id,
            ),
        )

        connection.commit()
        connection.close()

    def get_messages(self, conversation_id: str, user_id: str):

        connection = get_connection()

        cursor = connection.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ?
                            AND conversation_id IN (
                                    SELECT id FROM conversations WHERE user_id = ?
                            )
            ORDER BY id ASC
            """,
                        (conversation_id, user_id),
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

    def list_conversations(self, user_id: str, limit: int = 40):
        connection = get_connection()

        cursor = connection.execute(
            """
            SELECT
                conversations.id,
                conversations.created_at,
                (
                    SELECT content
                    FROM messages
                    WHERE conversation_id = conversations.id
                      AND role = 'user'
                    ORDER BY id ASC
                    LIMIT 1
                ) AS title,
                (
                    SELECT COUNT(*)
                    FROM messages
                    WHERE conversation_id = conversations.id
                ) AS message_count
            FROM conversations
            WHERE user_id = ? AND EXISTS (
                SELECT 1
                FROM messages
                WHERE conversation_id = conversations.id
            )
            ORDER BY (
                SELECT MAX(id)
                FROM messages
                WHERE conversation_id = conversations.id
            ) DESC
            LIMIT ?
            """,
            (user_id, limit),
        )

        conversations = [dict(row) for row in cursor.fetchall()]
        connection.close()

        return conversations

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