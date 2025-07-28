import requests
import os
from requests.auth import HTTPBasicAuth

# Intervals.icu API configuration
INTERVALS_BASE_URL = "https://intervals.icu/api/v1"

def get_intervals_client():
    """Create and return a requests session with intervals.icu authentication.
    
    The authentication is established lazily so that any authentication
    errors are raised *after* the MCP handshake. This prevents the entire
    server process from crashing before the client receives the
    initialization response.
    """
    api_key = os.getenv("INTERVALS_API_KEY")
    if not api_key:
        raise ValueError(
            "Environment variable INTERVALS_API_KEY is not set. "
            "Please export a valid API key from intervals.icu settings."
        )
    
    session = requests.Session()
    session.auth = HTTPBasicAuth("API_KEY", api_key)
    return session

def get_athlete_id():
    """Get the athlete ID from environment variable.
    
    Returns
    -------
    str
        The athlete ID (e.g., 'i335136')
    """
    athlete_id = os.getenv("INTERVALS_ATHLETE_ID")
    if not athlete_id:
        raise ValueError(
            "Environment variable INTERVALS_ATHLETE_ID is not set. "
            "Please export a valid athlete ID (e.g., 'i335136')."
        )
    return athlete_id