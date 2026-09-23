import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


# -------------------------------------------------
# Environment
# -------------------------------------------------

api_key = os.getenv("NEBIUS_API_KEY")

if not api_key:
    raise RuntimeError(
        "NEBIUS_API_KEY is not configured."
    )


# -------------------------------------------------
# Nebius Token Factory
# -------------------------------------------------

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=api_key,
)


# -------------------------------------------------
# Models
# -------------------------------------------------

FAST_MODEL = os.getenv(
    "NEBIUS_FAST_MODEL",
    "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B",
)

REASONING_MODEL = os.getenv(
    "NEBIUS_REASONING_MODEL",
    "nvidia/Nemotron-3-Ultra-550b-a55b",
)

# Backwards-compatible default model name.
MODEL = FAST_MODEL


# -------------------------------------------------
# System prompt
# -------------------------------------------------

SYSTEM_PROMPT = (
    "You are Private AI Workmate, a personal AI assistant. "
    "Be helpful, concise, accurate, and transparent. "
    "Use the conversation history and any provided memory context "
    "to answer the user. "
    "Never invent capabilities or make unsupported claims about "
    "privacy, encryption, data storage, security, permissions, "
    "local execution, or confidentiality. "
    "Only describe a capability as available when the application "
    "actually provides it. "
    "If a capability is not implemented yet, say so clearly."
)


# -------------------------------------------------
# Model generation
# -------------------------------------------------

def ask_nemotron(
    messages: list[dict],
    model: str | None = None,
    max_tokens: int | None = None,
) -> str:
    """
    Send messages to NVIDIA Nemotron through Nebius.

    Parameters:
        messages:
            Conversation messages.

        model:
            Optional model override.

        max_tokens:
            Optional output token limit.

    Returns:
        Assistant response as a string.
    """

    selected_model = model or FAST_MODEL

    if max_tokens is None:
        if selected_model == REASONING_MODEL:
            max_tokens = 1200
        else:
            max_tokens = 700

    formatted_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    formatted_messages.extend(messages)

    response = client.chat.completions.create(
        model=selected_model,
        messages=formatted_messages,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content

    if content:
        return content.strip()

    return (
        "I wasn't able to generate a response. "
        "Please try again."
    )