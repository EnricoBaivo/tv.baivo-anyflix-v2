# AniList Service Examples

This directory contains practical examples showing how to use the AniList service in your anime backend application.

## Files

### 🧪 `test_anilist_simple.py`
**Quick verification test** - Run this first to check if the AniList service is working.

```bash
python examples/test_anilist_simple.py
```

**What it does:**
- Tests basic AniList API connectivity
- Searches for "One Piece" as a known anime
- Shows data conversion to dictionary format
- Handles rate limiting gracefully

### 📚 `anilist_service_example.py`
**Comprehensive usage examples** - Shows all the different ways to use the AniList service.

```bash
python examples/anilist_service_example.py
```

**Examples included:**
- Single anime search
- Multiple searches with rate limiting
- Get anime by AniList ID
- Advanced search with filters
- Error handling patterns
- Data conversion for API responses

### 🔗 `api_integration_example.py`
**API integration patterns** - Shows how the service integrates with your FastAPI endpoints.

```bash
python examples/api_integration_example.py
```

**Demonstrates:**
- Metadata enrichment (like in your `sources.py`)
- Series detail endpoint simulation
- Rate limiting behavior in API context
- Data structure exploration
- Error handling in production scenarios

## Usage

All examples should be run from the **project root directory**:

```bash
# From /path/to/anyflix-backend/
python examples/test_anilist_simple.py
python examples/anilist_service_example.py
python examples/api_integration_example.py
```

## Rate Limiting

The AniList API currently has strict rate limits:
- **30 requests per minute** (degraded state)
- **429 errors are expected** when limits are exceeded
- Examples handle this gracefully

### If you see rate limit errors:
1. **This is normal behavior** - not a bug
2. Wait 1-2 minutes before running examples again
3. Your API handles this by returning `null` for metadata
4. Core functionality continues to work

## Key Concepts

### 1. Always use async context managers
```python
async with anilist_service:
    result = await anilist_service.search_anime("One Piece")
```

### 2. Convert Media objects to dictionaries
```python
# For API responses (like in sources.py)
first_result = anilist_data.media[0]
anime_dict = (
    first_result.model_dump() 
    if hasattr(first_result, "model_dump") 
    else first_result.dict()
)
```

### 3. Handle rate limiting gracefully
```python
try:
    result = await anilist_service.search_anime(title)
except Exception as e:
    if "429" in str(e):
        logger.warning("Rate limited - returning null metadata")
        return None
```

## Integration with Your API

These examples mirror the patterns used in your actual API:

- **`app/routers/sources.py`** lines 60-77: Metadata enrichment
- **`app/routers/sources.py`** lines 285-295: Series detail enrichment
- **Rate limiting**: Handled with try/catch and null fallbacks

## Troubleshooting

### ImportError: No module named 'lib'
Make sure you're running from the project root:
```bash
cd /path/to/anyflix-backend/
python examples/test_anilist_simple.py
```

### 429 Too Many Requests
This is expected! The examples show how to handle this:
- Wait 1-2 minutes
- Rate limits reset automatically
- Your API gracefully handles this

### Connection errors
Check your internet connection and try the simple test first:
```bash
python examples/test_anilist_simple.py
```

## Next Steps

1. **Start with the simple test** to verify everything works
2. **Explore the comprehensive examples** to understand all features
3. **Check the API integration** to see real-world usage patterns
4. **Refer back to these examples** when implementing new features

The examples are designed to be educational and practical - use them as reference when working with the AniList service in your application!
