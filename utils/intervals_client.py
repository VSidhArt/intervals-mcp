import time
from typing import Dict, Any, Optional, List, Union
import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from config.settings import get_config
from utils.logging import get_logger
from utils.api_decorators import handle_api_errors

logger = get_logger(__name__)


class IntervalsAPIClient:
    """HTTP client wrapper for Intervals.icu API with retry logic and error handling."""

    def __init__(self):
        """Initialize the Intervals API client."""
        self.config = get_config()
        self.base_url = self.config.intervals.base_url
        self.athlete_id = self.config.intervals.athlete_id
        self.session = self._create_session()
        self._setup_auth()

    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.intervals.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _setup_auth(self):
        """Set up authentication for all requests."""
        # Intervals.icu uses HTTP Basic Auth with "API_KEY" as username
        self.session.auth = HTTPBasicAuth("API_KEY", self.config.intervals.api_key)
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    @handle_api_errors
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], List[Any]]:
        """Execute GET request to Intervals API."""
        url = f"{self.base_url}{endpoint}"
        logger.debug("GET %s with params: %s", url, params)

        # Add delay between requests if configured
        if self.config.intervals.request_delay > 0:
            time.sleep(self.config.intervals.request_delay)

        response = self.session.get(url, params=params, timeout=self.config.intervals.timeout)

        self._check_response(response)
        return response.json()

    @handle_api_errors
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute POST request to Intervals API."""
        url = f"{self.base_url}{endpoint}"
        logger.debug("POST %s", url)

        # Add delay between requests if configured
        if self.config.intervals.request_delay > 0:
            time.sleep(self.config.intervals.request_delay)

        response = self.session.post(url, json=data, timeout=self.config.intervals.timeout)

        self._check_response(response)
        return response.json() if response.text else {}

    @handle_api_errors
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute PUT request to Intervals API."""
        url = f"{self.base_url}{endpoint}"
        logger.debug("PUT %s", url)

        # Add delay between requests if configured
        if self.config.intervals.request_delay > 0:
            time.sleep(self.config.intervals.request_delay)

        response = self.session.put(url, json=data, timeout=self.config.intervals.timeout)

        self._check_response(response)
        return response.json() if response.text else {}

    @handle_api_errors
    def delete(self, endpoint: str) -> bool:
        """Execute DELETE request to Intervals API."""
        url = f"{self.base_url}{endpoint}"
        logger.debug("DELETE %s", url)

        # Add delay between requests if configured
        if self.config.intervals.request_delay > 0:
            time.sleep(self.config.intervals.request_delay)

        response = self.session.delete(url, timeout=self.config.intervals.timeout)

        self._check_response(response)
        return response.status_code in (200, 204)

    def _check_response(self, response: requests.Response):
        """Check response for errors and raise appropriate exceptions."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Log error details
            logger.error(
                "API request failed: %s %s - Status: %s",
                response.request.method,
                response.url,
                response.status_code,
            )

            # Try to extract error message from response
            try:
                error_data = response.json()
                error_message = error_data.get("detail", str(e))
            except Exception:
                error_message = response.text or str(e)

            # Re-raise to be handled by decorator
            raise requests.exceptions.HTTPError(error_message, response=response)
