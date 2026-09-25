from qdrant_client import QdrantClient

from app.config import QDRANT_PATH


# One shared Qdrant client for the entire application.
qdrant_client = QdrantClient(
    path=str(QDRANT_PATH)
)