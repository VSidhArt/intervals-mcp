"""Service for Intervals.icu activities operations."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from collections import defaultdict

from config.settings import get_config
from utils.intervals_client import IntervalsAPIClient
from exceptions import IntervalsError, ValidationError

logger = logging.getLogger(__name__)


class ActivitiesService:
    """Service for managing Intervals.icu activities."""

    def __init__(self, api_client: Optional[IntervalsAPIClient] = None):
        """
        Initialize ActivitiesService.

        Args:
            api_client: The Intervals API client to use for requests.
        """
        self.config = get_config()
        self.api_client = api_client or IntervalsAPIClient()

    def get_activities(self, oldest_date: str, newest_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve activities for the configured athlete.

        Args:
            oldest_date: The oldest date to fetch activities from (format: YYYY-MM-DD).
            newest_date: The newest date to fetch activities from (format: YYYY-MM-DD).

        Returns:
            List of activity dictionaries.

        Raises:
            ValidationError: If date format is invalid.
            IntervalsError: If the API request fails.
        """
        # Validate date formats
        self._validate_date_format(oldest_date, "oldest_date")
        if newest_date:
            self._validate_date_format(newest_date, "newest_date")

        # Build the endpoint
        endpoint = f"/athlete/{self.api_client.athlete_id}/activities"

        # Build query parameters
        params = {"oldest": oldest_date}
        if newest_date:
            params["newest"] = newest_date

        logger.debug(
            "Fetching activities for athlete %s from %s to %s",
            self.api_client.athlete_id,
            oldest_date,
            newest_date or "now",
        )

        # Fetch from API
        try:
            response = self.api_client.get(endpoint, params=params)
            logger.info(
                "Successfully retrieved %d activities",
                len(response) if isinstance(response, list) else 0,
            )
            return response if isinstance(response, list) else []
        except IntervalsError as e:
            logger.error("Failed to retrieve activities: %s", e)
            raise

    def get_grouped_activities(
        self,
        oldest_date: str,
        newest_date: Optional[str] = None,
        group_by: str = "sport",
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieve and group activities to reduce data volume.

        Args:
            oldest_date: The oldest date to fetch activities from (format: YYYY-MM-DD).
            newest_date: The newest date to fetch activities from (format: YYYY-MM-DD).
            group_by: How to group activities ("sport", "day", "week", "month").
            include_details: Whether to include filtered activity details in each group.

        Returns:
            Dictionary with grouped activities and summaries.

        Raises:
            ValidationError: If parameters are invalid.
            IntervalsError: If the API request fails.
        """
        # Validate group_by parameter
        valid_group_by = {"sport", "day", "week", "month"}
        if group_by not in valid_group_by:
            raise ValidationError(
                "group_by",
                group_by,
                f"Invalid group_by value. Must be one of: {', '.join(valid_group_by)}",
            )

        # Get activities
        activities = self.get_activities(oldest_date, newest_date)

        # Group activities based on the specified method
        if group_by == "sport":
            grouped = self._group_by_sport(activities, include_details)
        elif group_by == "day":
            grouped = self._group_by_time_period(activities, "day", include_details)
        elif group_by == "week":
            grouped = self._group_by_time_period(activities, "week", include_details)
        elif group_by == "month":
            grouped = self._group_by_time_period(activities, "month", include_details)
        else:
            grouped = {}

        return grouped

    def _validate_date_format(self, date_str: str, field_name: str):
        """Validate that a date string is in YYYY-MM-DD format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(field_name, date_str, "Date must be in YYYY-MM-DD format")

    def _group_by_sport(self, activities: List[Dict[str, Any]], include_details: bool) -> Dict[str, Any]:
        """Group activities by sport type."""
        groups = defaultdict(
            lambda: {
                "count": 0,
                "total_duration": 0,
                "total_distance": 0,
                "total_elevation": 0,
                "activities": [] if include_details else None,
            }
        )

        for activity in activities:
            sport = activity.get("type", "Unknown")
            groups[sport]["count"] += 1
            groups[sport]["total_duration"] += activity.get("moving_time", 0) or 0
            groups[sport]["total_distance"] += activity.get("distance", 0) or 0
            groups[sport]["total_elevation"] += activity.get("icu_elevation_gain", 0) or 0

            if include_details:
                # Include filtered details
                filtered_activity = {
                    "id": activity.get("id"),
                    "name": activity.get("name"),
                    "start_date_local": activity.get("start_date_local"),
                    "moving_time": activity.get("moving_time"),
                    "distance": activity.get("distance"),
                    "icu_elevation_gain": activity.get("icu_elevation_gain"),
                    "icu_average_watts": activity.get("icu_average_watts"),
                    "average_heartrate": activity.get("average_heartrate"),
                }
                groups[sport]["activities"].append(filtered_activity)

        return {
            "groups": dict(groups),
            "total_activities": len(activities),
            "date_range": {
                "oldest": activities[-1].get("start_date_local") if activities else None,
                "newest": activities[0].get("start_date_local") if activities else None,
            },
        }

    def _group_by_time_period(
        self, activities: List[Dict[str, Any]], period: str, include_details: bool
    ) -> Dict[str, Any]:
        """Group activities by time period (day, week, or month)."""
        groups = defaultdict(
            lambda: {
                "count": 0,
                "sports": set(),
                "total_duration": 0,
                "total_distance": 0,
                "activities": [] if include_details else None,
            }
        )

        for activity in activities:
            start_date = activity.get("start_date_local", "")
            if not start_date:
                continue

            # Extract the period key
            date_obj = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            if period == "day":
                period_key = date_obj.strftime("%Y-%m-%d")
            elif period == "week":
                # Get ISO week number
                year, week, _ = date_obj.isocalendar()
                period_key = f"{year}-W{week:02d}"
            elif period == "month":
                period_key = date_obj.strftime("%Y-%m")
            else:
                continue

            groups[period_key]["count"] += 1
            groups[period_key]["sports"].add(activity.get("type", "Unknown"))
            groups[period_key]["total_duration"] += activity.get("moving_time", 0) or 0
            groups[period_key]["total_distance"] += activity.get("distance", 0) or 0

            if include_details:
                filtered_activity = {
                    "id": activity.get("id"),
                    "name": activity.get("name"),
                    "type": activity.get("type"),
                    "start_date_local": activity.get("start_date_local"),
                    "moving_time": activity.get("moving_time"),
                    "distance": activity.get("distance"),
                }
                groups[period_key]["activities"].append(filtered_activity)

        # Convert sets to lists for JSON serialization
        for period_key in groups:
            groups[period_key]["sports"] = list(groups[period_key]["sports"])

        return {
            "groups": dict(groups),
            "total_activities": len(activities),
            "period_type": period,
        }
