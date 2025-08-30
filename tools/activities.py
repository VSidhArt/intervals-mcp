"""MCP tools for Intervals.icu activities operations."""

from typing import Dict, Any, Optional
import logging

from server import mcp
from services.activities_service import ActivitiesService
from transformers.activities_transformer import ActivitiesTransformer
from utils.intervals_client import IntervalsAPIClient
from config.settings import get_config
from exceptions import IntervalsError, ValidationError

logger = logging.getLogger(__name__)

# Initialize services
api_client = IntervalsAPIClient()
activities_service = ActivitiesService(api_client)
config = get_config()


@mcp.tool()
def get_activities(oldest_date: str, newest_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Primary tool for fetching activities from intervals.icu for the configured athlete.

    **Best for:** Getting complete list of activities within a date range, analyzing training
    history, exporting activity data.
    **Not recommended for:** Large date ranges without pagination; real-time activity tracking.
    **Common mistakes:** Using wrong date format (must be YYYY-MM-DD); requesting too large
    date ranges that may timeout.
    **Prompt Example:** "Get my activities from 2024-01-01 to 2024-01-31" or
    "Show me all activities from last week"
    **Usage Example:**
    ```json
    {
      "name": "get_activities",
      "arguments": {
        "oldest_date": "2024-01-01",
        "newest_date": "2024-01-31"
      }
    }
    ```
    **Tool Relationships:** Use this first to get activity list, then use get_grouped_activities
    for aggregated analysis, or get specific activity details as needed.
    **Returns:** Complete activity data including id, name, type, distance, duration, power,
    heart rate, and other metrics.

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
    dict
        Dictionary containing:
        - status: "success" or "error"
        - count: Number of activities returned
        - activities: List of transformed activity objects

    Raises
    ------
    ValidationError: If date format is invalid.
    IntervalsError: If the API request fails.
    """
    try:
        logger.info(f"Fetching activities from {oldest_date} to {newest_date or 'now'}")

        # Fetch activities from service
        activities = activities_service.get_activities(oldest_date, newest_date)

        # Transform and return
        transformed = ActivitiesTransformer.transform_activities_response(activities)

        logger.info(f"Successfully fetched {transformed['count']} activities")
        return transformed

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return {"status": "error", "error": str(e), "field": e.field}
    except IntervalsError as e:
        logger.error(f"API error fetching activities: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error fetching activities: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
def get_grouped_activities(
    oldest_date: str,
    newest_date: Optional[str] = None,
    group_by: str = "sport",
    include_details: bool = False,
) -> Dict[str, Any]:
    """
    Tool for fetching and grouping activities to reduce data volume and show patterns.

    **Best for:** Analyzing training patterns, summarizing activity by sport/time period,
    creating training reports, reducing data volume for large date ranges.
    **Not recommended for:** Getting individual activity details; real-time tracking.
    **Common mistakes:** Using invalid group_by value; requesting details for large datasets.
    **Prompt Example:** "Group my activities by sport from January" or
    "Show me weekly activity summary for last month"
    **Usage Example:**
    ```json
    {
      "name": "get_grouped_activities",
      "arguments": {
        "oldest_date": "2024-01-01",
        "newest_date": "2024-01-31",
        "group_by": "week",
        "include_details": false
      }
    }
    ```
    **Tool Relationships:** Use after get_activities to analyze patterns, or directly for
    summarized data when individual activities aren't needed.
    **Returns:** Grouped activity data with summaries (count, duration, distance) per group.

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
        Dictionary containing:
        - groups: Dictionary of groups with summaries
        - total_activities: Total number of activities
        - Additional metadata based on grouping type

    Raises
    ------
    ValidationError: If parameters are invalid.
    IntervalsError: If the API request fails.
    """
    try:
        logger.info(
            f"Fetching grouped activities from {oldest_date} to {newest_date or 'now'}, " f"grouped by {group_by}"
        )

        # Fetch grouped activities from service
        grouped = activities_service.get_grouped_activities(oldest_date, newest_date, group_by, include_details)

        # The service already returns a well-structured response
        result = {"status": "success", **grouped}  # Include all the grouped data

        logger.info(f"Successfully grouped {grouped.get('total_activities', 0)} activities")
        return result

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return {"status": "error", "error": str(e), "field": e.field}
    except IntervalsError as e:
        logger.error(f"API error fetching grouped activities: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error fetching grouped activities: {e}")
        return {"status": "error", "error": str(e)}
