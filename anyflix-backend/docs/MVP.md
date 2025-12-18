# MVP Goals and Status

## Overview

The Anyflix Backend MVP provides a unified API for streaming media content from German sources with TMDB metadata enrichment.

## MVP Scope

### In Scope

- [x] AniWorld provider for anime content
- [x] SerienStream provider for series content
- [x] TMDB metadata enrichment
- [x] Hierarchical series structure (seasons/episodes/movies)
- [x] Video extraction from multiple hosts
- [x] Redis caching
- [x] OpenAPI documentation

### Out of Scope (Future)

- [ ] User authentication
- [ ] Watch history/progress
- [ ] Favorites/bookmarks
- [ ] Multiple language support (currently German-focused)
- [ ] Additional streaming sources

## API Structure

### Content Discovery

| Endpoint | Description | Status |
|----------|-------------|--------|
| `GET /sources/` | List available sources | ✅ |
| `GET /sources/{source}/popular` | Get popular content | ✅ |
| `GET /sources/{source}/latest` | Get latest updates | ✅ |
| `GET /sources/{source}/search` | Search content | ✅ |

### Series Operations

| Endpoint | Description | Status |
|----------|-------------|--------|
| `GET /sources/{source}/series` | Get series overview | ✅ |
| `GET /sources/{source}/series/seasons` | Get all seasons | ✅ |
| `GET /sources/{source}/series/seasons/{num}` | Get specific season | ✅ |
| `GET /sources/{source}/series/seasons/{s}/episodes/{e}` | Get specific episode | ✅ |
| `GET /sources/{source}/series/movies` | Get movies/OVAs | ✅ |
| `GET /sources/{source}/series/movies/{num}` | Get specific movie | ✅ |

### Video & Media

| Endpoint | Description | Status |
|----------|-------------|--------|
| `GET /sources/{source}/videos` | Get video streaming links | ✅ |
| `GET /sources/trailer` | Extract trailer URL | ✅ |

### Admin

| Endpoint | Description | Status |
|----------|-------------|--------|
| `GET /admin/sources/status` | Get sources status | ✅ |
| `GET /admin/cache/stats` | Get cache statistics | ✅ |
| `POST /admin/cache/clear/{prefix}` | Clear cache prefix | ✅ |
| `POST /admin/cache/flush` | Flush all cache | ✅ |

## Response Structure

### Content List Response

```json
{
  "type": "anime",
  "list": [
    {
      "name": "Series Name",
      "image_url": "https://...",
      "link": "/anime/stream/series-slug",
      "provider": "AniWorld",
      "available_languages": ["de", "en", "de_sub"],
      "media_info": { ... }
    }
  ],
  "has_next_page": true
}
```

### Series Detail Response

```json
{
  "type": "anime",
  "tmdb_data": { ... },
  "match_confidence": 0.95,
  "length": 3,
  "series": {
    "slug": "series-slug",
    "seasons": [
      {
        "season": 1,
        "title": "Staffel 1",
        "episodes": [
          {
            "season": 1,
            "episode": 1,
            "title": "Episode Title",
            "url": "/anime/stream/series/staffel-1/episode-1",
            "tmdb_overview": "...",
            "tmdb_still_path": "..."
          }
        ]
      }
    ],
    "movies": []
  }
}
```

### Video Sources Response

```json
{
  "type": "anime",
  "videos": [
    {
      "url": "https://streamable-url...",
      "original_url": "https://host/...",
      "quality": "Deutsch Dub 1080p VOE",
      "language": "de",
      "type": "Dub",
      "host": "voe",
      "format": "m3u8"
    }
  ]
}
```

## Models Reference

### Core Models

| Model | Purpose | Location |
|-------|---------|----------|
| `MediaInfo` | Detailed media information | `lib/models/base.py` |
| `SearchResult` | Search result item | `lib/models/base.py` |
| `Episode` | Episode information | `lib/models/base.py` |
| `Season` | Season with episodes | `lib/models/base.py` |
| `Movie` | Movie/OVA/Special | `lib/models/base.py` |
| `SeriesDetail` | Hierarchical series structure | `lib/models/base.py` |
| `VideoSource` | Video streaming source | `lib/models/base.py` |

### Response Models

| Model | Purpose | Location |
|-------|---------|----------|
| `PaginatedSearchResultResponse` | Paginated content list | `lib/models/responses.py` |
| `SeriesDetailResponse` | Full series data | `lib/models/responses.py` |
| `SeasonResponse` | Single season data | `lib/models/responses.py` |
| `EpisodeResponse` | Single episode data | `lib/models/responses.py` |
| `VideoListResponse` | Video sources list | `lib/models/responses.py` |

### TMDB Models

| Model | Purpose | Location |
|-------|---------|----------|
| `TMDBTVDetail` | TV show details | `lib/models/tmdb.py` |
| `TMDBMovieDetail` | Movie details | `lib/models/tmdb.py` |
| `TMDBSeasonDetail` | Season details | `lib/models/tmdb.py` |
| `TMDBEpisodeDetail` | Episode details | `lib/models/tmdb.py` |
| `TMDBSearchResult` | Search result | `lib/models/tmdb.py` |

## Services Reference

| Service | Purpose |
|---------|---------|
| `TMDBService` | TMDB API client with caching |
| `TMDBEnrichmentService` | Enriches provider data with TMDB metadata |
| `MatchingService` | Fuzzy title matching with confidence scoring |
| `SeriesConverterService` | Converts flat episodes to hierarchical structure |

## Providers Reference

| Provider | Source | Content Type |
|----------|--------|--------------|
| `AniWorldProvider` | aniworld.to | Anime |
| `SerienStreamProvider` | serienstream.to | TV Series |

## Video Extractors

| Extractor | Hosts | Notes |
|-----------|-------|-------|
| `voe_extractor` | VOE | HLS streams |
| `vidmoly_extractor` | Vidmoly | HLS streams |
| `vidoza_extractor` | Vidoza | Direct links |
| `filemoon_extractor` | Filemoon | HLS streams |
| `dood_extractor` | Doodstream | Dynamic tokens |
| `luluvdo_extractor` | Luluvdo | HLS streams |
| `speedfiles_extractor` | SpeedFiles | Direct links |
| `ytdlp_extractor` | YouTube | Trailers |
