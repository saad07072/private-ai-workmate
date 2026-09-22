import uuid

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.memory.store import (
    conversation_store,
)

from app.memory.retrieval import (
    retrieve_relevant_memories,
)

from app.rag.retrieval import (
    retrieve_relevant_documents,
)

from app.agents.orchestrator import (
    run_agent,
)


router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    conversation_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )


class ChatResponse(BaseModel):
    conversation_id: str
    response: str


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
):
    conversation_id = (
        request.conversation_id
        or str(uuid.uuid4())
    )

    conversation_store.create_conversation(
        conversation_id
    )

    conversation_store.add_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message,
    )

    history = conversation_store.get_messages(
        conversation_id
    )

    messages_for_agent = []

    # -------------------------------------------------
    # Long-term memory
    # -------------------------------------------------

    memories = retrieve_relevant_memories(
        request.message
    )

    if memories:
        memory_lines = []

        for memory in memories:
            memory_lines.append(
                f"- {memory['content']}"
            )

        messages_for_agent.append(
            {
                "role": "system",
                "content": (
                    "Relevant long-term memories "
                    "about the user:\n"
                    + "\n".join(
                        memory_lines
                    )
                    + "\n\n"
                    "Use these memories only when "
                    "relevant to the request."
                ),
            }
        )

    # -------------------------------------------------
    # RAG context
    # -------------------------------------------------

    documents = retrieve_relevant_documents(
        request.message
    )

    if documents:

        document_lines = []

        for document in documents:

            filename = document.get(
                "filename",
                "Unknown document",
            )

            page = document.get(
                "page"
            )

            if page:
                source = (
                    f"{filename}, page {page}"
                )
            else:
                source = filename

            document_lines.append(
                f"[Source: {source}]\n"
                f"{document['text']}"
            )

        messages_for_agent.append(
            {
                "role": "system",
                "content": (
                    "PRIVATE DOCUMENT CONTEXT\n"
                    "=========================\n\n"
                    + "\n\n".join(
                        document_lines
                    )
                    + "\n\n"
                    "Use this context when relevant. "
                    "Do not invent information that is "
                    "not supported by these documents."
                ),
            }
        )

    # -------------------------------------------------
    # Conversation history
    # -------------------------------------------------

    messages_for_agent.extend(
        history
    )

    # -------------------------------------------------
    # Agent
    # -------------------------------------------------

    response = run_agent(
        messages_for_agent
    )

    # -------------------------------------------------
    # Save assistant response
    # -------------------------------------------------

    conversation_store.add_message(
        conversation_id=conversation_id,
        role="assistant",
        content=response,
    )

    return {
        "conversation_id": conversation_id,
        "response": response,
    }


@router.get(
    "/conversations/{conversation_id}"
)
def get_conversation(
    conversation_id: str,
):
    messages = conversation_store.get_messages(
        conversation_id
    )

    return {
        "conversation_id": conversation_id,
        "message_count": len(messages),
        "messages": messages,
    }