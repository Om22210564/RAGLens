from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.middleware import trace_and_size_middleware
from app.api.routes.health import router as health_router
from app.api.routes.identity import router as identity_router
from app.core.config import get_settings
from app.core.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    app.state.settings = settings
    configure_logging(settings.log_level)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Advanced RAG Platform", version="0.1.0", lifespan=lifespan)
    app.middleware("http")(trace_and_size_middleware)
    app.include_router(health_router)
    app.include_router(identity_router, prefix="/api/v1")
    return app


app = create_app()
