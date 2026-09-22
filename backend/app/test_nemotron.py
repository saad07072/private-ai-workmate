from app.nemotron import client, MODEL, SYSTEM_PROMPT
from app.memory.store import conversation_store


conversation_id = "b1f6e99a-ee99-46fe-b824-f166ea53ecc7"

messages = conversation_store.get_messages(conversation_id)

print("\n===== STORED MESSAGES =====\n")

for message in messages:
    print(message)


response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        *messages,
        {
            "role": "user",
            "content": "What is my name? Answer in one short sentence."
        }
    ],
    max_tokens=200,
)

print("\n===== NEBIUS RESPONSE =====\n")
print(response.model_dump_json(indent=2))