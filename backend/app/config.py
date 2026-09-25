import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = Path(
	os.getenv("WORKMATE_DATA_DIR", str(BASE_DIR / "data"))
).resolve()
DATABASE_PATH = Path(
	os.getenv("WORKMATE_DATABASE_PATH", str(DATA_DIR / "workmate.db"))
).resolve()
QDRANT_PATH = Path(
	os.getenv("WORKMATE_QDRANT_PATH", "data/qdrant")
)
DOCUMENTS_PATH = Path(
	os.getenv("WORKMATE_DOCUMENTS_PATH", str(DATA_DIR / "documents"))
).resolve()
AUDIT_FILE = Path(
	os.getenv("WORKMATE_AUDIT_FILE", str(DATA_DIR / "tool_audit.jsonl"))
).resolve()

CORS_ORIGINS = [
	origin.strip()
	for origin in os.getenv(
		"CORS_ORIGINS",
		"http://localhost:5173,http://127.0.0.1:5173",
	).split(",")
	if origin.strip()
]

DATA_DIR.mkdir(parents=True, exist_ok=True)
QDRANT_PATH.mkdir(parents=True, exist_ok=True)
DOCUMENTS_PATH.mkdir(parents=True, exist_ok=True)
