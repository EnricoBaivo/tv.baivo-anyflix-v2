# Provider API Tests

This directory contains comprehensive integration tests for the AniWorld and SerienStream providers.

## Test Structure

### `test_api_endpoints.py`
Tests all API endpoints through the FastAPI application:
- **TestSourcesEndpoints**: Tests for `/sources/` endpoints
- **TestPopularEndpoints**: Tests for popular content
- **TestLatestEndpoints**: Tests for latest updates
- **TestSearchEndpoints**: Tests for search functionality
- **TestSeriesEndpoints**: Tests for series detail endpoints
- **TestSeasonEndpoints**: Tests for season-specific endpoints
- **TestEpisodeEndpoints**: Tests for episode-specific endpoints
- **TestMoviesEndpoints**: Tests for movies/OVAs
- **TestVideoEndpoints**: Tests for video extraction
- **TestTMDBEnrichment**: Tests for TMDB data enrichment
- **TestErrorHandling**: Tests for error scenarios
- **TestResponseTypes**: Tests for response type consistency

### `test_providers.py`
Tests provider classes directly without going through the API:
- **TestAniWorldProvider**: Direct tests for AniWorld provider
- **TestSerienStreamProvider**: Direct tests for SerienStream provider
- **TestProviderContextManager**: Tests for context manager functionality
- **TestSearchResultStructure**: Tests for search result data structures
- **TestEpisodeParsing**: Tests for episode parsing logic
- **TestLanguageHandling**: Tests for language filtering

## Running the Tests

### Run All Tests
```bash
cd anyflix-backend
pytest tests/providers/
```

### Run Specific Test File
```bash
pytest tests/providers/test_api_endpoints.py
pytest tests/providers/test_providers.py
```

### Run Specific Test Class
```bash
pytest tests/providers/test_api_endpoints.py::TestSourcesEndpoints
pytest tests/providers/test_providers.py::TestAniWorldProvider
```

### Run Specific Test Method
```bash
pytest tests/providers/test_api_endpoints.py::TestSourcesEndpoints::test_list_sources
```

### Run Tests by Marker

**Integration tests only:**
```bash
pytest -m integration tests/providers/
```

**Slow tests only:**
```bash
pytest -m slow tests/providers/
```

**Exclude slow tests:**
```bash
pytest -m "not slow" tests/providers/
```

### Run with Coverage
```bash
pytest tests/providers/ --cov=app --cov=lib --cov-report=html
```

### Run with Verbose Output
```bash
pytest tests/providers/ -v
```

### Run with Output from Print Statements
```bash
pytest tests/providers/ -s
```

## Test Markers

Tests are marked with the following pytest markers:

- `@pytest.mark.integration` - Integration tests that make real HTTP requests
- `@pytest.mark.slow` - Tests that take longer to execute (series/episode detail fetching)
- `@pytest.mark.asyncio` - Async tests (required for async test functions)

## Test Data

Tests use real URLs from aniworld.to and serienstream.to:

### AniWorld Test Data
- Series: One Punch Man (`/anime/stream/one-punch-man`)
- Season 1, Episode 1
- Search query: "one punch"

### SerienStream Test Data
- Series: The Witcher (`/serie/stream/the-witcher`)
- Season 1, Episode 1
- Search query: "witcher"

## Expected Test Behavior

### Passing Tests
All tests should pass if:
1. The backend server dependencies are installed
2. The websites (aniworld.to, serienstream.to) are accessible
3. TMDB API key is configured (for TMDB enrichment tests)
4. Redis is running (if caching is enabled)

### Potential Failures
Tests may fail if:
- Network connectivity issues
- Website structure changes (HTML parsing may break)
- TMDB API rate limits or unavailability
- Test data URLs become unavailable

## Configuration

Tests use fixtures from `tests/conftest.py`:
- `client` - Synchronous FastAPI test client
- `async_client` - Async FastAPI test client
- `aniworld_test_data` - AniWorld test URLs and data
- `serienstream_test_data` - SerienStream test URLs and data
- `provider_test_data` - Parametrized fixture for both providers

## Environment Variables

Make sure the following environment variables are set:
```bash
TMDB_API_KEY=your_tmdb_api_key
ENABLE_CACHING=true  # optional
REDIS_HOST=localhost  # if caching enabled
REDIS_PORT=6379  # if caching enabled
```

## CI/CD Considerations

For continuous integration:
1. **Cache popular/latest endpoints**: These are cached, so tests should be fast
2. **Rate limiting**: Consider adding delays between tests if rate limits are hit
3. **Test isolation**: Each test should be independent and not rely on previous test state
4. **Timeouts**: Slow tests have longer timeouts for series detail fetching

## Adding New Tests

When adding new tests:
1. Use appropriate markers (`@pytest.mark.integration`, `@pytest.mark.slow`)
2. Follow the existing test class structure
3. Use fixtures from conftest.py for test data
4. Add docstrings explaining what the test validates
5. Use descriptive assertion messages

## Example Test Run Output

```
$ pytest tests/providers/ -v

tests/providers/test_api_endpoints.py::TestSourcesEndpoints::test_list_sources PASSED
tests/providers/test_api_endpoints.py::TestSourcesEndpoints::test_get_source_preferences[aniworld] PASSED
tests/providers/test_api_endpoints.py::TestSourcesEndpoints::test_get_source_preferences[serienstream] PASSED
tests/providers/test_api_endpoints.py::TestPopularEndpoints::test_get_popular_content[aniworld-anime] PASSED
...

====== 87 passed in 45.23s ======
```

## Troubleshooting

### Tests timing out
- Increase pytest timeout: `pytest --timeout=300`
- Check network connectivity to aniworld.to and serienstream.to

### TMDB tests failing
- Verify TMDB_API_KEY is set correctly
- Check TMDB API rate limits

### Redis connection errors
- Ensure Redis is running: `redis-cli ping`
- Or disable caching: `ENABLE_CACHING=false`

### Import errors
- Install dependencies: `pip install -r requirements.txt`
- Ensure you're in the correct directory
