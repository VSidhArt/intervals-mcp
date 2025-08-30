"""MCP tools for Intervals.icu wellness operations."""

from typing import Dict, Any, Optional
import logging

from server import mcp
from services.wellness_service import WellnessService
from transformers.wellness_transformer import WellnessTransformer
from utils.intervals_client import IntervalsAPIClient
from config.settings import get_config
from exceptions import IntervalsError, ValidationError

logger = logging.getLogger(__name__)

# Initialize services
api_client = IntervalsAPIClient()
wellness_service = WellnessService(api_client)
config = get_config()


@mcp.tool()
def get_wellness(oldest_date: str, newest_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Primary tool for fetching wellness data from intervals.icu for the configured athlete.

    **Best for:** Getting daily wellness metrics, tracking health trends, monitoring recovery,
    analyzing sleep patterns, weight tracking.
    **Not recommended for:** Real-time monitoring; medical diagnosis; very large date ranges.
    **Common mistakes:** Using wrong date format (must be YYYY-MM-DD); requesting years of data
    at once.
    **Prompt Example:** "Get my wellness data from 2024-01-01 to 2024-01-31" or
    "Show me wellness metrics for last month"
    **Usage Example:**
    ```json
    {
      "name": "get_wellness",
      "arguments": {
        "oldest_date": "2024-01-01",
        "newest_date": "2024-01-31"
      }
    }
    ```
    **Tool Relationships:** Use this first to get wellness records, then use get_grouped_wellness
    for trend analysis or summary statistics.
    **Returns:** Complete wellness data including weight, HRV, resting HR, sleep, fatigue,
    mood, motivation, and training metrics (ATL/CTL/TSB).

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
        Dictionary containing:
        - status: "success" or "error"
        - count: Number of wellness records returned
        - wellness: List of transformed wellness objects
        - date_range: Date range of the wellness data

    Raises
    ------
    ValidationError: If date format is invalid.
    IntervalsError: If the API request fails.
    """
    try:
        logger.info(f"Fetching wellness data from {oldest_date} to {newest_date or 'now'}")

        # Fetch wellness data from service
        wellness_records = wellness_service.get_wellness(oldest_date, newest_date)

        # Transform and return
        transformed = WellnessTransformer.transform_wellness_response(wellness_records)

        logger.info(f"Successfully fetched {transformed['count']} wellness records")
        return transformed

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return {"status": "error", "error": str(e), "field": e.field}
    except IntervalsError as e:
        logger.error(f"API error fetching wellness data: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error fetching wellness data: {e}")
        return {"status": "error", "error": str(e)}


@mcp.tool()
def get_grouped_wellness(
    oldest_date: str,
    newest_date: Optional[str] = None,
    group_by: str = "month",
    include_details: bool = False,
) -> Dict[str, Any]:
    """
    Tool for fetching and grouping wellness data to show trends and patterns.

    **Best for:** Analyzing wellness trends over time, creating health reports, tracking
    recovery patterns, monitoring training stress balance, identifying correlations.
    **Not recommended for:** Individual day analysis; real-time monitoring.
    **Common mistakes:** Using invalid group_by value; requesting details for very large datasets.
    **Prompt Example:** "Show me monthly wellness trends for 2024" or
    "Group my wellness data by week for the last 3 months"
    **Usage Example:**
    ```json
    {
      "name": "get_grouped_wellness",
      "arguments": {
        "oldest_date": "2024-01-01",
        "newest_date": "2024-03-31",
        "group_by": "month",
        "include_details": false
      }
    }
    ```
    **Tool Relationships:** Use after get_wellness to analyze patterns, or directly for
    trend analysis when individual records aren't needed.
    **Returns:** Grouped wellness data with averages and statistics per time period.

    Parameters
    ----------
    oldest_date : str
        The oldest date to fetch wellness data from (format: YYYY-MM-DD).
        This parameter is required.
    newest_date : str, optional
        The newest date to fetch wellness data from (format: YYYY-MM-DD).
        If not provided, no upper date limit is applied.
    group_by : str, optional
        How to group wellness data. Options: "week", "month", "all". Default: "month"
    include_details : bool, optional
        Whether to include individual records in each group. Default: False

    Returns
    -------
    dict
        Dictionary containing:
        - status: "success" or "error"
        - groups: Dictionary of groups with summaries (when not "all")
        - summary: Aggregate statistics (when group_by is "all")
        - total_records: Total number of wellness records
        - Additional metadata based on grouping type

    Raises
    ------
    ValidationError: If parameters are invalid.
    IntervalsError: If the API request fails.
    """
    try:
        logger.info(
            f"Fetching grouped wellness data from {oldest_date} to {newest_date or 'now'}, " f"grouped by {group_by}"
        )

        # Fetch grouped wellness data from service
        grouped = wellness_service.get_grouped_wellness(oldest_date, newest_date, group_by, include_details)

        # The service already returns a well-structured response
        result = {"status": "success", **grouped}  # Include all the grouped data

        logger.info(f"Successfully grouped {grouped.get('total_records', 0)} wellness records")
        return result

    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return {"status": "error", "error": str(e), "field": e.field}
    except IntervalsError as e:
        logger.error(f"API error fetching grouped wellness data: {e}")
        return {"status": "error", "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error fetching grouped wellness data: {e}")
        return {"status": "error", "error": str(e)}
