from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.auth import (
    auth_router,
)

from app.api.chat import (
    router as chat_router,
)

from app.api.memory import (
    router as memory_router,
)

from app.api.documents import (
    router as documents_router,
)

from app.memory.database import (
    initialize_database,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()

    yield


app = FastAPI(
    title="Private AI Workmate",
    description=(
        "Personal AI system powered by "
        "NVIDIA Nemotron on Nebius Token Factory"
    ),
    version="0.3.0",
    lifespan=lifespan,
)


app.include_router(
    chat_router
)

app.include_router(
    memory_router
)

app.include_router(
    documents_router
)

app.include_router(
    auth_router()
)


@app.get("/")
def root():
    return {
        "project": "Private AI Workmate",
        "status": "running",
        "version": "0.3.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }