from server import mcp
from utils.intervals_client import get_intervals_client, get_athlete_id, INTERVALS_BASE_URL


@mcp.tool()
def get_wellness(oldest_date: str, newest_date: str = None):
    """Fetch wellness data from intervals.icu for the configured athlete.
    
    Parameters
    ----------
    oldest_date : str
        The oldest date to fetch wellness data from (format: YYYY-MM-DD).
        This parameter is required.
    newest_date : str, optional
        The newest date to fetch wellness data from (format: YYYY-MM-DD).
        If not provided, no upper date limit is applied.
        
    Returns
    -------
    dict
        Wellness data objects or error information
    """
    try:
        session = get_intervals_client()
        athlete_id = get_athlete_id()
        
        # Build the URL
        url = f"{INTERVALS_BASE_URL}/athlete/{athlete_id}/wellness"
        
        # Build query parameters
        params = {'oldest': oldest_date}
        if newest_date:
            params['newest'] = newest_date
        
        # Make the API request
        response = session.get(url, params=params)
        response.raise_for_status()
        
        wellness_data = response.json()
        
        # Clean wellness data by removing keys with empty values
        cleaned_wellness = []
        for entry in wellness_data:
            cleaned_entry = {}
            for key, value in entry.items():
                if value is not None and value != "" and value != []:
                    cleaned_entry[key] = value
            cleaned_wellness.append(cleaned_entry)
        
        return {
            "status": "success",
            "count": len(cleaned_wellness),
            "wellness": cleaned_wellness
        }
        
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc)
        }