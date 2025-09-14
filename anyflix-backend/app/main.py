"""FastAPI application for anime backend service."""

import logging

# Import logging setup function
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .internal import admin
from .routers import sources

sys.path.append(str(Path(__file__).parent.parent))

try:
    from lib.utils.logging_config import setup_logging
except ImportError:
    # Fallback if logging_config not available
    def setup_logging(**kwargs):
        logging.basicConfig(
            level=getattr(logging, settings.log_level.upper(), logging.INFO)
        )


class DebugMiddleware(BaseHTTPMiddleware):
    """Middleware for debugging requests and responses."""

    def __init__(self, app, logger_name: str = "debug_middleware") -> None:
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)

    async def dispatch(self, request: Request, call_next):
        # Log request
        start_time = time.time()
        self.logger.info(f"🔵 {request.method} {request.url}")
        self.logger.debug(f"Request headers: {dict(request.headers)}")

        # Log query parameters for proxy endpoints
        if "/proxy/" in str(request.url):
            self.logger.debug(f"Query params: {dict(request.query_params)}")

        # Process request
        try:
            response = await call_next(request)

            # Log response
            process_time = time.time() - start_time
            self.logger.info(
                f"🟢 {request.method} {request.url} -> {response.status_code} ({process_time:.3f}s)"
            )

            # Log error responses with more detail
            if response.status_code >= 400:
                self.logger.error(
                    f"❌ Error response: {response.status_code} for {request.method} {request.url}"
                )
                if hasattr(response, "body"):
                    self.logger.debug(f"Error response body: {response.body}")

            return response

        except Exception as e:
            process_time = time.time() - start_time
            self.logger.error(
                f"🔴 {request.method} {request.url} -> EXCEPTION ({process_time:.3f}s): {e!s}",
                exc_info=True,
            )
            raise


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

    # Initialize cache if enabled
    if settings.enable_caching:
        try:
            from lib.utils.caching import initialize_cache

            initialize_cache(
                redis_host=settings.redis_host,
                redis_port=settings.redis_port,
                redis_db=settings.redis_db,
                redis_password=settings.redis_password,
            )
            logger.info("✅ Cache initialized successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to initialize cache: {e}")
    else:
        logger.info("🚫 Caching disabled in configuration")

    yield

    # Shutdown
    logger.info("🛑 Anime Backend Service shutting down...")


# Create FastAPI app with comprehensive OpenAPI documentation
app = FastAPI(
    title="Media Streaming Backend Service",
    lifespan=lifespan,
    description="""
    **Python backend service for media streaming sources** 🎬

    Complete media streaming API providing access to content from multiple streaming sources
    with a modern, logically organized structure. Currently supports anime content from German sources
    including AniWorld and SerienStream, with extensible architecture for other media types.

    ## 🎬 Media API Structure

    ### 📋 Source Management
    - List available streaming sources: `GET /sources/`
    - Get source-specific preferences: `GET /sources/{source}/preferences`

    ### 🔍 Content Discovery
    - Browse popular content: `GET /sources/{source}/popular?page=1`
    - Get latest updates: `GET /sources/{source}/latest?page=1`
    - Search by title: `GET /sources/{source}/search?q=attack&page=1`

    ### 📺 Series Structure
    - Complete series data: `GET /sources/{source}/series?url=...`
    - All seasons: `GET /sources/{source}/series/seasons?url=...`
    - Specific season: `GET /sources/{source}/series/seasons/{season_num}?url=...`
    - Specific episode: `GET /sources/{source}/series/seasons/{season}/episodes/{episode}?url=...`
    - Movies/OVAs: `GET /sources/{source}/series/movies?url=...`

    ### 🎬 Video & Media
    - Extract streaming links: `GET /sources/{source}/videos?url=...`
    - Trailer extraction: `POST /sources/trailer`

    ## ⚡ Quick Start Examples
    ```bash
    # 1. List sources
    curl http://localhost:8000/sources/

    # 2. Search content
    curl "http://localhost:8000/sources/aniworld/search?q=attack"

    # 3. Get series details
    curl "http://localhost:8000/sources/aniworld/series?url=/anime/stream/attack-on-titan"

    # 4. Get video sources
    curl "http://localhost:8000/sources/aniworld/videos?url=/episode/url"
    ```

    ## 📊 Features
    - **Metadata Enrichment**: Automatic TMDB and AniList data integration
    - **Hierarchical Structure**: Organized seasons, episodes, and movies
    - **Multiple Sources**: Support for 2+ streaming sources
    - **Video Extraction**: 10+ hosting provider support
    - **Error Handling**: Comprehensive error responses
    - **Type Safety**: Full OpenAPI schema with examples
    """,
    version="1.0.0",
    contact={
        "name": "Media Streaming Backend API",
        "url": "https://github.com/your-repo/media-backend",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "media-api",
            "description": "Complete media streaming API with discovery, content management, and video sources",
        },
        {
            "name": "proxy",
            "description": "Video proxy endpoints for CORS handling and streaming",
        },
        {
            "name": "admin",
            "description": "Administrative endpoints for service management",
        },
    ],
)

# Add debugging middleware (only in debug mode)
if settings.debug_extractors or settings.debug_providers:
    app.add_middleware(DebugMiddleware)

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
    tags=["media-api"],
)
async def root():
    """
    Get API information and available sources.

    Returns basic information about the API including version,
    available streaming sources, and links to documentation.
    """
    return {
        "message": "Media Streaming Backend Service",
        "version": "1.0.0",
        "available_sources": ["aniworld", "serienstream"],
        "api_docs": "/docs",
        "openapi_schema": "/openapi.json",
        "features": {
            "hierarchical_api": "Modern structure with seasons and movies",
            "video_proxy": "Built-in video proxy for CORS handling",
            "multi_source": "Support for multiple streaming sources",
            "extractors": "Support for 10+ video hosting services",
            "media_types": "Extensible architecture for various media content",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Include routers
app.include_router(sources.router)
app.include_router(admin.router)
