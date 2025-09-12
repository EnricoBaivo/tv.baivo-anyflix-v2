# Anime Backend Service

A Python backend service that replicates the functionality of JavaScript anime streaming sources (AniWorld and SerienStream). Built with FastAPI and designed to provide REST API endpoints for anime content discovery and streaming.

## Features

### Core Features
- **Multiple Sources**: Support for AniWorld and SerienStream
- **REST API**: FastAPI-based web service with automatic documentation
- **Search & Discovery**: Popular anime, latest updates, and search functionality
- **Episode Management**: Detailed anime information with episode lists
- **Video Sources**: Extract video streaming links from various hosts (Doodstream, Vidmoly, Vidoza, Filemoon, SpeedFiles, Luluvdo)
- **Playlist Support**: M3U8 and JWPlayer playlist parsing
- **Async Operations**: High-performance async/await implementation
- **Type Safety**: Full Pydantic models for request/response validation

### 🆕 Enhanced Metadata Features
- **AniList Integration**: Comprehensive AniList API support with GraphQL queries
- **Rich Metadata**: Automatic enrichment with AniList data (descriptions, ratings, genres, characters, staff)
- **Smart Matching**: Intelligent title matching between streaming sources and AniList database
- **Metadata Coverage**: Track and report metadata enrichment statistics
- **Flexible Control**: Enable/disable metadata enrichment per request or globally
- **Caching System**: Efficient caching of AniList lookups for better performance
- **Enhanced Responses**: All endpoints now available with rich metadata versions

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

### 🎬 Media Sources (Unified with Optional Metadata)

- `GET /sources` - List available streaming sources with metadata capabilities
- `GET /sources/{source}/preferences` - Get source preferences

#### Content Discovery
- `GET /sources/{source}/popular` - Popular anime (add `?include_metadata=true` for AniList data)
- `GET /sources/{source}/latest` - Latest updates (add `?include_metadata=true` for enrichment)
- `GET /sources/{source}/search` - Search anime (add `?include_metadata=true` for comprehensive data)

#### Anime Details
- `GET /sources/{source}/videos` - Get video streams (add `?include_context=true` for episode info)
- `GET /sources/{source}/series` - Complete series structure (add `?include_metadata=true` for AniList data)

#### 📊 Metadata Management
- `GET /sources/metadata/stats` - Get metadata enrichment statistics
- `POST /sources/metadata/toggle` - Enable/disable metadata enrichment
- `GET /sources/metadata/cache/info` - Get cache information and hit rates
- `POST /sources/metadata/cache/clear` - Clear metadata cache

**💡 Pro Tip**: Add `?include_metadata=true` to any content endpoint to get rich AniList data including ratings, genres, characters, trailers, and more!

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

### AniList (`anilist`)
- Base URL: https://graphql.anilist.co
- Language: Multiple (English, Japanese, etc.)
- Features: Comprehensive anime/manga database with detailed metadata, relations, characters, staff, and recommendations

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

### AniList API Examples

#### Search for Anime on AniList
```python
from lib.services.anilist_service import AniListService
from lib.models.anilist import MediaType

async def search_anime():
    async with AniListService() as anilist:
        results = await anilist.search_anime("Attack on Titan")
        for anime in results.media:
            print(f"{anime.title.userPreferred} - Score: {anime.averageScore}")
```

#### Get Detailed Anime Information
```python
async def get_anime_details():
    async with AniListService() as anilist:
        # Get Cowboy Bebop details
        anime = await anilist.get_media_by_id(1)
        print(f"Title: {anime.title.userPreferred}")
        print(f"Episodes: {anime.episodes}")
        print(f"Genres: {', '.join(anime.genres)}")
```

#### Get Trending Anime
```python
async def get_trending():
    async with AniListService() as anilist:
        trending = await anilist.get_trending_anime(per_page=10)
        for i, anime in enumerate(trending.media, 1):
            print(f"{i}. {anime.title.userPreferred}")
```

#### Get Seasonal Anime
```python
async def get_seasonal():
    async with AniListService() as anilist:
        # Get Fall 2023 anime
        seasonal = await anilist.get_seasonal_anime("FALL", 2023)
        for anime in seasonal.media:
            print(f"{anime.title.userPreferred} - {anime.season} {anime.seasonYear}")
```

## Project Structure

```
lib/
├── models/           # Pydantic models for data structures
│   ├── anilist.py   # AniList API models (Media, Character, Studio, etc.)
│   ├── base.py      # Base models (Episode, VideoSource, etc.)
│   └── responses.py # API response models
├── providers/        # Source provider implementations
│   ├── aniworld.py  # AniWorld scraping provider
│   ├── serienstream.py # SerienStream scraping provider
│   └── base.py      # Base provider interface
├── extractors/       # Video extractor modules
├── services/         # Business logic services
│   ├── anime_service.py   # Anime scraping service
│   └── anilist_service.py # AniList API service
├── utils/           # Utility functions and helpers
└── ...
app/
├── main.py          # FastAPI application
├── config.py        # Configuration management
└── ...
tests/
├── unit/
│   ├── test_anime_service.py
│   └── test_anilist_service.py
└── integration/
```

## Architecture

The service is built with a modular architecture:

