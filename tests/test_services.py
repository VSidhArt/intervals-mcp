"""Tests for service modules."""

import pytest
from unittest.mock import Mock, patch
from services.activities_service import ActivitiesService
from services.wellness_service import WellnessService
from exceptions import ValidationError


def test_activities_service_date_validation():
    """Test date validation in activities service."""
    service = ActivitiesService(Mock())
    
    # Valid date
    service._validate_date_format("2024-01-15", "test_date")
    
    # Invalid date format
    with pytest.raises(ValidationError, match="Date must be in YYYY-MM-DD format"):
        service._validate_date_format("01/15/2024", "test_date")
    
    # Invalid date
    with pytest.raises(ValidationError, match="Date must be in YYYY-MM-DD format"):
        service._validate_date_format("2024-13-45", "test_date")


def test_activities_service_get_activities(mock_api_client, sample_activity_data):
    """Test getting activities."""
    mock_api_client.get.return_value = sample_activity_data
    mock_api_client.athlete_id = "i123456"
    
    service = ActivitiesService(mock_api_client)
    activities = service.get_activities("2024-01-01", "2024-01-31")
    
    assert len(activities) == 2
    assert activities[0]["id"] == "123"
    mock_api_client.get.assert_called_once_with(
        "/athlete/i123456/activities",
        params={"oldest": "2024-01-01", "newest": "2024-01-31"}
    )


def test_activities_group_by_sport(sample_activity_data):
    """Test grouping activities by sport."""
    service = ActivitiesService(Mock())
    grouped = service._group_by_sport(sample_activity_data, include_details=False)
    
    assert "groups" in grouped
    assert "Run" in grouped["groups"]
    assert "Ride" in grouped["groups"]
    assert grouped["groups"]["Run"]["count"] == 1
    assert grouped["groups"]["Ride"]["count"] == 1
    assert grouped["total_activities"] == 2


def test_wellness_service_date_validation():
    """Test date validation in wellness service."""
    service = WellnessService(Mock())
    
    # Valid date
    service._validate_date_format("2024-01-15", "test_date")
    
    # Invalid date format
    with pytest.raises(ValidationError, match="Date must be in YYYY-MM-DD format"):
        service._validate_date_format("invalid", "test_date")


def test_wellness_service_get_wellness(mock_api_client, sample_wellness_data):
    """Test getting wellness data."""
    mock_api_client.get.return_value = sample_wellness_data
    mock_api_client.athlete_id = "i123456"
    
    service = WellnessService(mock_api_client)
    wellness = service.get_wellness("2024-01-01", "2024-01-31")
    
    assert len(wellness) == 2
    assert wellness[0]["id"] == "2024-01-15"
    mock_api_client.get.assert_called_once_with(
        "/athlete/i123456/wellness",
        params={"oldest": "2024-01-01", "newest": "2024-01-31"}
    )


def test_wellness_calculate_average(sample_wellness_data):
    """Test calculating averages."""
    service = WellnessService(Mock())
    
    avg = service._calculate_average(sample_wellness_data, "weight")
    assert avg == 70.4
    
    avg = service._calculate_average(sample_wellness_data, "restingHR")
    assert avg == 55.5
    
    # Field that doesn't exist
    avg = service._calculate_average(sample_wellness_data, "nonexistent")
    assert avg is None