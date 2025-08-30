from typing import Optional, Dict, Any


class IntervalsError(Exception):
    """Base exception for Intervals-specific errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ):
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ValidationError(IntervalsError):
    """Raised when input validation fails."""

    SENSITIVE_FIELDS = {"password", "token", "api_key", "secret", "auth_token"}

    def __init__(self, field: str, value: Any, message: str):
        self.field = field
        # Redact sensitive values
        if any(sensitive in field.lower() for sensitive in self.SENSITIVE_FIELDS):
            self.value = "<redacted>"
        else:
            self.value = value
        super().__init__(f"Validation failed for {field}", {"message": message})


class NotFoundError(IntervalsError):
    """Raised when a resource is not found."""

    def __init__(self, resource_type: str, resource_id: str):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(f"{resource_type} not found: {resource_id}", status_code=404)


class AuthenticationError(IntervalsError):
    """Raised when authentication fails."""

    pass


class AuthorizationError(IntervalsError):
    """Raised when authorization fails."""

    pass


class NetworkError(IntervalsError):
    """Raised for network-related errors."""

    pass


class RateLimitError(IntervalsError):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        message = "API rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message)


class TimeoutError(IntervalsError):
    """Raised when a request times out."""

    def __init__(self, timeout: int):
        self.timeout = timeout
        super().__init__(f"Request timed out after {timeout} seconds")
