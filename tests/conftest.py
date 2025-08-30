import os
import pytest
from unittest.mock import Mock, patch
from config.settings import AppConfig, IntervalsConfig, LoggingConfig


@pytest.fixture
def mock_intervals_config():
    """Mock Intervals configuration for testing."""
    return IntervalsConfig(
        base_url="https://intervals.icu/api/v1",
        api_key="test-api-key",
        athlete_id="i123456",
        timeout=30,
        max_retries=3,
        request_delay=0.0,
    )


@pytest.fixture
def mock_app_config(mock_intervals_config):
    """Mock application configuration for testing."""
    return AppConfig(
        intervals=mock_intervals_config,
        logging=LoggingConfig(level="DEBUG", debug=True),
        environment="testing",
    )


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "INTERVALS_API_KEY": "test-api-key",
        "INTERVALS_ATHLETE_ID": "i123456",
        "INTERVALS_BASE_URL": "https://intervals.icu/api/v1",
        "ENVIRONMENT": "testing",
        "LOG_LEVEL": "DEBUG",
        "DEBUG": "true",
    }

    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture(autouse=True)
def reset_global_config():
    """Reset global config before each test."""
    from config.settings import reset_config

    reset_config()
    yield
    reset_config()


@pytest.fixture
def mock_api_client():
    """Mock Intervals API client."""
    client = Mock()
    client.athlete_id = "i123456"
    client.base_url = "https://intervals.icu/api/v1"
    client.get = Mock()
    client.post = Mock()
    client.put = Mock()
    client.delete = Mock()
    return client


@pytest.fixture
def sample_activity_data():
    """Sample activity data for testing."""
    return [
        {
            "id": "123",
            "name": "Morning Run",
            "type": "Run",
            "start_date_local": "2024-01-15T08:00:00Z",
            "moving_time": 3600,
            "distance": 10000,
            "icu_elevation_gain": 150,
            "average_heartrate": 145,
            "icu_average_watts": 250,
            "calories": 600,
            "device_name": "Garmin",
            "athlete_id": "i123456",
        },
        {
            "id": "124",
            "name": "Evening Ride",
            "type": "Ride",
            "start_date_local": "2024-01-15T18:00:00Z",
            "moving_time": 5400,
            "distance": 30000,
            "icu_elevation_gain": 300,
            "average_heartrate": 135,
            "icu_average_watts": 200,
            "calories": 800,
            "device_name": "Wahoo",
            "athlete_id": "i123456",
        },
    ]


@pytest.fixture
def sample_wellness_data():
    """Sample wellness data for testing."""
    return [
        {
            "id": "2024-01-15",  # id is the date
            "weight": 70.5,
            "restingHR": 55,
            "hrv": 45,
            "sleepTime": 7.5,
            "sleepQuality": 4,
            "fatigue": 3,
            "mood": 4,
            "motivation": 4,
            "atl": 75,
            "ctl": 65,
            "tsb": -10,
            "kcalConsumed": 2500,
            "athlete_id": "i123456",
        },
        {
            "id": "2024-01-14",
            "weight": 70.3,
            "restingHR": 56,
            "hrv": 42,
            "sleepTime": 8.0,
            "sleepQuality": 5,
            "fatigue": 2,
            "mood": 5,
            "motivation": 5,
            "atl": 70,
            "ctl": 64,
            "tsb": -6,
            "kcalConsumed": 2400,
            "athlete_id": "i123456",
        },
    ]


@pytest.fixture
def mock_requests_response():
    """Mock requests.Response object."""
    response = Mock()
    response.status_code = 200
    response.headers = {}
    response.text = ""
    response.json = Mock(return_value={})
    response.raise_for_status = Mock()
    return response
