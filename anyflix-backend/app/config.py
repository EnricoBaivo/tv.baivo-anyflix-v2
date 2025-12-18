"""Configuration management for media backend service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # API settings
    api_title: str = "Anime Backend Service"
    api_description: str = "Python backend service for anime streaming sources"
    api_version: str = "0.1.0"

    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_methods: list[str] = ["*"]
    cors_headers: list[str] = ["*"]

    # HTTP client settings
    request_timeout: int = 30
    max_connections: int = 100

    # Logging settings
    log_level: str = "INFO"
    log_file: str = "logs/anime_backend.log"
    enable_console_logging: bool = True
    enable_file_logging: bool = True
    log_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 5
    debug_extractors: bool = False  # Enable detailed extractor debugging
    debug_providers: bool = False  # Enable detailed provider debugging

    # External API keys
    tmdb_api_key: str = ""  # TMDB API key for metadata enrichment

    # Feature flags
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes

    # Cache settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    cache_default_ttl: int = 3600  # 1 hour

    # Service-specific cache TTLs
    tmdb_search_ttl: int = 1800  # 30 minutes
    tmdb_details_ttl: int = 7200  # 2 hours
    tmdb_config_ttl: int = 86400  # 24 hours
    provider_popular_ttl: int = 900  # 15 minutes
    provider_latest_ttl: int = 600  # 10 minutes
    provider_search_ttl: int = 1800  # 30 minutes
    provider_detail_ttl: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
