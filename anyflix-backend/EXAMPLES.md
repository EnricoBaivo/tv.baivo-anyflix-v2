# API Response Examples

## Table of Contents
1. [Paginated Endpoints](#paginated-endpoints)
2. [Error Responses](#error-responses)
3. [Series Endpoints](#series-endpoints)
4. [Video Endpoints](#video-endpoints)

---

## Paginated Endpoints

### 1. Popular Content

**Request:**
```bash
GET /sources/aniworld/popular?page=1
```

**Response (200 OK):**
```json
{
  "content_type": "anime",
  "items": [
    {
      "name": "Attack on Titan",
      "image_url": "https://aniworld.to/cover/attack-on-titan.jpg",
      "link": "/anime/stream/attack-on-titan",
      "provider": "AniWorld",
      "available_languages": ["de", "de_sub", "en_sub"],
      "media_info": {
        "name": "Attack on Titan",
        "cover_image_url": "https://aniworld.to/cover/attack-on-titan.jpg",
        "description": "Several hundred years ago, humans were...",
        "genres": ["Action", "Drama", "Fantasy"],
        "start_year": 2013,
        "end_year": 2023,
        "rating_value": 4.8,
        "rating_count": 15420
      }
    },
    {
      "name": "Demon Slayer",
      "image_url": "https://aniworld.to/cover/demon-slayer.jpg",
      "link": "/anime/stream/demon-slayer",
      "provider": "AniWorld",
      "available_languages": ["de", "de_sub"]
    }
    // ... 13 more items (15 per page)
  ],
  "pagination": {
    "page": 1,
    "per_page": 15,
    "total_items": 100,
    "total_pages": 7,
    "has_next": true,
    "has_previous": false
  }
}
```

**Headers:**
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

---

### 2. Latest Updates

**Request:**
```bash
GET /sources/serienstream/latest?page=2
```

**Response (200 OK):**
```json
{
  "content_type": "series_movie",
  "items": [
    {
      "name": "Breaking Bad",
      "image_url": "https://serienstream.to/cover/breaking-bad.jpg",
      "link": "/serie/stream/breaking-bad",
      "provider": "SerienStream",
      "available_languages": ["de", "en"]
    }
    // ... more items
  ],
  "pagination": {
    "page": 2,
    "per_page": 15,
    "total_items": 45,
    "total_pages": 3,
    "has_next": true,
    "has_previous": true
  }
}
```

---

### 3. Search Results

**Request:**
```bash
GET /sources/aniworld/search?q=attack&page=1
```

**Response (200 OK):**
```json
{
  "content_type": "anime",
  "items": [
    {
      "name": "Attack on Titan",
      "image_url": "https://aniworld.to/cover/attack-on-titan.jpg",
      "link": "/anime/stream/attack-on-titan",
      "provider": "AniWorld",
      "available_languages": ["de", "de_sub", "en_sub"]
    },
    {
      "name": "No Game No Life",
      "image_url": "https://aniworld.to/cover/no-game-no-life.jpg",
      "link": "/anime/stream/no-game-no-life",
      "provider": "AniWorld",
      "available_languages": ["de", "de_sub"]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 15,
    "total_items": 2,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

---

## Error Responses

### 1. Resource Not Found (404)

**Request:**
```bash
GET /sources/invalid_source/popular
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "HTTP_404",
    "message": "Source 'invalid_source' not found",
    "details": {
      "status_code": 404
    }
  },
  "metadata": {
    "timestamp": "2025-12-19T10:30:00.123456",
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "version": "1.0.0"
  }
}
```

**Headers:**
```
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json
```

---

### 2. Validation Error (422)

**Request:**
```bash
GET /sources/aniworld/search?q=
```

**Response (422 Unprocessable Entity):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {
      "errors": [
        {
          "type": "string_too_short",
          "loc": ["query", "q"],
          "msg": "String should have at least 1 character",
          "input": "",
          "ctx": {
            "min_length": 1
          }
        }
      ]
    }
  },
  "metadata": {
    "timestamp": "2025-12-19T10:30:05.789012",
    "request_id": "660e8400-e29b-41d4-a716-446655440001",
    "version": "1.0.0"
  }
}
```

---

### 3. Internal Server Error (500)

**Request:**
```bash
GET /sources/aniworld/series?url=/broken/endpoint
```

**Response (500 Internal Server Error):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "An unexpected error occurred",
    "details": null
  },
  "metadata": {
    "timestamp": "2025-12-19T10:30:10.456789",
    "request_id": "770e8400-e29b-41d4-a716-446655440002",
    "version": "1.0.0"
  }
}
```

**Note:** In debug mode, `details` may include additional error information.

---

## Series Endpoints

### 1. Series Overview

**Request:**
```bash
GET /sources/aniworld/series?url=/anime/stream/attack-on-titan
```

**Response (200 OK):**
```json
{
  "content_type": "anime",
  "series": {
    "slug": "attack-on-titan",
    "seasons": [
      {
        "season": 1,
        "title": "Season 1",
        "episodes": []
      },
      {
        "season": 2,
        "title": "Season 2",
        "episodes": []
      }
    ],
    "movies": []
  },
  "tmdb_series_data": {
    "id": 1429,
    "name": "Attack on Titan",
    "overview": "Several hundred years ago...",
    "poster_path": "/hTP1DtLGFamjfu8WqjnuQdP1n4i.jpg",
    "vote_average": 8.7,
    "vote_count": 5234,
    "first_air_date": "2013-04-07",
    "genres": [
      {"id": 16, "name": "Animation"},
      {"id": 10759, "name": "Action & Adventure"}
    ]
  },
  "match_confidence": 0.95,
  "season_count": 4
}
```

---

### 2. All Seasons

**Request:**
```bash
GET /sources/aniworld/series/seasons?url=/anime/stream/attack-on-titan
```

**Response (200 OK):**
```json
{
  "content_type": "anime",
  "seasons": [
    {
      "season": 1,
      "title": "Season 1",
      "episodes": [
        {
          "season": 1,
          "episode": 1,
          "title": "To You, in 2000 Years",
          "name": "Staffel 1 Folge 1 : To You, in 2000 Years",
          "url": "/anime/stream/attack-on-titan/staffel-1/episode-1",
          "tags": [],
          "tmdb_episode_data": {
            "id": 63056,
            "name": "To You, in 2000 Years",
            "overview": "After 100 years of peace...",
            "vote_average": 8.2,
            "vote_count": 189,
            "air_date": "2013-04-07",
            "episode_number": 1,
            "season_number": 1,
            "still_path": "/path/to/still.jpg",
            "runtime": 24
          }
        }
        // ... more episodes
      ]
    }
    // ... more seasons
  ],
  "tmdb_series_data": {
    "id": 1429,
    "name": "Attack on Titan",
    "overview": "Several hundred years ago...",
    "poster_path": "/hTP1DtLGFamjfu8WqjnuQdP1n4i.jpg",
    "vote_average": 8.7,
    "vote_count": 5234,
    "first_air_date": "2013-04-07",
    "genres": [
      {"id": 16, "name": "Animation"},
      {"id": 10759, "name": "Action & Adventure"}
    ]
  },
  "match_confidence": 0.95
}
```

---

### 3. Specific Season

**Request:**
```bash
GET /sources/aniworld/series/seasons/1?url=/anime/stream/attack-on-titan
```

**Response (200 OK):**
```json
{
  "content_type": "anime",
  "season": {
    "season": 1,
    "title": "Season 1",
    "episodes": [
      {
        "season": 1,
        "episode": 1,
        "title": "To You, in 2000 Years",
        "name": "Staffel 1 Folge 1 : To You, in 2000 Years",
        "url": "/anime/stream/attack-on-titan/staffel-1/episode-1",
        "tags": [],
        "tmdb_episode_data": {
          "id": 63056,
          "name": "To You, in 2000 Years",
          "overview": "After 100 years of peace...",
          "vote_average": 8.2,
          "vote_count": 234,
          "air_date": "2013-04-07",
          "episode_number": 1,
          "season_number": 1,
          "still_path": "/path/to/still.jpg",
          "runtime": 24
        }
      }
      // ... more episodes
    ],
    "tmdb_season_data": {
      "id": 3850,
      "name": "Season 1",
      "overview": "The first season...",
      "poster_path": "/path/to/poster.jpg",
      "season_number": 1,
      "air_date": "2013-04-07",
      "episode_count": 25
    }
  },
  "tmdb_series_data": {
    "id": 1429,
    "name": "Attack on Titan",
    "overview": "Several hundred years ago...",
    "poster_path": "/hTP1DtLGFamjfu8WqjnuQdP1n4i.jpg",
    "vote_average": 8.7,
    "vote_count": 5234,
    "first_air_date": "2013-04-07",
    "genres": [
      {"id": 16, "name": "Animation"},
      {"id": 10759, "name": "Action & Adventure"}
    ]
  },
  "match_confidence": 0.95
}
```

---

### 4. Specific Episode

**Request:**
```bash
GET /sources/aniworld/series/seasons/1/episodes/1?url=/anime/stream/attack-on-titan
```

**Response (200 OK):**
```json
{
  "content_type": "anime",
  "episode": {
    "season": 1,
    "episode": 1,
    "title": "To You, in 2000 Years",
    "name": "Staffel 1 Folge 1 : To You, in 2000 Years",
    "url": "/anime/stream/attack-on-titan/staffel-1/episode-1",
    "tags": [],
    "tmdb_episode_data": {
      "id": 63056,
      "name": "To You, in 2000 Years",
      "overview": "After 100 years of peace...",
      "vote_average": 8.2,
      "vote_count": 234,
      "air_date": "2013-04-07",
      "episode_number": 1,
      "season_number": 1,
      "still_path": "/path/to/still.jpg",
      "runtime": 24
    }
  },
  "tmdb_series_data": {
    "id": 1429,
    "name": "Attack on Titan",
    "overview": "Several hundred years ago...",
    "poster_path": "/hTP1DtLGFamjfu8WqjnuQdP1n4i.jpg",
    "vote_average": 8.7,
    "vote_count": 5234,
    "first_air_date": "2013-04-07",
    "genres": [
      {"id": 16, "name": "Animation"},
      {"id": 10759, "name": "Action & Adventure"}
    ]
  }
}
```

---

## Video Endpoints

### 1. Video Sources

**Request:**
```bash
GET /sources/aniworld/videos?url=/anime/stream/attack-on-titan/staffel-1/episode-1
```

**Response (200 OK):**
```json
{
  "content_type": "anime",
  "videos": [
    {
      "url": "https://streamable-url.com/video.m3u8",
      "original_url": "https://host.com/embed/xyz123",
      "quality": "Deutsch Dub 1080p Vidmoly",
      "language": "de",
      "format": "m3u8",
      "type": "Dub",
      "host": "Vidmoly",
      "requires_proxy": false
    },
    {
      "url": "https://streamable-url.com/video2.m3u8",
      "original_url": "https://host.com/embed/abc456",
      "quality": "Deutsch Sub 1080p VOE",
      "language": "de_sub",
      "format": "m3u8",
      "type": "Sub",
      "host": "VOE",
      "requires_proxy": false
    }
  ]
}
```

---

### 2. Trailer Extraction

**Request:**
```bash
GET /sources/trailer?youtube_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Response (200 OK):**
```json
{
  "success": true,
  "original_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "streamable_url": "https://rr3---sn-qxo7rn7e.googlevideo.com/videoplayback?...",
  "m3u8_url": "https://manifest.googlevideo.com/api/manifest/hls_variant/...",
  "quality": "1080p",
  "error": null
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "original_url": "https://invalid-url.com",
  "streamable_url": null,
  "m3u8_url": null,
  "quality": null,
  "error": "Invalid YouTube URL"
}
```

