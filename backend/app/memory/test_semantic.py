from app.memory.semantic import (
    store_semantic_memory,
    search_semantic_memories,
)


# Store a test memory
store_semantic_memory(
    memory_id=999,
    content="I prefer Python for backend development.",
    category="preferences",
)

print("Memory stored successfully.")


# Search using different wording
results = search_semantic_memories(
    "What programming language do I like for server-side work?"
)

print("\nSemantic search results:")

for result in results:
    print(result)