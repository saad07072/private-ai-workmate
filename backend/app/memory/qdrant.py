from qdrant_client import QdrantClient


QDRANT_PATH = "data/qdrant"


# One shared Qdrant client for the entire application.
qdrant_client = QdrantClient(
    path=QDRANT_PATH
)