1. **Models**: Pydantic models define the data structures
   - **AniList Models**: Complete GraphQL schema models for AniList API
   - **Base Models**: Core models for anime, episodes, video sources
   - **Response Models**: API response wrappers
2. **Providers**: Implement source-specific logic for each anime site
3. **Extractors**: Video extractor modules for different hosting services
4. **Services**: Orchestrate provider operations and handle business logic
   - **AnimeService**: Manages scraping providers (AniWorld, SerienStream)
   - **AniListService**: Handles AniList GraphQL API communication
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

## 🆕 Enhanced Metadata Integration

The service now includes two API tiers:

### Standard API (`/sources/`)
- Basic anime information from streaming sources
- Fast responses with essential data
- Episode lists and video sources
- Minimal metadata overhead

### Enhanced API (`/enhanced/sources/`)
- **Rich AniList metadata integration (ANIME only)**
- Comprehensive anime information including:
  - Detailed descriptions and synopses
  - Complete genre classifications
  - Character information with voice actors
  - Staff details (directors, writers, studios)
  - Related anime and recommendations
  - Official ratings and popularity scores
  - External links (official sites, streaming platforms)
  - Release dates and seasonal information
  - Content tags and themes

### Smart Title Matching
The enhanced service uses intelligent algorithms to match anime titles between streaming sources and AniList:
- **Normalized matching**: Handles different title formats and languages
- **Synonym support**: Recognizes alternative titles and common aliases
- **Confidence scoring**: Each match includes a confidence score (0.0-1.0)
- **Fallback handling**: Graceful degradation when no match is found

### Metadata Coverage & Statistics
- **Coverage reporting**: Track percentage of results with successful metadata matches
- **Performance metrics**: Monitor cache hit rates and response times  
- **Match statistics**: View overall success rates and confidence scores
- **Professional caching**: Uses `cachetools` TTLCache with automatic expiration and LRU eviction
- **Cache management**: Clear, resize, and configure TTL for optimal performance
- **Cache analytics**: Detailed cache statistics including hit rates and size information

### Enhanced Response Examples

#### Enhanced Search Response
```json
{
  "list": [
    {
      "name": "Attack on Titan",
      "image_url": "https://example.com/image.jpg",
      "link": "/anime/stream/attack-on-titan",
      "anilist_id": 16498,
      "match_confidence": 0.95,
      "anilist_data": {
        "id": 16498,
        "title": {"userPreferred": "Shingeki no Kyojin"},
        "averageScore": 84,
        "genres": ["Action", "Drama", "Fantasy"],
        "description": "Several hundred years ago, humans were nearly exterminated by Titans...",
        "episodes": 25,
        "studios": [{"name": "Wit Studio"}],
        "characters": [
          {
            "name": "Eren Jaeger",
            "role": "MAIN",
            "voice_actors": ["Yuki Kaji"]
          }
        ]
      }
    }
  ],
  "has_next_page": false,
  "metadata_coverage": 85.5
}
```

#### Metadata Statistics
```json
{
  "total_requests": 150,
  "anilist_matches": 128,
  "match_rate": 85.3,
  "average_confidence": 0.87,
  "cache_hits": 45,
  "cache_misses": 105
}
```

## AniList Service Features

The AniListService provides comprehensive access to the AniList GraphQL API:

### Core Functionality
- **Media Search**: Search anime and manga by title with filters
- **Media Details**: Get detailed information including relations, characters, staff
- **Trending Content**: Access trending anime and manga
- **Popular Content**: Get most popular anime and manga
- **Seasonal Anime**: Browse anime by season and year
- **Upcoming Releases**: Find upcoming anime and manga
- **Top Rated**: Access highest-rated content

### Available Methods
- `get_media_by_id(media_id)` - Get detailed media information
- `search_media(query, type, **filters)` - Search with advanced filters
- `search_anime(query)` / `search_manga(query)` - Type-specific searches
- `get_trending_anime()` - Current trending anime
- `get_popular_anime()` - Most popular anime
- `get_top_rated_anime()` - Highest-rated anime
- `get_seasonal_anime(season, year)` - Seasonal anime
- `get_upcoming_anime()` - Upcoming releases
- `get_media_relations(media_id)` - Media with relation information
- `get_media_characters(media_id)` - Media with character information
- `get_media_staff(media_id)` - Media with staff information

### Data Models
The service includes comprehensive Pydantic models covering:
- **Media**: Complete anime/manga information
- **Characters**: Character details with voice actors
- **Staff**: Staff information with roles
- **Studios**: Animation studio details
- **Reviews**: User reviews and ratings
- **Recommendations**: Related media suggestions
- **External Links**: Official and streaming links
- **Statistics**: Score distributions and popularity metrics

### Usage Example
```python
# Use in your code
from lib.services.anilist_service import AniListService

async with AniListService() as anilist:
    # Search for anime
    results = await anilist.search_anime("Your Name")
    
    # Get detailed information
    anime = await anilist.get_media_by_id(129)  # Your Name ID
    print(f"Title: {anime.title.userPreferred}")
    print(f"Score: {anime.averageScore}/100")
    print(f"Genres: {', '.join(anime.genres)}")
```

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
