from server import mcp
from utils.intervals_client import get_intervals_client, get_athlete_id, INTERVALS_BASE_URL
from datetime import datetime
from collections import defaultdict


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


@mcp.tool()
def get_grouped_activities(oldest_date: str, newest_date: str = None, group_by: str = "sport", include_details: bool = False):
    """Fetch and group activities from intervals.icu to reduce data volume.
    
    Parameters
    ----------
    oldest_date : str
        The oldest date to fetch activities from (format: YYYY-MM-DD).
        This parameter is required.
    newest_date : str, optional
        The newest date to fetch activities from (format: YYYY-MM-DD).
        If not provided, no upper date limit is applied.
    group_by : str, optional
        How to group activities. Options: "sport", "day", "week", "month". Default: "sport"
    include_details : bool, optional
        Whether to include filtered activity details in each group. Default: False
        
    Returns
    -------
    dict
        Grouped activities with summary statistics
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
        
        # Filter to essential fields only
        essential_fields = [
            'id', 'type', 'start_date_local', 'name', 'elapsed_time', 'moving_time',
            'distance', 'icu_distance', 'calories', 'icu_training_load', 
            'average_heartrate', 'max_heartrate', 'kg_lifted', 'icu_intensity'
        ]
        
        filtered_activities = []
        for activity in activities:
            filtered_activity = {}
            for field in essential_fields:
                if field in activity and activity[field] is not None:
                    filtered_activity[field] = activity[field]
            filtered_activities.append(filtered_activity)
        
        # Group activities
        groups = defaultdict(list)
        
        for activity in filtered_activities:
            group_key = _get_group_key(activity, group_by)
            groups[group_key].append(activity)
        
        # Calculate statistics for each group
        group_stats = {}
        total_stats = {
            'total_activities': len(filtered_activities),
            'total_time': 0,
            'total_distance': 0,
            'total_calories': 0,
            'total_training_load': 0
        }
        
        for group_name, group_activities in groups.items():
            stats = _calculate_group_stats(group_activities)
            
            # Add to totals
            total_stats['total_time'] += stats['total_time']
            total_stats['total_distance'] += stats['total_distance'] 
            total_stats['total_calories'] += stats['total_calories']
            total_stats['total_training_load'] += stats['total_training_load']
            
            # Include details if requested
            if include_details:
                stats['activities'] = group_activities
                
            group_stats[group_name] = stats
        
        period_str = oldest_date
        if newest_date:
            period_str += f" to {newest_date}"
        
        return {
            "status": "success",
            "period": period_str,
            "group_by": group_by,
            "groups": group_stats,
            "totals": total_stats
        }
        
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc)
        }


def _get_group_key(activity, group_by):
    """Get the grouping key for an activity based on group_by parameter."""
    if group_by == "sport":
        return activity.get('type', 'Unknown')
    
    elif group_by in ["day", "week", "month"]:
        date_str = activity.get('start_date_local', '')
        if not date_str:
            return 'Unknown'
        
        try:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            if group_by == "day":
                return date_obj.strftime('%Y-%m-%d')
            elif group_by == "week":
                year, week, _ = date_obj.isocalendar()
                return f"{year}-W{week:02d}"
            elif group_by == "month":
                return date_obj.strftime('%Y-%m')
                
        except ValueError:
            return 'Unknown'
    
    return 'Unknown'


def _calculate_group_stats(activities):
    """Calculate statistics for a group of activities."""
    stats = {
        'count': len(activities),
        'total_time': 0,
        'total_distance': 0,
        'total_calories': 0,
        'total_training_load': 0,
        'total_kg_lifted': 0,
        'avg_heart_rate': 0,
        'avg_intensity': 0
    }
    
    hr_sum = 0
    hr_count = 0
    intensity_sum = 0
    intensity_count = 0
    
    for activity in activities:
        # Sum totals
        stats['total_time'] += activity.get('elapsed_time', 0) or 0
        stats['total_distance'] += activity.get('distance', 0) or activity.get('icu_distance', 0) or 0
        stats['total_calories'] += activity.get('calories', 0) or 0
        stats['total_training_load'] += activity.get('icu_training_load', 0) or 0
        stats['total_kg_lifted'] += activity.get('kg_lifted', 0) or 0
        
        # Calculate averages
        if activity.get('average_heartrate'):
            hr_sum += activity['average_heartrate']
            hr_count += 1
            
        if activity.get('icu_intensity'):
            intensity_sum += activity['icu_intensity']
            intensity_count += 1
    
    # Calculate averages
    if hr_count > 0:
        stats['avg_heart_rate'] = round(hr_sum / hr_count, 1)
    if intensity_count > 0:
        stats['avg_intensity'] = round(intensity_sum / intensity_count, 1)
    
    # Convert time to hours for readability
    stats['total_time_hours'] = round(stats['total_time'] / 3600, 2)
    
    return stats