# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           FastAPI App                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │   Sources   │  │   Series    │  │    Admin    │   Routers       │
│  │   Router    │  │   Router    │  │   Router    │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
└─────────┼────────────────┼────────────────┼─────────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Provider Registry                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Shared: providers, get_provider()               │   │
│  │              TMDB: tmdb_service, enrichment_service          │   │
│  └─────────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   AniWorld      │ │  SerienStream   │ │     TMDB        │
│   Provider      │ │   Provider      │ │    Service      │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                    │
         ▼                   ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  aniworld.to    │ │ serienstream.to │ │ api.tmdb.org    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Directory Structure

```
anyflix-backend/
├── app/                      # FastAPI application
│   ├── main.py               # Application entry point
│   ├── config.py             # Settings and configuration
│   ├── providers.py          # Shared provider registry
│   ├── routers/              # API route handlers
│   │   ├── sources.py        # Content discovery & video endpoints
│   │   └── series.py         # Series/season/episode endpoints
│   └── internal/
│       └── admin.py          # Admin/cache management endpoints
│
├── lib/                      # Core library modules
│   ├── models/               # Pydantic data models
│   │   ├── base.py           # Core models (Episode, Season, etc.)
│   │   ├── responses.py      # API response models
│   │   └── tmdb.py           # TMDB-specific models
│   │
│   ├── providers/            # Streaming source providers
│   │   ├── base.py           # Abstract base provider
│   │   ├── aniworld.py       # AniWorld anime provider
│   │   └── serienstream.py   # SerienStream series provider
│   │
│   ├── services/             # Business logic services
│   │   ├── tmdb_service.py           # TMDB API client
│   │   ├── tmdb_enrichment_service.py# TMDB data enrichment
│   │   ├── matching_service.py       # Title matching algorithms
│   │   └── series_converter.py       # Episode/season organization
│   │
│   ├── extractors/           # Video host extractors
│   │   ├── base.py           # Base extractor interface
│   │   ├── extract_any.py    # Extractor dispatcher
│   │   ├── voe_extractor.py  # VOE video extraction
│   │   ├── vidmoly_extractor.py
│   │   ├── vidoza_extractor.py
│   │   ├── filemoon_extractor.py
│   │   ├── dood_extractor.py
│   │   ├── luluvdo_extractor.py
│   │   ├── speedfiles_extractor.py
│   │   └── ytdlp_extractor.py # YouTube/trailer extraction
│   │
│   └── utils/                # Utility modules
│       ├── client.py         # HTTP client wrapper
│       ├── caching.py        # Redis caching utilities
│       ├── parser.py         # HTML parsing utilities
│       ├── helpers.py        # General helpers
│       └── logging_config.py # Logging configuration
│
├── tests/                    # Test suite
│   └── extractors/           # Extractor tests
│
└── docs/                     # Documentation
```

## Key Components

### Providers

Providers are responsible for fetching content from streaming sources. They inherit from `BaseProvider` and implement:

- `get_popular()` - Trending/popular content
- `get_latest_updates()` - Recently updated content
- `search(query)` - Content search
- `get_detail(url)` - Series metadata and episodes
- `get_video_list(url)` - Video streaming sources

### Services

Services handle business logic:

- **TMDBService**: Direct TMDB API integration
- **TMDBEnrichmentService**: Enriches provider data with TMDB metadata
- **MatchingService**: Fuzzy matching for title/metadata correlation
- **SeriesConverterService**: Converts flat episode lists to hierarchical structure

### Extractors

Extractors handle video source extraction from various hosting providers:

| Extractor | Host | Status |
|-----------|------|--------|
| voe_extractor | VOE | Active |
| vidmoly_extractor | Vidmoly | Active |
| vidoza_extractor | Vidoza | Active |
| filemoon_extractor | Filemoon | Active |
| dood_extractor | Doodstream | Active |
| luluvdo_extractor | Luluvdo | Active |
| speedfiles_extractor | SpeedFiles | Active |
| ytdlp_extractor | YouTube | Active |

### Caching Strategy

The system uses Redis for caching with namespace-based key organization:

```
endpoints:aniworld:popular      # Popular content
endpoints:aniworld:latest       # Latest updates
endpoints:aniworld:series:detail # Series details
services:tmdb:search:multi      # TMDB search results
services:tmdb:tv:details        # TMDB TV details
```

Cache TTLs are configured per data type:
- Popular/Latest: 10-15 minutes
- Search results: 30 minutes
- Details: 1-2 hours
- TMDB config: 24 hours

## Data Flow

### Content Discovery

```
Client Request → Router → Provider → Web Scraping → Response
                           ↓
                        Caching
```

### Series Details with TMDB Enrichment

```
Client Request
      ↓
   Router
      ↓
   Provider.get_detail()
      ↓
TMDBEnrichmentService.enrich_media_info()
      ↓
MatchingService.calculate_match_confidence()
      ↓
SeriesConverterService.convert_to_hierarchical()
      ↓
   Response
```

### Video Extraction

```
Client Request (episode URL)
      ↓
   Provider.get_video_list()
      ↓
   Parse available hosts
      ↓
   extract_any() dispatcher
      ↓
   Host-specific extractor
      ↓
   VideoSource[]
```
