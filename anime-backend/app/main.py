"""FastAPI application for anime backend service."""

import logging

# Import logging setup function
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .dependencies import get_anime_service
from .internal import admin
from .routers import proxy, sources

sys.path.append(str(Path(__file__).parent.parent))

try:
    from lib.utils.logging_config import setup_logging
except ImportError:
    # Fallback if logging_config not available
    def setup_logging(**kwargs):
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper(), logging.INFO)
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup: Configure logging
    setup_logging(
        level=settings.log_level,
        log_file=settings.log_file,
        enable_console=settings.enable_console_logging,
        enable_file=settings.enable_file_logging,
        max_bytes=settings.log_max_bytes,
        backup_count=settings.log_backup_count,
    )

    logger = logging.getLogger(__name__)
    logger.info("🚀 Anime Backend Service starting up...")
    logger.info(f"📊 Log level: {settings.log_level}")
    logger.info(f"📁 Log file: {settings.log_file}")
    logger.info(f"🔧 Debug extractors: {settings.debug_extractors}")
    logger.info(f"🔧 Debug providers: {settings.debug_providers}")

    yield

    # Shutdown
    logger.info("🛑 Anime Backend Service shutting down...")


# Create FastAPI app with comprehensive OpenAPI documentation
app = FastAPI(
    title="Anime Backend Service",
    lifespan=lifespan,
    description="""
    **Python backend service for anime streaming sources** 🎌

    This API provides access to anime content from multiple German streaming sources 
    including AniWorld and SerienStream, with both legacy flat and modern hierarchical endpoints.

    ## Features
    - 🔍 **Search and Discovery**: Find anime across multiple sources
    - 📺 **Hierarchical Episodes**: Organized by seasons with separate movies/OVAs
    - 🎬 **Video Sources**: Extract streaming links from various hosts
    - 🔄 **Backward Compatibility**: Legacy endpoints for existing integrations
    - ⚙️ **Source Preferences**: Configurable language, quality, and host settings

    ## API Versions
    - **🆕 Hierarchical API** (`/sources/{source}/series/*`): Modern structure with seasons & movies
    - **⚠️ Legacy API** (`/sources/{source}/detail`, `/sources/{source}/episodes`): Flat structure (deprecated)

    ## Migration Guide
    For new applications, use the hierarchical endpoints under `/sources/{source}/series/`.
    Legacy endpoints will be removed in v2.0.0.
    """,
    version="1.0.0",
    contact={
        "name": "Anime Backend API",
        "url": "https://github.com/your-repo/anime-backend",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "anime-sources",
            "description": "Core source management and discovery endpoints",
        },
        {
            "name": "hierarchical-api",
            "description": "🆕 Modern hierarchical endpoints with seasons and movies structure",
        },
        {
            "name": "legacy-endpoints",
            "description": "⚠️ Deprecated flat structure endpoints (use hierarchical-api instead)",
        },
    ],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    summary="API Information",
    description="Get basic API information and available sources.",
    response_description="API information with available sources",
    responses={
        200: {
            "description": "Successfully retrieved API information",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Anime Backend Service",
                        "version": "1.0.0",
                        "available_sources": ["aniworld", "serienstream"],
                        "api_docs": "/docs",
                        "openapi_schema": "/openapi.json",
                    }
                }
            },
        }
    },
    tags=["anime-sources"],
)
async def root():
    """
    Get API information and available sources.

    Returns basic information about the API including version,
    available streaming sources, and links to documentation.
    """
    anime_service = get_anime_service()
    return {
        "message": "Anime Backend Service",
        "version": "1.0.0",
        "available_sources": anime_service.get_available_sources(),
        "api_docs": "/docs",
        "openapi_schema": "/openapi.json",
        "features": {
            "hierarchical_api": "Modern structure with seasons and movies",
            "legacy_support": "Backward compatibility maintained",
            "multi_source": "Support for multiple anime sources",
        },
    }


# Include routers
app.include_router(sources.router)
app.include_router(proxy.router)
app.include_router(admin.router)
