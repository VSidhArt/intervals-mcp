"""Tests for config module."""

import pytest
from config.settings import IntervalsConfig, LoggingConfig, AppConfig, load_config


def test_intervals_config_validation():
    """Test IntervalsConfig validation."""
    # Valid config
    config = IntervalsConfig(
        base_url="https://intervals.icu/api/v1",
        api_key="test_key",
        athlete_id="i123456",
    )
    assert config.api_key == "test_key"
    assert config.athlete_id == "i123456"

    # Invalid API key
    with pytest.raises(ValueError, match="Intervals API key is required"):
        IntervalsConfig(
            base_url="https://intervals.icu/api/v1",
            api_key="",
            athlete_id="i123456",
        )

    # Invalid athlete ID
    with pytest.raises(ValueError, match="Invalid athlete ID format"):
        IntervalsConfig(
            base_url="https://intervals.icu/api/v1",
            api_key="test_key",
            athlete_id="123456",  # Missing 'i' prefix
        )


def test_logging_config():
    """Test LoggingConfig validation."""
    # Valid config
    config = LoggingConfig(level="INFO")
    assert config.level == "INFO"

    # Invalid level
    with pytest.raises(ValueError, match="Invalid log level"):
        LoggingConfig(level="INVALID")


def test_app_config():
    """Test AppConfig validation."""
    intervals_config = IntervalsConfig(
        base_url="https://intervals.icu/api/v1",
        api_key="test_key",
        athlete_id="i123456",
    )
    
    config = AppConfig(
        intervals=intervals_config,
        environment="production"
    )
    assert config.environment == "production"

    # Invalid environment
    with pytest.raises(ValueError, match="Invalid environment"):
        AppConfig(
            intervals=intervals_config,
            environment="invalid"
        )


def test_load_config(mock_env_vars):
    """Test loading config from environment variables."""
    config = load_config()
    assert config.intervals.api_key == "test-api-key"
    assert config.intervals.athlete_id == "i123456"
    assert config.environment == "testing"