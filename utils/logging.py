import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from config.settings import LoggingConfig


def setup_logging(config: Optional[LoggingConfig] = None) -> None:
    """Configure logging for the application.

    Logs are only output when DEBUG environment variable is set to true.
    Logs are sent to stderr to keep stdout clean for MCP communication.
    Logs are also saved to dated files in the logs directory.
    """
    if config is None:
        from config.settings import get_config

        config = get_config().logging

    # Clear existing handlers
    logging.root.handlers.clear()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(config.level)

    # Only add handlers if DEBUG is enabled
    if config.debug:
        # Create formatter
        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Create and configure stderr handler
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(formatter)
        root_logger.addHandler(stderr_handler)

        # Create logs directory if it doesn't exist
        log_dir = Path(config.log_dir)
        log_dir.mkdir(exist_ok=True)

        # Create file handler with date in filename
        log_filename = log_dir / f"intervals-mcp-{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given module."""
    return logging.getLogger(name)
