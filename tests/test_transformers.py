"""Tests for transformer modules."""

import pytest
from transformers.activities_transformer import ActivitiesTransformer
from transformers.wellness_transformer import WellnessTransformer


def test_activities_transformer_remove_nulls():
    """Test removing null values from activities data."""
    data = {
        "id": "123",
        "name": "Morning Run",
        "empty": None,
        "blank": "",
        "empty_list": [],
        "nested": {
            "value": 1,
            "null": None
        }
    }
    
    cleaned = ActivitiesTransformer._remove_nulls(data)
    assert "empty" not in cleaned
    assert "blank" not in cleaned
    assert "empty_list" not in cleaned
    assert "null" not in cleaned["nested"]
    assert cleaned["nested"]["value"] == 1


def test_transform_activity(sample_activity_data):
    """Test transforming activity data."""
    activity = sample_activity_data[0]
    transformed = ActivitiesTransformer.transform_activity(activity)
    
    assert transformed["id"] == "123"
    assert transformed["name"] == "Morning Run"
    assert transformed["type"] == "Run"
    assert transformed["distance"] == 10000
    assert transformed["elevation_gain"] == 150
    assert transformed["average_heartrate"] == 145


def test_transform_activities_list(sample_activity_data):
    """Test transforming list of activities."""
    transformed = ActivitiesTransformer.transform_activities_list(sample_activity_data)
    assert len(transformed) == 2
    assert transformed[0]["name"] == "Morning Run"
    assert transformed[1]["name"] == "Evening Ride"


def test_wellness_transformer_remove_nulls():
    """Test removing null values from wellness data."""
    data = {
        "id": "2024-01-15",
        "weight": 70.5,
        "empty": None,
        "blank": "",
        "empty_list": []
    }
    
    cleaned = WellnessTransformer._remove_nulls(data)
    assert "empty" not in cleaned
    assert "blank" not in cleaned
    assert "empty_list" not in cleaned


def test_transform_wellness_record(sample_wellness_data):
    """Test transforming wellness record."""
    record = sample_wellness_data[0]
    transformed = WellnessTransformer.transform_wellness_record(record)
    
    assert transformed["date"] == "2024-01-15"
    assert transformed["weight"] == 70.5
    assert transformed["resting_hr"] == 55
    assert transformed["hrv"] == 45
    assert transformed["sleep_time"] == 7.5


def test_transform_wellness_list(sample_wellness_data):
    """Test transforming list of wellness records."""
    transformed = WellnessTransformer.transform_wellness_list(sample_wellness_data)
    assert len(transformed) == 2
    assert transformed[0]["date"] == "2024-01-15"
    assert transformed[1]["date"] == "2024-01-14"


def test_wellness_summary(sample_wellness_data):
    """Test creating wellness summary."""
    summary = WellnessTransformer.transform_wellness_summary(sample_wellness_data)
    
    assert summary["status"] == "success"
    assert summary["count"] == 2
    assert "weight" in summary["summary"]
    assert summary["summary"]["weight"]["average"] == 70.4
    assert summary["summary"]["weight"]["min"] == 70.3
    assert summary["summary"]["weight"]["max"] == 70.5