"""Service for Intervals.icu wellness operations."""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from collections import defaultdict

from config.settings import get_config
from utils.intervals_client import IntervalsAPIClient
from exceptions import IntervalsError, ValidationError

logger = logging.getLogger(__name__)


class WellnessService:
    """Service for managing Intervals.icu wellness data."""

    def __init__(self, api_client: Optional[IntervalsAPIClient] = None):
        """
        Initialize WellnessService.

        Args:
            api_client: The Intervals API client to use for requests.
        """
        self.config = get_config()
        self.api_client = api_client or IntervalsAPIClient()

    def get_wellness(self, oldest_date: str, newest_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve wellness data for the configured athlete.

        Args:
            oldest_date: The oldest date to fetch wellness data from (format: YYYY-MM-DD).
            newest_date: The newest date to fetch wellness data from (format: YYYY-MM-DD).

        Returns:
            List of wellness data dictionaries.

        Raises:
            ValidationError: If date format is invalid.
            IntervalsError: If the API request fails.
        """
        # Validate date formats
        self._validate_date_format(oldest_date, "oldest_date")
        if newest_date:
            self._validate_date_format(newest_date, "newest_date")

        # Build the endpoint
        endpoint = f"/athlete/{self.api_client.athlete_id}/wellness"

        # Build query parameters
        params = {"oldest": oldest_date}
        if newest_date:
            params["newest"] = newest_date

        logger.debug(
            "Fetching wellness data for athlete %s from %s to %s",
            self.api_client.athlete_id,
            oldest_date,
            newest_date or "now",
        )

        # Fetch from API
        try:
            response = self.api_client.get(endpoint, params=params)
            logger.info(
                "Successfully retrieved %d wellness records",
                len(response) if isinstance(response, list) else 0,
            )
            return response if isinstance(response, list) else []
        except IntervalsError as e:
            logger.error("Failed to retrieve wellness data: %s", e)
            raise

    def get_grouped_wellness(
        self,
        oldest_date: str,
        newest_date: Optional[str] = None,
        group_by: str = "month",
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieve and group wellness data to show trends.

        Args:
            oldest_date: The oldest date to fetch wellness data from (format: YYYY-MM-DD).
            newest_date: The newest date to fetch wellness data from (format: YYYY-MM-DD).
            group_by: How to group wellness data ("week", "month", "all").
            include_details: Whether to include individual records in each group.

        Returns:
            Dictionary with grouped wellness data and statistics.

        Raises:
            ValidationError: If parameters are invalid.
            IntervalsError: If the API request fails.
        """
        # Validate group_by parameter
        valid_group_by = {"week", "month", "all"}
        if group_by not in valid_group_by:
            raise ValidationError(
                "group_by",
                group_by,
                f"Invalid group_by value. Must be one of: {', '.join(valid_group_by)}",
            )

        # Get wellness data
        wellness_records = self.get_wellness(oldest_date, newest_date)

        # Group wellness data based on the specified method
        if group_by == "all":
            grouped = self._group_all_wellness(wellness_records, include_details)
        elif group_by == "week":
            grouped = self._group_wellness_by_period(wellness_records, "week", include_details)
        elif group_by == "month":
            grouped = self._group_wellness_by_period(wellness_records, "month", include_details)
        else:
            grouped = {}

        return grouped

    def _validate_date_format(self, date_str: str, field_name: str):
        """Validate that a date string is in YYYY-MM-DD format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValidationError(field_name, date_str, "Date must be in YYYY-MM-DD format")

    def _group_all_wellness(self, records: List[Dict[str, Any]], include_details: bool) -> Dict[str, Any]:
        """Group all wellness data together for overall statistics."""
        if not records:
            return {
                "summary": {},
                "count": 0,
                "date_range": {"oldest": None, "newest": None},
            }

        # Calculate aggregate statistics
        summary = {
            "avg_weight": self._calculate_average(records, "weight"),
            "avg_restingHR": self._calculate_average(records, "restingHR"),
            "avg_hrv": self._calculate_average(records, "hrv"),
            "avg_sleep_time": self._calculate_average(records, "sleepTime"),
            "avg_sleep_quality": self._calculate_average(records, "sleepQuality"),
            "avg_fatigue": self._calculate_average(records, "fatigue"),
            "avg_mood": self._calculate_average(records, "mood"),
            "avg_motivation": self._calculate_average(records, "motivation"),
            "avg_injury": self._calculate_average(records, "injury"),
            "avg_kcalConsumed": self._calculate_average(records, "kcalConsumed"),
        }

        # Get min/max values for key metrics
        weight_values = [r.get("weight") for r in records if r.get("weight")]
        if weight_values:
            summary["min_weight"] = min(weight_values)
            summary["max_weight"] = max(weight_values)

        hrv_values = [r.get("hrv") for r in records if r.get("hrv")]
        if hrv_values:
            summary["min_hrv"] = min(hrv_values)
            summary["max_hrv"] = max(hrv_values)

        result = {
            "summary": summary,
            "count": len(records),
            "date_range": {
                "oldest": records[-1].get("id") if records else None,
                "newest": records[0].get("id") if records else None,
            },
        }

        if include_details:
            result["records"] = records

        return result

    def _group_wellness_by_period(
        self, records: List[Dict[str, Any]], period: str, include_details: bool
    ) -> Dict[str, Any]:
        """Group wellness data by time period (week or month)."""
        groups = defaultdict(lambda: {"records": [], "summary": {}})

        for record in records:
            date_str = record.get("id", "")  # id is the date in YYYY-MM-DD format
            if not date_str:
                continue

            # Extract the period key
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if period == "week":
                # Get ISO week number
                year, week, _ = date_obj.isocalendar()
                period_key = f"{year}-W{week:02d}"
            elif period == "month":
                period_key = date_obj.strftime("%Y-%m")
            else:
                continue

            groups[period_key]["records"].append(record)

        # Calculate summaries for each group
        for period_key, group_data in groups.items():
            records_in_group = group_data["records"]
            group_data["summary"] = {
                "count": len(records_in_group),
                "avg_weight": self._calculate_average(records_in_group, "weight"),
                "avg_restingHR": self._calculate_average(records_in_group, "restingHR"),
                "avg_hrv": self._calculate_average(records_in_group, "hrv"),
                "avg_sleep_time": self._calculate_average(records_in_group, "sleepTime"),
                "avg_sleep_quality": self._calculate_average(records_in_group, "sleepQuality"),
                "avg_fatigue": self._calculate_average(records_in_group, "fatigue"),
                "avg_mood": self._calculate_average(records_in_group, "mood"),
                "avg_motivation": self._calculate_average(records_in_group, "motivation"),
            }

            # Only keep records if include_details is True
            if not include_details:
                del group_data["records"]

        return {
            "groups": dict(groups),
            "total_records": len(records),
            "period_type": period,
        }

    def _calculate_average(self, records: List[Dict[str, Any]], field: str) -> Optional[float]:
        """Calculate the average of a field across records."""
        values = [r.get(field) for r in records if r.get(field) is not None]
        if not values:
            return None
        return round(sum(values) / len(values), 2)
