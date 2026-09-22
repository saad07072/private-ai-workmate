import os

from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env
load_dotenv()


# Get Nebius API key
api_key = os.getenv("NEBIUS_API_KEY")

if not api_key:
    raise RuntimeError(
        "NEBIUS_API_KEY is not configured."
    )


# Nebius Token Factory OpenAI-compatible client
client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=api_key,
)


# NVIDIA Nemotron model
MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"


# Main system instructions
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


def ask_nemotron(messages: list[dict]) -> str:
    """
    Send conversation messages to NVIDIA Nemotron
    through Nebius Token Factory.

    Parameters:
        messages: List of chat messages containing
                  role and content.

    Returns:
        The assistant's response as a string.
    """

    # Start with our system instructions
    formatted_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    # Add conversation history and memory context
    formatted_messages.extend(messages)

    # Send request to Nemotron
    response = client.chat.completions.create(
        model=MODEL,
        messages=formatted_messages,
        max_tokens=500,
    )

    # Extract assistant response
    content = response.choices[0].message.content

    # Prevent an empty response from reaching the API
    if content:
        return content.strip()

    return (
        "I wasn't able to generate a response. "
        "Please try again."
    )