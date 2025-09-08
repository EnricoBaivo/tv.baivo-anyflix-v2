# 📋 Logging Guide for Anime Backend

## 🚀 Quick Start

The anime backend now has comprehensive logging configured! Here's how to use it effectively for debugging.

## 📁 Configuration

### Environment Variables (.env)

```bash
# Basic logging settings
LOG_LEVEL=DEBUG          # DEBUG, INFO, WARNING, ERROR, CRITICAL  
LOG_FILE=logs/anime_backend.log
ENABLE_CONSOLE_LOGGING=true
ENABLE_FILE_LOGGING=true

# Advanced settings
LOG_MAX_BYTES=10485760   # 10MB per log file
LOG_BACKUP_COUNT=5       # Keep 5 backup files
DEBUG_EXTRACTORS=true    # Detailed extractor debugging
DEBUG_PROVIDERS=true     # Detailed provider debugging
```

## 🔍 Using Logging in Code

### Basic Logger Usage

```python
from lib.utils.logging_config import get_logger

class MyClass:
    def __init__(self):
        self.logger = get_logger(__name__)
        
    def my_method(self):
        self.logger.info("This is an info message")
        self.logger.debug("This is a debug message")
        self.logger.warning("This is a warning")
        self.logger.error("This is an error")
        
        # Exception logging with traceback
        try:
            # some code
            pass
        except Exception as e:
            self.logger.exception("An error occurred")
```

### Performance Monitoring

```python
from lib.utils.logging_config import timed_operation

# Using context manager for timing
async def get_video_sources(self, url: str):
    with timed_operation(f"get_video_sources({url})", self.logger):
        # Your code here
        result = await some_operation()
        return result
```

### Advanced Logging Context

```python
from lib.utils.logging_config import LoggingContext

with LoggingContext("database_operation", self.logger):
    # Complex operation
    result = perform_database_query()
```

## 🎯 Log Levels Guide

| Level    | When to Use | Example |
|----------|-------------|---------|
| `DEBUG`  | Detailed diagnostic info | Variable values, function calls |
| `INFO`   | Normal operation info | Request started, operation completed |
| `WARNING`| Something unexpected but not critical | Fallback used, deprecated method |
| `ERROR`  | Error occurred but app continues | Failed to connect to service |
| `CRITICAL`| Serious error, app might stop | Database unavailable |

## 📊 Log Output Format

### Console Output (Colored)
```
02:17:11 | INFO | lib.services.anime_service:46 | ⚙️ Service operation completed
```

### File Output (Detailed)
```
2025-09-07 02:17:11 | INFO | lib.services.anime_service:46 | get_popular | Retrieved 20 anime from aniworld (page 1)
```

## 🔧 Debugging Tips

### 1. Enable Debug Mode
```bash
# In .env file
LOG_LEVEL=DEBUG
DEBUG_EXTRACTORS=true
DEBUG_PROVIDERS=true
```

### 2. Component-Specific Debugging
```python
# Focus on specific components
import logging

# Reduce noise from third-party libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Increase verbosity for your components
logging.getLogger("lib.extractors").setLevel(logging.DEBUG)
logging.getLogger("lib.providers").setLevel(logging.DEBUG)
```

### 3. Structured Logging
```python
self.logger.info("Processing request", extra={
    "source": "aniworld",
    "page": 1,
    "operation": "get_popular",
    "user_id": user_id
})
```

## 📁 Log Files

- **Primary log**: `logs/anime_backend.log`
- **Rotated logs**: `logs/anime_backend.log.1`, `logs/anime_backend.log.2`, etc.
- **Test logs**: `logs/debug_test.log` (from debug script)

## 🧪 Testing Logging

Run the debug utility to test logging:

```bash
uv run python debug_logging.py
```

This will:
- Test all log levels
- Test component-specific loggers  
- Test performance logging
- Create sample log files
- Verify configuration

## 🚨 Common Patterns

### Provider Debugging
```python
class MyProvider(BaseProvider):
    def __init__(self):
        super().__init__(source)
        self.logger = get_logger(__name__)
        
    async def get_popular(self, page: int):
        with timed_operation(f"get_popular(page={page})", self.logger):
            self.logger.debug(f"Fetching popular anime, page {page}")
            # ... operation
            self.logger.info(f"Retrieved {len(results)} popular anime")
            return results
```

### Extractor Debugging
```python
async def extract_video_sources(self, url: str):
    self.logger.debug(f"Starting extraction for: {url}")
    
    try:
        sources = await self._extract_sources(url)
        self.logger.info(f"Extracted {len(sources)} video sources")
        return sources
    except Exception as e:
        self.logger.error(f"Extraction failed for {url}: {e}")
        self.logger.exception("Full traceback:")
        raise
```

### Error Handling
```python
try:
    result = await risky_operation()
except SpecificError as e:
    self.logger.warning(f"Expected error occurred: {e}")
    # Handle gracefully
except Exception as e:
    self.logger.error(f"Unexpected error: {e}")
    self.logger.exception("Full traceback for debugging:")
    raise
```

## 🎛️ Environment Examples

### Development
```bash
LOG_LEVEL=DEBUG
DEBUG_EXTRACTORS=true
DEBUG_PROVIDERS=true
ENABLE_CONSOLE_LOGGING=true
```

### Production
```bash
LOG_LEVEL=INFO
DEBUG_EXTRACTORS=false  
DEBUG_PROVIDERS=false
ENABLE_CONSOLE_LOGGING=false
ENABLE_FILE_LOGGING=true
```

### Troubleshooting
```bash
LOG_LEVEL=DEBUG
DEBUG_EXTRACTORS=true
DEBUG_PROVIDERS=true
ENABLE_CONSOLE_LOGGING=true
ENABLE_FILE_LOGGING=true
```

## 🔍 Monitoring & Analysis

### Useful Commands
```bash
# Watch live logs
tail -f logs/anime_backend.log

# Filter by component
grep "lib.extractors" logs/anime_backend.log

# Filter by level
grep "ERROR\|CRITICAL" logs/anime_backend.log

# Search for specific operations
grep "get_video_list" logs/anime_backend.log
```

---

**Happy debugging! 🐛✨**
