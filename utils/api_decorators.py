import functools
from typing import Any, Callable, TypeVar
import requests
from exceptions import (
    NetworkError,
    TimeoutError,
    AuthenticationError,
    AuthorizationError,
    RateLimitError,
    IntervalsError,
)
from utils.logging import get_logger
from config.settings import get_config

logger = get_logger(__name__)
F = TypeVar("F", bound=Callable[..., Any])


def handle_api_errors(func: F) -> F:
    """Decorator to handle API request exceptions consistently."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        config = get_config()

        try:
            return func(*args, **kwargs)
        except requests.exceptions.Timeout:
            error = TimeoutError(config.intervals.timeout)
            logger.error("Timeout error: %s", str(error), exc_info=True)
            raise error
        except requests.exceptions.ConnectionError as e:
            error = NetworkError(f"Connection failed: {str(e)}")
            logger.error("Connection error: %s", str(error), exc_info=True)
            raise error
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code if e.response else None
            if status_code == 401:
                raise AuthenticationError("Invalid API key or authentication failed")
            elif status_code == 403:
                raise AuthorizationError("Access denied to this resource")
            elif status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                retry_after_int = int(retry_after) if retry_after else None
                raise RateLimitError(retry_after_int)

            # Extract detailed error message from response
            error_message = str(e)
            if e.response:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get("detail", error_data.get("message", str(e)))
                except Exception:
                    error_message = e.response.text or str(e)

            # Raise IntervalsError with status code and detailed message
            raise IntervalsError(
                f"API request failed: {error_message}",
                details={"status_code": status_code, "url": e.response.url if e.response else None},
                status_code=status_code,
            ) from e
        except requests.exceptions.RequestException as e:
            error = NetworkError(f"Request failed: {str(e)}")
            logger.error("Request error: %s", str(error), exc_info=True)
            raise error

    return wrapper  # type: ignore
