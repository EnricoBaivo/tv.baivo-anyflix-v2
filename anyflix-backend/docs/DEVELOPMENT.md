# Development Guide

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Redis (optional, for caching)
- TMDB API key (for metadata enrichment)

## Setup

### 1. Clone and Install Dependencies

```bash
cd anyflix-backend

# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 2. Environment Configuration

Create a `.env` file:

```env
# API Keys
TMDB_API_KEY=your_tmdb_api_key_here

# Server Settings
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/anime_backend.log
DEBUG_EXTRACTORS=false
DEBUG_PROVIDERS=false

# Cache Settings
ENABLE_CACHING=true
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

### 3. Start Redis (Optional)

```bash
# Using Docker
docker run -d --name redis -p 6379:6379 redis

# Or using docker-compose
docker-compose up -d redis
```

### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or using the run script
./run.sh

# Or using Makefile
make run
```

The API will be available at `http://localhost:8000`.

## Project Structure

```
anyflix-backend/
├── app/                  # FastAPI application
│   ├── main.py           # Entry point
│   ├── config.py         # Configuration
│   ├── providers.py      # Shared provider registry
│   └── routers/          # API endpoints
├── lib/                  # Core library
│   ├── models/           # Pydantic models
│   ├── providers/        # Source providers
│   ├── services/         # Business services
│   ├── extractors/       # Video extractors
│   └── utils/            # Utilities
├── tests/                # Test suite
├── docs/                 # Documentation
└── logs/                 # Log files
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=lib --cov=app

# Run specific test file
pytest tests/extractors/test_voe.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Lint with ruff
ruff check .

# Format with black
black .

# Type checking with mypy
mypy app lib
```

### Adding a New Provider

1. Create `lib/providers/newprovider.py`:

```python
from lib.models.base import MediaSource
from lib.providers.base import BaseProvider

class NewProvider(BaseProvider):
    def __init__(self):
        source = MediaSource(
            name="NewProvider",
            lang="de",
            base_url="https://newprovider.to",
            ...
        )
        super().__init__(source)

    async def get_popular(self, page: int = 1):
        # Implementation
        pass

    async def get_latest_updates(self, page: int = 1):
        # Implementation
        pass

    async def search(self, query: str, page: int = 1, lang: str = None):
        # Implementation
        pass

    def get_source_preferences(self):
        # Implementation
        pass
```

2. Register in `app/providers.py`:

```python
from lib.providers.newprovider import NewProvider

providers: dict[str, BaseProvider] = {
    "aniworld": AniWorldProvider(),
    "serienstream": SerienStreamProvider(),
    "newprovider": NewProvider(),
}
```

### Adding a New Extractor

1. Create `lib/extractors/newhost_extractor.py`:

```python
from lib.models.base import VideoSource

async def newhost_extractor(
    url: str,
    headers: dict[str, str] | None = None
) -> list[VideoSource]:
    # Extraction logic
    return [
        VideoSource(
            url="https://stream-url",
            original_url=url,
            quality="1080p",
            host="newhost",
            format="m3u8",
        )
    ]
```

2. Register in `lib/extractors/extract_any.py`:

```python
from .newhost_extractor import newhost_extractor

EXTRACTOR_METHODS = {
    ...
    "newhost": newhost_extractor,
}
```

3. Export in `lib/extractors/__init__.py`:

```python
from .newhost_extractor import newhost_extractor

__all__ = [
    ...
    "newhost_extractor",
]
```

## Debugging

### Enable Debug Logging

Set in `.env`:
```env
LOG_LEVEL=DEBUG
DEBUG_EXTRACTORS=true
DEBUG_PROVIDERS=true
```

### View Logs

```bash
# Real-time log viewing
tail -f logs/anime_backend.log

# Filter by level
grep ERROR logs/anime_backend.log
```

### Debug Middleware

When `DEBUG_EXTRACTORS` or `DEBUG_PROVIDERS` is enabled, the `DebugMiddleware` logs:
- All incoming requests
- Response status codes and timing
- Error responses with details

## Caching

### Cache Configuration

Cache namespaces follow this pattern:
- `endpoints:{provider}:{endpoint}` - Provider endpoints
- `services:tmdb:{operation}` - TMDB service calls
- `extractors:{host}:extract` - Video extraction

### Cache Management

```bash
# View cache stats
curl http://localhost:8000/admin/cache/stats

# Clear specific cache
curl -X POST http://localhost:8000/admin/cache/clear/endpoints:aniworld:popular

# Flush all cache
curl -X POST http://localhost:8000/admin/cache/flush
```

### Disable Caching

Set in `.env`:
```env
ENABLE_CACHING=false
```

## Common Issues

### Redis Connection Error

If you see "Failed to initialize Redis cache", ensure Redis is running:
```bash
docker ps | grep redis
```

The application will fall back to in-memory caching if Redis is unavailable.

### TMDB API Errors

If TMDB enrichment fails:
1. Check your `TMDB_API_KEY` is set correctly
2. Verify API rate limits haven't been exceeded
3. The system will continue without TMDB data if errors occur

### Extractor Failures

Video extractors may fail due to:
- Host-side changes (update extractor logic)
- Rate limiting (add delays between requests)
- Geo-blocking (some hosts may be region-restricted)

## API Documentation

Access interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Generate OpenAPI schema:
```bash
python generate_openapi.py
```
