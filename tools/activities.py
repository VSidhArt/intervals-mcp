from server import mcp
from utils.intervals_client import get_intervals_client, get_athlete_id, INTERVALS_BASE_URL


@mcp.tool()
def get_activities(oldest_date: str, newest_date: str = None):
    """Fetch activities from intervals.icu for the configured athlete.
    
    Parameters
    ----------
    oldest_date : str
        The oldest date to fetch activities from (format: YYYY-MM-DD).
        This parameter is required.
    newest_date : str, optional
        The newest date to fetch activities from (format: YYYY-MM-DD).
        If not provided, no upper date limit is applied.
        
    Returns
    -------
    list or dict
        List of activity objects or error information
    """
    try:
        session = get_intervals_client()
        athlete_id = get_athlete_id()
        
        # Build the URL
        url = f"{INTERVALS_BASE_URL}/athlete/{athlete_id}/activities"
        
        # Build query parameters
        params = {'oldest': oldest_date}
        if newest_date:
            params['newest'] = newest_date
        
        # Make the API request
        response = session.get(url, params=params)
        response.raise_for_status()
        
        activities = response.json()
        
        # Clean activities by removing keys with empty values
        cleaned_activities = []
        for activity in activities:
            cleaned_activity = {}
            for key, value in activity.items():
                if value is not None and value != "" and value != []:
                    cleaned_activity[key] = value
            cleaned_activities.append(cleaned_activity)
        
        return {
            "status": "success",
            "count": len(cleaned_activities),
            "activities": cleaned_activities
        }
        
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc)
        }