---

## Other Endpoints

### 1. List Sources

**Request:**
```bash
GET /sources/
```

**Response (200 OK):**
```json
{
  "sources": [
    "aniworld",
    "serienstream"
  ]
}
```

---

### 2. Source Preferences

**Request:**
```bash
GET /sources/aniworld/preferences
```

**Response (200 OK):**
```json
{
  "preferences": {
    "lang": {
      "key": "lang",
      "list_preference": {
        "title": "Bevorzugte Sprache",
        "summary": "Wenn verfügbar, wird diese Sprache ausgewählt",
        "valueIndex": 0,
        "entries": ["Deutsch", "Englisch"],
        "entryValues": ["Deutsch", "Englisch"]
      }
    },
    "type": {
      "key": "type",
      "list_preference": {
        "title": "Bevorzugter Typ",
        "summary": "Wenn verfügbar, wird dieser Typ ausgewählt",
        "valueIndex": 0,
        "entries": ["Dub", "Sub"],
        "entryValues": ["Dub", "Sub"]
      }
    }
  }
}
```

---

## Notes

1. All timestamps are in UTC ISO 8601 format
2. All responses include `X-Request-ID` header for tracking
3. Pagination uses 1-based indexing (first page is page=1)
4. TMDB enrichment may be null if TMDB API key is not configured
5. Video URLs may expire after a certain time period
6. Language codes: `de` (German dub), `en` (English dub), `de_sub` (German sub), `en_sub` (English sub)
