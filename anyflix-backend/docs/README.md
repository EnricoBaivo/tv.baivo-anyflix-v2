# Anyflix Backend Documentation

This folder contains the technical documentation for the Anyflix Backend service.

## Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture](./ARCHITECTURE.md) | Technical architecture and system design |
| [MVP Goals](./MVP.md) | MVP scope, goals, and current status |
| [API Reference](./API.md) | API endpoints and usage examples |
| [Development](./DEVELOPMENT.md) | Setup, development workflow, and testing |

## Quick Start

```bash
# Install dependencies
uv sync

# Run the server
uvicorn app.main:app --reload

# Run tests
pytest
```

## Project Overview

Anyflix Backend is a Python FastAPI service that provides a unified API for accessing media content from multiple German streaming sources (AniWorld for anime, SerienStream for series). It enriches content with metadata from TMDB (The Movie Database).

### Key Features

- Multi-source media aggregation (AniWorld, SerienStream)
- TMDB metadata enrichment with intelligent matching
- Video extraction from 7+ hosting providers
- Hierarchical series structure (seasons, episodes, movies)
- Redis-based caching for performance
- Comprehensive API documentation (OpenAPI/Swagger)

### Tech Stack

- **Framework**: FastAPI
- **Python**: 3.11+
- **Caching**: Redis (with aiocache)
- **HTTP Client**: httpx/aiohttp
- **Validation**: Pydantic v2
- **Testing**: pytest with pytest-asyncio
