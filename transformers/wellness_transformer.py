"""Transformer for Intervals.icu wellness data."""

from typing import Dict, Any, List
from utils.logging import get_logger

logger = get_logger(__name__)


class WellnessTransformer:
    """Transform Intervals.icu wellness data into standardized formats."""

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
                k: WellnessTransformer._remove_nulls(v)
                for k, v in data.items()
                if v is not None and v != "" and v != []
            }
        elif isinstance(data, list):
            return [WellnessTransformer._remove_nulls(item) for item in data if item is not None]
        return data

    @staticmethod
    def transform_wellness_record(wellness_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform raw wellness data into a standardized format.

        Args:
            wellness_data: Raw wellness data from API.

        Returns:
            Transformed wellness data.
        """
        transformed = {
            "date": wellness_data.get("id"),  # id is the date in YYYY-MM-DD format
            "weight": wellness_data.get("weight"),
            "weight_unit": "kg" if wellness_data.get("weight") else None,
            "resting_hr": wellness_data.get("restingHR"),
            "hrv": wellness_data.get("hrv"),
            "hrv_sdnn": wellness_data.get("hrvSDNN"),
            "sleep_time": wellness_data.get("sleepTime"),
            "sleep_quality": wellness_data.get("sleepQuality"),
            "atl": wellness_data.get("atl"),
            "ctl": wellness_data.get("ctl"),
            "tsb": wellness_data.get("tsb"),
            "rampRate": wellness_data.get("rampRate"),
            "fatigue": wellness_data.get("fatigue"),
            "mood": wellness_data.get("mood"),
            "motivation": wellness_data.get("motivation"),
            "injury": wellness_data.get("injury"),
            "spO2": wellness_data.get("spO2"),
            "systolic": wellness_data.get("systolic"),
            "diastolic": wellness_data.get("diastolic"),
            "calories_consumed": wellness_data.get("kcalConsumed"),
            "bodyFat": wellness_data.get("bodyFat"),
            "abdomen": wellness_data.get("abdomen"),
            "vo2max": wellness_data.get("vo2max"),
            "comments": wellness_data.get("comments"),
            "athlete_id": wellness_data.get("athlete_id"),
        }

        # Remove all null values from the transformed data
        return WellnessTransformer._remove_nulls(transformed)

    @staticmethod
    def transform_wellness_list(wellness_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a list of raw wellness records.

        Args:
            wellness_records: List of raw wellness data.

        Returns:
            List of transformed wellness records.
        """
        return [WellnessTransformer.transform_wellness_record(record) for record in wellness_records]

    @staticmethod
    def transform_wellness_response(
        wellness_records: List[Dict[str, Any]], include_raw: bool = False
    ) -> Dict[str, Any]:
        """
        Transform wellness API response into a standardized format.

        Args:
            wellness_records: List of raw wellness data.
            include_raw: Whether to include raw data in response.

        Returns:
            Standardized response with wellness records and metadata.
        """
        transformed_records = WellnessTransformer.transform_wellness_list(wellness_records)

        response = {
            "status": "success",
            "count": len(transformed_records),
            "wellness": transformed_records,
        }

        if include_raw:
            response["raw_wellness"] = wellness_records

        # Add date range if records exist
        if transformed_records:
            response["date_range"] = {
                "oldest": transformed_records[-1].get("date"),
                "newest": transformed_records[0].get("date"),
            }

        return response

    @staticmethod
    def transform_wellness_summary(wellness_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a summary of wellness metrics.

        Args:
            wellness_records: List of raw wellness data.

        Returns:
            Summary statistics of wellness metrics.
        """
        if not wellness_records:
            return {"status": "success", "summary": {}, "count": 0}

        # Calculate averages and ranges for key metrics
        summary = {}

        # Weight metrics
        weight_values = [r.get("weight") for r in wellness_records if r.get("weight")]
        if weight_values:
            summary["weight"] = {
                "average": round(sum(weight_values) / len(weight_values), 2),
                "min": min(weight_values),
                "max": max(weight_values),
                "count": len(weight_values),
            }

        # HRV metrics
        hrv_values = [r.get("hrv") for r in wellness_records if r.get("hrv")]
        if hrv_values:
            summary["hrv"] = {
                "average": round(sum(hrv_values) / len(hrv_values), 2),
                "min": min(hrv_values),
                "max": max(hrv_values),
                "count": len(hrv_values),
            }

        # Resting HR metrics
        hr_values = [r.get("restingHR") for r in wellness_records if r.get("restingHR")]
        if hr_values:
            summary["resting_hr"] = {
                "average": round(sum(hr_values) / len(hr_values), 2),
                "min": min(hr_values),
                "max": max(hr_values),
                "count": len(hr_values),
            }

        # Sleep metrics
        sleep_values = [r.get("sleepTime") for r in wellness_records if r.get("sleepTime")]
        if sleep_values:
            summary["sleep_time"] = {
                "average": round(sum(sleep_values) / len(sleep_values), 2),
                "min": min(sleep_values),
                "max": max(sleep_values),
                "count": len(sleep_values),
            }

        # Sleep quality metrics
        quality_values = [r.get("sleepQuality") for r in wellness_records if r.get("sleepQuality")]
        if quality_values:
            summary["sleep_quality"] = {
                "average": round(sum(quality_values) / len(quality_values), 2),
                "min": min(quality_values),
                "max": max(quality_values),
                "count": len(quality_values),
            }

        # Training metrics
        atl_values = [r.get("atl") for r in wellness_records if r.get("atl")]
        if atl_values:
            summary["atl"] = {
                "average": round(sum(atl_values) / len(atl_values), 2),
                "min": min(atl_values),
                "max": max(atl_values),
                "count": len(atl_values),
            }

        ctl_values = [r.get("ctl") for r in wellness_records if r.get("ctl")]
        if ctl_values:
            summary["ctl"] = {
                "average": round(sum(ctl_values) / len(ctl_values), 2),
                "min": min(ctl_values),
                "max": max(ctl_values),
                "count": len(ctl_values),
            }

        tsb_values = [r.get("tsb") for r in wellness_records if r.get("tsb")]
        if tsb_values:
            summary["tsb"] = {
                "average": round(sum(tsb_values) / len(tsb_values), 2),
                "min": min(tsb_values),
                "max": max(tsb_values),
                "count": len(tsb_values),
            }

        return {
            "status": "success",
            "summary": summary,
            "count": len(wellness_records),
            "date_range": {
                "oldest": wellness_records[-1].get("id") if wellness_records else None,
                "newest": wellness_records[0].get("id") if wellness_records else None,
            },
        }
