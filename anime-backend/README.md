# Anime Backend Service

A Python backend service that replicates the functionality of JavaScript anime streaming sources (AniWorld and SerienStream). Built with FastAPI and designed to provide REST API endpoints for anime content discovery and streaming.

## Features

- **Multiple Sources**: Support for AniWorld and SerienStream
- **REST API**: FastAPI-based web service with automatic documentation
- **Search & Discovery**: Popular anime, latest updates, and search functionality
- **Episode Management**: Detailed anime information with episode lists
- **Video Sources**: Extract video streaming links from various hosts (Doodstream, Vidmoly, Vidoza, Filemoon, SpeedFiles, Luluvdo)
- **Playlist Support**: M3U8 and JWPlayer playlist parsing
- **Async Operations**: High-performance async/await implementation
- **Type Safety**: Full Pydantic models for request/response validation

## Quick Start

### Prerequisites

- Python 3.11+
- uv (Python package manager)

### Installation

1. Clone the repository and navigate to the anime-backend directory
2. Install dependencies:
   ```bash
   uv sync
   ```

### Running the Service

Start the development server:
```bash
uv run python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### Sources

- `GET /sources` - List available anime sources
- `GET /sources/{source}/preferences` - Get source preferences

### Content Discovery

- `GET /sources/{source}/popular` - Get popular anime
- `GET /sources/{source}/latest` - Get latest updates
- `GET /sources/{source}/search?q={query}` - Search anime

### Anime Details

- `GET /sources/{source}/detail?url={anime_url}` - Get anime details
- `GET /sources/{source}/videos?url={episode_url}` - Get video sources

### Health

- `GET /health` - Health check endpoint

## Available Sources

### AniWorld (`aniworld`)
- Base URL: https://aniworld.to
- Language: German
- Features: Popular, Latest, Search, Details, Videos

### SerienStream (`serienstream`)
- Base URL: https://s.to
- Language: German
- Features: Popular, Latest, Search, Details, Videos with upload dates

## API Usage Examples

### Get Popular Anime from AniWorld
```bash
curl "http://localhost:8000/sources/aniworld/popular"
```

### Search for Anime
```bash
curl "http://localhost:8000/sources/aniworld/search?q=naruto"
```

### Get Anime Details
```bash
curl "http://localhost:8000/sources/aniworld/detail?url=/anime/stream/naruto"
```

### Get Video Sources
```bash
curl "http://localhost:8000/sources/aniworld/videos?url=/anime/stream/naruto/staffel-1/episode-1"
```

## Project Structure

```
src/anime_backend/
├── models/           # Pydantic models for data structures
├── providers/        # Source provider implementations
├── extractors/       # Video extractor modules
├── services/         # Business logic services
├── utils/           # Utility functions and helpers
├── api.py           # FastAPI application
└── config.py        # Configuration management
```

## Architecture

The service is built with a modular architecture:

1. **Models**: Pydantic models define the data structures
2. **Providers**: Implement source-specific logic for each anime site
3. **Extractors**: Video extractor modules for different hosting services
4. **Services**: Orchestrate provider operations and handle business logic
5. **API**: FastAPI endpoints expose functionality via REST API
6. **Utils**: Shared utilities for HTTP clients, HTML parsing, etc.

## Video Extractors

The service includes specialized extractors for various video hosting services:

- **Doodstream**: Handles Doodstream video links with token-based authentication
- **Vidmoly**: Extracts M3U8 playlists from Vidmoly hosts
- **Vidoza**: Direct MP4 link extraction from Vidoza
- **Filemoon**: JWPlayer-based extraction with iframe support
- **SpeedFiles**: Multi-stage base64 decoding for encrypted URLs
- **Luluvdo**: Embed-based JWPlayer extraction
- **M3U8**: Generic M3U8 playlist parser with quality detection
- **JWPlayer**: Universal JWPlayer setup parser

Each extractor handles the specific authentication, decoding, or parsing requirements of its target service.

## Configuration

The service can be configured via environment variables or `.env` file:

```env
HOST=0.0.0.0
PORT=8000
RELOAD=true
LOG_LEVEL=INFO
REQUEST_TIMEOUT=30
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **httpx**: Async HTTP client for making requests
- **BeautifulSoup4**: HTML parsing and scraping
- **Pydantic**: Data validation and serialization
- **uvicorn**: ASGI server for running the application

## Development

### Adding New Sources

1. Create a new provider class inheriting from `BaseProvider`
2. Implement required methods: `get_popular`, `get_latest_updates`, `search`, `get_detail`, `get_video_list`
3. Add the provider to `AnimeService`
4. Update documentation

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
uv run black src/
uv run isort src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is for educational purposes. Please respect the terms of service of the anime streaming sources.

## Disclaimer

This software is provided for educational and research purposes only. Users are responsible for complying with the terms of service of any websites they access through this software.
