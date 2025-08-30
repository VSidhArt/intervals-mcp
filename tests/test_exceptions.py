"""Tests for exception module."""

import pytest
from exceptions import (
    IntervalsError,
    ValidationError,
    NotFoundError,
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    RateLimitError,
    TimeoutError
)


def test_intervals_error():
    """Test base IntervalsError."""
    error = IntervalsError("Test error", details={"key": "value"}, status_code=400)
    assert str(error) == "Test error (Details: {'key': 'value'})"
    assert error.status_code == 400
    assert error.details == {"key": "value"}
    
    error_no_details = IntervalsError("Simple error")
    assert str(error_no_details) == "Simple error"


def test_validation_error():
    """Test ValidationError with sensitive field redaction."""
    # Non-sensitive field
    error = ValidationError("username", "john", "Invalid format")
    assert error.field == "username"
    assert error.value == "john"
    
    # Sensitive field - should be redacted
    error = ValidationError("api_key", "secret123", "Invalid format")
    assert error.field == "api_key"
    assert error.value == "<redacted>"
    
    error = ValidationError("password", "pass123", "Too short")
    assert error.value == "<redacted>"


def test_not_found_error():
    """Test NotFoundError."""
    error = NotFoundError("Activity", "123")
    assert error.resource_type == "Activity"
    assert error.resource_id == "123"
    assert error.status_code == 404
    assert "Activity not found: 123" in str(error)


def test_authentication_error():
    """Test AuthenticationError."""
    error = AuthenticationError("Invalid credentials")
    assert str(error) == "Invalid credentials"


def test_authorization_error():
    """Test AuthorizationError."""
    error = AuthorizationError("Access denied")
    assert str(error) == "Access denied"


def test_network_error():
    """Test NetworkError."""
    error = NetworkError("Connection failed")
    assert str(error) == "Connection failed"


def test_rate_limit_error():
    """Test RateLimitError."""
    error = RateLimitError()
    assert str(error) == "API rate limit exceeded"
    
    error_with_retry = RateLimitError(retry_after=60)
    assert error_with_retry.retry_after == 60
    assert "Retry after 60 seconds" in str(error_with_retry)


def test_timeout_error():
    """Test TimeoutError."""
    error = TimeoutError(30)
    assert error.timeout == 30
    assert "Request timed out after 30 seconds" in str(error)