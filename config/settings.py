import os
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse


@dataclass
class IntervalsConfig:
    """Intervals.icu-specific configuration with validation."""

    base_url: str = "https://intervals.icu/api/v1"
    api_key: str = ""
    athlete_id: str = ""
    timeout: int = 30
    max_retries: int = 3
    request_delay: float = 0.1

    def __post_init__(self):
        """Validate configuration after initialization."""
        self._validate_base_url()
        self._validate_api_key()
        self._validate_athlete_id()
        self._validate_numeric_fields()

    def _validate_base_url(self):
        """Validate the base URL format."""
        if not self.base_url:
            raise ValueError("Intervals base_url is required")

        parsed = urlparse(self.base_url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid base_url format: {self.base_url}")

        if parsed.scheme not in ("http", "https"):
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Use http or https")

        # Ensure URL ends without trailing slash for consistency
        self.base_url = self.base_url.rstrip("/")

    def _validate_api_key(self):
        """Validate the API key."""
        if not self.api_key:
            raise ValueError("Intervals API key is required. " "Please set INTERVALS_API_KEY environment variable.")

        # API key should be a non-empty string (intervals.icu uses various formats)
        if not isinstance(self.api_key, str) or len(self.api_key) < 1:
            raise ValueError("Invalid API key format")

    def _validate_athlete_id(self):
        """Validate the athlete ID."""
        if not self.athlete_id:
            raise ValueError("Athlete ID is required. " "Please set INTERVALS_ATHLETE_ID environment variable.")

        # Athlete IDs should start with 'i' followed by numbers
        if not self.athlete_id.startswith("i"):
            raise ValueError(
                f"Invalid athlete ID format: {self.athlete_id}. " "Should start with 'i' (e.g., 'i335136')"
            )

    def _validate_numeric_fields(self):
        """Validate numeric configuration fields."""
        if self.timeout <= 0:
            raise ValueError(f"Invalid timeout: {self.timeout}. Must be positive")

        if self.max_retries < 0:
            raise ValueError(f"Invalid max_retries: {self.max_retries}. Must be non-negative")

        if self.request_delay < 0:
            raise ValueError(f"Invalid request_delay: {self.request_delay}. Must be non-negative")


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    debug: bool = False
    log_dir: str = "logs"

    def __post_init__(self):
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {self.level}")
        self.level = self.level.upper()


@dataclass
class AppConfig:
    """Main application configuration."""

    intervals: IntervalsConfig
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    environment: str = "production"

    def __post_init__(self):
        valid_environments = {"development", "testing", "production"}
        if self.environment.lower() not in valid_environments:
            raise ValueError(f"Invalid environment: {self.environment}")
        self.environment = self.environment.lower()


def load_config() -> AppConfig:
    """Load configuration from environment variables."""
    # Required variables
    api_key = os.environ.get("INTERVALS_API_KEY")
    if not api_key:
        raise ValueError(
            "INTERVALS_API_KEY environment variable is required. "
            "Please export a valid API key from intervals.icu settings."
        )

    athlete_id = os.environ.get("INTERVALS_ATHLETE_ID")
    if not athlete_id:
        raise ValueError(
            "INTERVALS_ATHLETE_ID environment variable is required. "
            "Please export a valid athlete ID (e.g., 'i335136')."
        )

    # Optional variables with defaults
    base_url = os.environ.get("INTERVALS_BASE_URL", "https://intervals.icu/api/v1")

    # Create Intervals config
    intervals_config = IntervalsConfig(
        base_url=base_url,
        api_key=api_key,
        athlete_id=athlete_id,
        timeout=int(os.environ.get("INTERVALS_TIMEOUT", "30")),
        max_retries=int(os.environ.get("INTERVALS_MAX_RETRIES", "3")),
        request_delay=float(os.environ.get("INTERVALS_REQUEST_DELAY", "0.1")),
    )

    # Create logging config
    logging_config = LoggingConfig(
        level=os.environ.get("LOG_LEVEL", "INFO"),
        debug=os.environ.get("DEBUG", "false").lower() in ("true", "1", "yes", "on"),
        log_dir=os.environ.get("LOG_DIR", "logs"),
    )

    # Create app config
    return AppConfig(
        intervals=intervals_config,
        logging=logging_config,
        environment=os.environ.get("ENVIRONMENT", "production"),
    )


# Global configuration instance
_config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get or create singleton configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config():
    """Reset the global configuration (mainly for testing)."""
    global _config
    _config = None
