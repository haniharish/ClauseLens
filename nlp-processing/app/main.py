"""
ClauseLens NLP Service — Application Entry Point
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import get_settings
from app.utils.logger import get_logger, setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.environment != "test":
        setup_logging("DEBUG" if settings.environment == "development" else "INFO")
    logger = get_logger("clauselens.startup")
    logger.info(
        "clauselens_nlp_service_starting",
        environment=settings.environment,
        host=settings.api_host,
        port=settings.api_port,
        embedding_model=settings.embedding_model,
        llm_provider=settings.llm_provider,
        lightweight_mode=settings.lightweight_mode,
    )
    yield
    logger.info("clauselens_nlp_service_shutting_down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ClauseLens NLP Service",
        description=(
            "AI-powered NLP processing module for ClauseLens: Context-Aware "
            "Terms & Conditions Risk Summarization.\n\n"
            "**Member 4 — NLP & AI Processing**\n\n"
            "Processes legal documents, extracts clauses, classifies them into "
            "11 categories, generates semantic embeddings, and produces plain-English "
            "summaries using configurable LLM providers."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Allow Django backend to call this service
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Restrict in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/", include_in_schema=False)
    async def root():
        return {
            "service": "ClauseLens NLP Service",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/nlp/health/",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
        log_level="debug" if settings.environment == "development" else "info",
    )
