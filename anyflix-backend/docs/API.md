# API Reference

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## Content Discovery

### List Available Sources

```http
GET /sources/
```

**Response:**
```json
{
  "sources": ["aniworld", "serienstream"]
}
```

### Get Popular Content

```http
GET /sources/{source}/popular?page=1
```

**Parameters:**
- `source` (path): Source name (`aniworld` or `serienstream`)
- `page` (query): Page number (default: 1)

**Response:**
```json
{
  "type": "anime",
  "list": [
    {
      "name": "Solo Leveling",
      "image_url": "https://aniworld.to/public/img/cover/...",
      "link": "/anime/stream/solo-leveling",
      "provider": "AniWorld",
      "available_languages": ["de", "en", "de_sub"],
      "media_info": {
        "name": "Solo Leveling",
        "description": "...",
        "genres": ["Action", "Fantasy"],
        "start_year": 2024,
        "imdb_id": "tt21209876"
      }
    }
  ],
  "has_next_page": true
}
```

### Get Latest Updates

```http
GET /sources/{source}/latest?page=1
```

Same response format as popular content.

### Search Content

```http
GET /sources/{source}/search?q=attack&page=1&lang=de
```

**Parameters:**
- `source` (path): Source name
- `q` (query): Search query (required)
- `page` (query): Page number (default: 1)
- `lang` (query): Language filter (optional)

---

## Series Operations

### Get Series Overview

```http
GET /sources/{source}/series?url=/anime/stream/solo-leveling
```

**Parameters:**
- `source` (path): Source name
- `url` (query): Series URL path (required)

**Response:**
```json
{
  "type": "anime",
  "tmdb_data": {
    "id": 217134,
    "name": "Solo Leveling",
    "overview": "...",
    "poster_path": "/geCRueV3ElhRTr0xtJuEWJt6dJ1.jpg",
    "vote_average": 8.6
  },
  "match_confidence": 0.95,
  "length": 2,
  "series": {
    "slug": "solo-leveling",
    "seasons": [],
    "movies": []
  }
}
```

### Get All Seasons

```http
GET /sources/{source}/series/seasons?url=/anime/stream/solo-leveling
```

**Response:**
```json
{
  "type": "anime",
  "seasons": [
    {
      "season": 1,
      "title": "Staffel 1",
      "episodes": [
        {
          "season": 1,
          "episode": 1,
          "title": "I'm Used to It",
          "url": "/anime/stream/solo-leveling/staffel-1/episode-1"
        }
      ]
    }
  ],
  "tmdb_data": { ... },
  "match_confidence": 0.95
}
```

### Get Specific Season

```http
GET /sources/{source}/series/seasons/{season_num}?url=/anime/stream/solo-leveling
```

Includes TMDB season-specific data with episode enrichment:
- `tmdb_overview`: Episode description
- `tmdb_still_path`: Episode thumbnail
- `tmdb_vote_average`: Episode rating
- `tmdb_air_date`: Air date

### Get Specific Episode

```http
GET /sources/{source}/series/seasons/{season_num}/episodes/{episode_num}?url=/anime/stream/solo-leveling
```

Includes TMDB episode-specific data.

### Get Movies/OVAs

```http
GET /sources/{source}/series/movies?url=/anime/stream/series-name
```

**Response:**
```json
{
  "type": "anime",
  "movies": [
    {
      "number": 1,
      "title": "Movie Title",
      "kind": "movie",
      "url": "/anime/stream/series/filme/film-1"
    }
  ],
  "tmdb_data": { ... }
}
```

---

## Video Sources

### Get Video Streaming Links

```http
GET /sources/{source}/videos?url=/anime/stream/solo-leveling/staffel-1/episode-1&lang=de
```

**Parameters:**
- `source` (path): Source name
- `url` (query): Episode URL path (required)
- `lang` (query): Language filter (`de`, `en`, `sub`, `all`)

**Response:**
```json
{
  "type": "anime",
  "videos": [
    {
      "url": "https://streamable-url...",
      "original_url": "https://voe.sx/...",
      "quality": "Deutsch Dub 1080p VOE",
      "language": "de",
      "type": "Dub",
      "host": "voe",
      "format": "m3u8",
      "requires_proxy": false,
      "headers": {
        "Referer": "https://aniworld.to"
      }
    }
  ]
}
```

### Extract Trailer URL

```http
GET /sources/trailer?youtube_url=https://www.youtube.com/watch?v=VIDEO_ID
```

**Response:**
```json
{
  "success": true,
  "original_url": "https://www.youtube.com/watch?v=...",
  "streamable_url": "https://...",
  "m3u8_url": "https://...",
  "quality": "1080p"
}
```

---

## Source Configuration

### Get Source Preferences

```http
GET /sources/{source}/preferences
```

**Response:**
```json
{
  "preferences": {
    "lang": {
      "key": "lang",
      "list_preference": {
        "title": "Bevorzugte Sprache",
        "entries": ["Deutsch", "Englisch"],
        "entryValues": ["Deutsch", "Englisch"]
      }
    },
    "host": {
      "key": "host",
      "list_preference": {
        "title": "Bevorzugter Hoster",
        "entries": ["Doodstream", "Filemoon", "VOE", ...]
      }
    }
  }
}
```

---

## Admin Endpoints

### Get Sources Status

```http
GET /admin/sources/status
```

### Get Cache Statistics

```http
GET /admin/cache/stats
```

**Response:**
```json
{
  "cache_enabled": true,
  "status": "active",
  "stats": {
    "cache_type": "redis",
    "used_memory_human": "1.5M",
    "total_keys": 150,
    "hit_ratio": 85.5,
    "namespaces": {
      "endpoints": 100,
      "services": 50
    }
  }
}
```

### Clear Cache by Prefix

```http
POST /admin/cache/clear/{prefix}
```

**Example:**
```http
POST /admin/cache/clear/endpoints:aniworld:popular
```

### Clear Cache by Endpoint

```http
POST /admin/cache/clear/endpoint/aniworld/popular
```

### Flush All Cache

```http
POST /admin/cache/flush
```

---

## Error Responses

### 404 Not Found

```json
{
  "detail": "Source 'invalid' not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to fetch series data from aniworld"
}
```

---

## Language Codes

| Code | Description |
|------|-------------|
| `de` | German dub |
| `en` | English dub |
| `de_sub` | German subtitles (Japanese audio) |
| `en_sub` | English subtitles (Japanese audio) |
| `all` | All available languages |
