from server import mcp
from utils.intervals_client import get_intervals_client, get_athlete_id, INTERVALS_BASE_URL
from datetime import datetime
from collections import defaultdict


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


@mcp.tool()
def get_grouped_wellness(oldest_date: str, newest_date: str = None, group_by: str = "week", include_details: bool = False):
    """Fetch and group wellness data from intervals.icu to reduce data volume and provide summary statistics.
    
    Parameters
    ----------
    oldest_date : str
        The oldest date to fetch wellness data from (format: YYYY-MM-DD).
        This parameter is required.
    newest_date : str, optional
        The newest date to fetch wellness data from (format: YYYY-MM-DD).
        If not provided, no upper date limit is applied.
    group_by : str, optional
        How to group wellness data. Options: "week", "month", "day". Default: "week"
    include_details : bool, optional
        Whether to include filtered wellness details in each group. Default: False
        
    Returns
    -------
    dict
        Grouped wellness data with summary statistics
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
        
        # Filter to essential fields only
        essential_fields = [
            'id', 'ctl', 'atl', 'rampRate', 'ctlLoad', 'atlLoad', 'weight', 
            'restingHR', 'hrv', 'sleepSecs', 'sleepScore', 'sleepQuality', 
            'steps', 'vo2max', 'fatigue', 'soreness', 'stress', 'mood', 'motivation'
        ]
        
        filtered_wellness = []
        for entry in wellness_data:
            filtered_entry = {}
            for field in essential_fields:
                if field in entry and entry[field] is not None:
                    filtered_entry[field] = entry[field]
            filtered_wellness.append(filtered_entry)
        
        # Group wellness data
        groups = defaultdict(list)
        
        for entry in filtered_wellness:
            group_key = _get_wellness_group_key(entry, group_by)
            groups[group_key].append(entry)
        
        # Calculate statistics for each group
        group_stats = {}
        total_stats = {
            'total_entries': len(filtered_wellness),
            'date_range': f"{oldest_date}" + (f" to {newest_date}" if newest_date else ""),
            'avg_ctl': 0,
            'avg_atl': 0,
            'avg_resting_hr': 0,
            'avg_hrv': 0,
            'avg_sleep_score': 0,
            'avg_steps': 0
        }
        
        all_entries_for_totals = [entry for group_entries in groups.values() for entry in group_entries]
        total_stats.update(_calculate_wellness_totals(all_entries_for_totals))
        
        for group_name, group_entries in groups.items():
            stats = _calculate_wellness_group_stats(group_entries)
            
            # Include details if requested
            if include_details:
                stats['entries'] = group_entries
                
            group_stats[group_name] = stats
        
        return {
            "status": "success",
            "period": total_stats['date_range'],
            "group_by": group_by,
            "groups": group_stats,
            "totals": total_stats
        }
        
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc)
        }


def _get_wellness_group_key(entry, group_by):
    """Get the grouping key for a wellness entry based on group_by parameter."""
    date_str = entry.get('id', '')  # wellness uses 'id' as the date
    if not date_str:
        return 'Unknown'
    
    try:
        date_obj = datetime.fromisoformat(date_str)
        
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


def _calculate_wellness_group_stats(entries):
    """Calculate statistics for a group of wellness entries."""
    stats = {
        'count': len(entries),
        'avg_ctl': 0,
        'avg_atl': 0,
        'avg_resting_hr': 0,
        'avg_hrv': 0,
        'avg_sleep_score': 0,
        'avg_sleep_hours': 0,
        'avg_steps': 0,
        'total_training_load': 0
    }
    
    if not entries:
        return stats
    
    # Initialize sums and counts for averaging
    sums = {}
    counts = {}
    fields_to_average = ['ctl', 'atl', 'restingHR', 'hrv', 'sleepScore', 'sleepSecs', 'steps', 'ctlLoad']
    
    for field in fields_to_average:
        sums[field] = 0
        counts[field] = 0
    
    for entry in entries:
        for field in fields_to_average:
            if field in entry and entry[field] is not None:
                sums[field] += entry[field]
                counts[field] += 1
        
        # Sum training load
        if entry.get('ctlLoad'):
            stats['total_training_load'] += entry['ctlLoad']
    
    # Calculate averages
    if counts['ctl'] > 0:
        stats['avg_ctl'] = round(sums['ctl'] / counts['ctl'], 2)
    if counts['atl'] > 0:
        stats['avg_atl'] = round(sums['atl'] / counts['atl'], 2)
    if counts['restingHR'] > 0:
        stats['avg_resting_hr'] = round(sums['restingHR'] / counts['restingHR'], 1)
    if counts['hrv'] > 0:
        stats['avg_hrv'] = round(sums['hrv'] / counts['hrv'], 1)
    if counts['sleepScore'] > 0:
        stats['avg_sleep_score'] = round(sums['sleepScore'] / counts['sleepScore'], 1)
    if counts['sleepSecs'] > 0:
        stats['avg_sleep_hours'] = round(sums['sleepSecs'] / counts['sleepSecs'] / 3600, 1)
    if counts['steps'] > 0:
        stats['avg_steps'] = round(sums['steps'] / counts['steps'])
    
    return stats


def _calculate_wellness_totals(entries):
    """Calculate total statistics across all wellness entries."""
    if not entries:
        return {}
    
    totals = {}
    sums = {}
    counts = {}
    fields_to_average = ['ctl', 'atl', 'restingHR', 'hrv', 'sleepScore', 'sleepSecs', 'steps']
    
    for field in fields_to_average:
        sums[field] = 0
        counts[field] = 0
    
    for entry in entries:
        for field in fields_to_average:
            if field in entry and entry[field] is not None:
                sums[field] += entry[field]
                counts[field] += 1
    
    # Calculate averages
    if counts['ctl'] > 0:
        totals['avg_ctl'] = round(sums['ctl'] / counts['ctl'], 2)
    if counts['atl'] > 0:
        totals['avg_atl'] = round(sums['atl'] / counts['atl'], 2)
    if counts['restingHR'] > 0:
        totals['avg_resting_hr'] = round(sums['restingHR'] / counts['restingHR'], 1)
    if counts['hrv'] > 0:
        totals['avg_hrv'] = round(sums['hrv'] / counts['hrv'], 1)
    if counts['sleepScore'] > 0:
        totals['avg_sleep_score'] = round(sums['sleepScore'] / counts['sleepScore'], 1)
    if counts['sleepSecs'] > 0:
        totals['avg_sleep_hours'] = round(sums['sleepSecs'] / counts['sleepSecs'] / 3600, 1)
    if counts['steps'] > 0:
        totals['avg_steps'] = round(sums['steps'] / counts['steps'])
    
    return totals