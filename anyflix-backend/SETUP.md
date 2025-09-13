# AnyFlix Backend - Quick Setup Guide

## 🚀 Quick Start

The application works out of the box without any API keys! Just run:

```bash
uv run fasatapi dev app.main:app
```

## 🔧 Optional Configuration

### TMDB API Key (For Series Metadata)

If you want rich metadata for series from SerienStream, get a free API key:

1. Visit: https://www.themoviedb.org/settings/api
2. Create an account and get your API key
3. Set the environment variable:

```bash
export TMDB_API_KEY=your_api_key_here
```

### Rate Limiting Notes

- **AniList**: Free GraphQL API with rate limits (handled gracefully)
- **TMDB**: Free REST API, requires key for metadata enrichment
- **Without API keys**: Core streaming functionality works perfectly

## 🎯 MVP Features

✅ **Direct Provider Access** - No over-engineered service layers  
✅ **Graceful Degradation** - Works without API keys  
✅ **Type-based Responses** - `"anime"` vs `"normal"` content  
✅ **Conditional Metadata** - AniList for anime, TMDB for series  
✅ **All Required Endpoints** - Popular, latest, search, videos, series structure  

## 📊 API Response Format

```json
{
  "type": "anime",
  "list": [
    {
      "name": "Gachiakuta",
      "image_url": "https://...",
      "link": "/anime/stream/gachiakuta",
      "tmdb_data": null,
      "anilist_data": { "id": 178025, "title": {...}, ... },
      "match_confidence": 1.0
    }
  ]
}
```

Perfect for MVP requirements! 🎉
