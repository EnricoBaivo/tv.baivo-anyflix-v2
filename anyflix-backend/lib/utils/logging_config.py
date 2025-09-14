"""Logging configuration utilities."""

import logging
import logging.handlers
import sys
from pathlib import Path

from app.config import settings


class ColorFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    # Color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset_color = self.COLORS["RESET"]

        # Add color to level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"

        return super().format(record)


def setup_logging(
    level: str | None = None,
    log_file: str | None = None,
    enable_console: bool = True,
    enable_file: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """Set up comprehensive logging configuration.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        enable_console: Enable console logging
        enable_file: Enable file logging
        max_bytes: Maximum bytes per log file before rotation
        backup_count: Number of backup files to keep
    """
    # Use config level if not specified
    if level is None:
        level = settings.log_level

    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Default log file
    if log_file is None:
        log_file = logs_dir / "anime_backend.log"

    # Clear existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Set root logger level
    root_logger.setLevel(numeric_level)

    # Console handler with colors
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(numeric_level)

        console_formatter = ColorFormatter(
            "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler with rotation
    if enable_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(numeric_level)

        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s:%(lineno)d | %(funcName)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Configure third-party loggers
    configure_third_party_loggers(numeric_level)

    logging.info(
        f"Logging configured - Level: {level}, Console: {enable_console}, File: {enable_file}"
    )


def configure_third_party_loggers(level: int) -> None:
    """Configure third-party library loggers to reduce noise."""
    # Reduce httpx/httpcore verbosity unless DEBUG level
    if level > logging.DEBUG:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Always reduce uvicorn access logs unless DEBUG
    if level > logging.DEBUG:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_function_call(func_name: str, *args, **kwargs) -> None:
    """Log function calls for debugging.

    Args:
        func_name: Name of the function being called
        *args: Function arguments
        **kwargs: Function keyword arguments
    """
    logger = get_logger("function_calls")

    # Format arguments for logging
    arg_strs = []
    if args:
        arg_strs.extend([repr(arg) for arg in args])
    if kwargs:
        arg_strs.extend([f"{k}={v!r}" for k, v in kwargs.items()])

    args_str = ", ".join(arg_strs)
    logger.debug("Calling %s(%s)", func_name, args_str)


def log_performance(func_name: str, duration: float, success: bool = True) -> None:
    """Log function performance metrics.

    Args:
        func_name: Name of the function
        duration: Execution duration in seconds
        success: Whether the function completed successfully
    """
    logger = get_logger("performance")

    status = "SUCCESS" if success else "FAILED"
    logger.info("%s - %s - %.3fs", func_name, status, duration)


class LoggingContext:
    """Context manager for enhanced logging during operations."""

    def __init__(self, operation: str, logger: logging.Logger | None = None) -> None:
        """Initialize logging context.

        Args:
            operation: Name of the operation
            logger: Logger to use (defaults to root logger)
        """
        self.operation = operation
        self.logger = logger or logging.getLogger()
        self.start_time = None

    def __enter__(self):
        """Enter the context."""
        import time

        self.start_time = time.time()
        self.logger.info("Starting %s", self.operation)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        import time

        duration = time.time() - self.start_time

        if exc_type is None:
            self.logger.info("Completed %s in %.3fs", self.operation, duration)
        else:
            self.logger.error(
                f"Failed {self.operation} after {duration:.3f}s: {exc_val}"
            )

        return False  # Don't suppress exceptions


# Convenience function for timing operations
def timed_operation(operation: str, logger: logging.Logger | None = None):
    """Decorator or context manager for timing operations.

    Args:
        operation: Name of the operation
        logger: Logger to use

    Returns:
        LoggingContext instance
    """
    return LoggingContext(operation, logger)
