"""Transformer for Intervals.icu activities data."""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utils.logging import get_logger

logger = get_logger(__name__)


class ActivitiesTransformer:
    """Transform Intervals.icu activities data into standardized formats."""

    @staticmethod
    def _remove_nulls(data: Any) -> Any:
        """
        Recursively remove null values and empty arrays from dictionaries and lists.

        Args:
            data: Data structure to clean.

        Returns:
            Cleaned data structure without null values and empty arrays.
        """
        if isinstance(data, dict):
            return {
                k: ActivitiesTransformer._remove_nulls(v)
                for k, v in data.items()
                if v is not None and v != "" and v != []
            }
        elif isinstance(data, list):
            return [ActivitiesTransformer._remove_nulls(item) for item in data if item is not None]
        return data

    @staticmethod
    def transform_activity(activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw activity data into a standardized format.

        Args:
            activity_data: Raw activity data from API.

        Returns:
            Transformed activity data.
        """
        transformed = {
            "id": activity_data.get("id"),
            "name": activity_data.get("name"),
            "type": activity_data.get("type"),
            "start_date": ActivitiesTransformer._parse_datetime(activity_data.get("start_date_local")),
            "moving_time": activity_data.get("moving_time"),
            "elapsed_time": activity_data.get("elapsed_time"),
            "distance": activity_data.get("distance"),
            "elevation_gain": activity_data.get("icu_elevation_gain"),
            "average_speed": activity_data.get("icu_average_speed"),
            "max_speed": activity_data.get("icu_max_speed"),
            "average_cadence": activity_data.get("icu_average_cadence"),
            "average_heartrate": activity_data.get("average_heartrate"),
            "max_heartrate": activity_data.get("max_heartrate"),
            "average_watts": activity_data.get("icu_average_watts"),
            "max_watts": activity_data.get("icu_max_watts"),
            "normalized_power": activity_data.get("icu_normalized_power"),
            "training_load": activity_data.get("icu_training_load"),
            "calories": activity_data.get("calories"),
            "device_name": activity_data.get("device_name"),
            "workout_doc": ActivitiesTransformer._transform_workout_doc(activity_data.get("workout_doc")),
            "intervals": ActivitiesTransformer._transform_intervals(activity_data.get("intervals")),
            "tags": activity_data.get("tags"),
            "description": activity_data.get("description"),
            "athlete_id": activity_data.get("athlete_id"),
            "source": activity_data.get("source"),
            "external_id": activity_data.get("external_id"),
        }

        # Remove all null values from the transformed data
        return ActivitiesTransformer._remove_nulls(transformed)

    @staticmethod
    def transform_activities_list(activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a list of raw activities.

        Args:
            activities: List of raw activity data.

        Returns:
            List of transformed activities.
        """
        return [ActivitiesTransformer.transform_activity(activity) for activity in activities]

    @staticmethod
    def transform_activities_response(activities: List[Dict[str, Any]], include_raw: bool = False) -> Dict[str, Any]:
        """
        Transform activities API response into a standardized format.

        Args:
            activities: List of raw activity data.
            include_raw: Whether to include raw data in response.

        Returns:
            Standardized response with activities and metadata.
        """
        transformed_activities = ActivitiesTransformer.transform_activities_list(activities)

        response = {
            "status": "success",
            "count": len(transformed_activities),
            "activities": transformed_activities,
        }

        if include_raw:
            response["raw_activities"] = activities

        return response

    @staticmethod
    def _parse_datetime(date_str: Any) -> Optional[str]:
        """Parse datetime to ISO format."""
        if not date_str:
            return None

        if isinstance(date_str, str):
            try:
                # Handle various datetime formats
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt.isoformat()
            except (ValueError, AttributeError):
                return date_str

        return str(date_str)

    @staticmethod
    def _transform_workout_doc(workout_doc: Any) -> Optional[Dict[str, Any]]:
        """Transform workout document data."""
        if not workout_doc:
            return None

        if isinstance(workout_doc, dict):
            return {
                "name": workout_doc.get("name"),
                "description": workout_doc.get("description"),
                "target": workout_doc.get("target"),
                "duration": workout_doc.get("duration"),
            }

        return None

    @staticmethod
    def _transform_intervals(intervals: Any) -> Optional[List[Dict[str, Any]]]:
        """Transform intervals data."""
        if not intervals or not isinstance(intervals, list):
            return None

        transformed_intervals = []
        for interval in intervals:
            if isinstance(interval, dict):
                transformed_interval = {
                    "name": interval.get("name"),
                    "type": interval.get("type"),
                    "duration": interval.get("duration"),
                    "distance": interval.get("distance"),
                    "average_power": interval.get("average_power"),
                    "average_heartrate": interval.get("average_heartrate"),
                    "average_cadence": interval.get("average_cadence"),
                }
                # Only add if it has meaningful data
                if any(v for v in transformed_interval.values() if v):
                    transformed_intervals.append(ActivitiesTransformer._remove_nulls(transformed_interval))

        return transformed_intervals if transformed_intervals else None
