"""FastAPI main application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.database.session import init_db
from src.logging_config import logger
from api.schemas.common import HealthCheckResponse, APIResponse
from api.routes import (
    meetings_router,
    action_items_router,
    analytics_router,
    exports_router,
    evaluation_router,
)

# Initialize database schema on startup
init_db()

app = FastAPI(
    title="AI Meeting Action-Item Extractor API",
    version=settings.APP_VERSION,
    description="Production-grade AI system converting meeting transcripts into structured, validated action items.",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(meetings_router)
app.include_router(action_items_router)
app.include_router(analytics_router)
app.include_router(exports_router)
app.include_router(evaluation_router)


@app.get("/health", response_model=APIResponse[HealthCheckResponse], tags=["Health"])
def health_check():
    """System health check endpoint."""
    return APIResponse(
        success=True,
        data=HealthCheckResponse(
            status="healthy",
            app_name=settings.APP_NAME,
            version=settings.APP_VERSION,
            provider=settings.AI_PROVIDER,
            database="Connected",
        ),
    )


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to AI Meeting Action-Item Extractor API",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
    }
