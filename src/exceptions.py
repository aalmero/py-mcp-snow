"""Custom exceptions for ServiceNow MCP Server."""

from typing import Optional, Dict, Any


class ServiceNowMCPError(Exception):
    """Base exception for ServiceNow MCP Server errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize ServiceNow MCP error.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class ConfigurationError(ServiceNowMCPError):
    """Raised when there are configuration-related errors."""
    
    def __init__(self, message: str, missing_config: Optional[str] = None):
        """Initialize configuration error.
        
        Args:
            message: Error message
            missing_config: Name of missing configuration parameter
        """
        super().__init__(message, error_code="CONFIGURATION_ERROR")
        self.missing_config = missing_config


class AuthenticationError(ServiceNowMCPError):
    """Raised when authentication with ServiceNow fails."""
    
    def __init__(self, message: str, auth_type: Optional[str] = None):
        """Initialize authentication error.
        
        Args:
            message: Error message
            auth_type: Type of authentication that failed
        """
        super().__init__(message, error_code="AUTHENTICATION_ERROR")
        self.auth_type = auth_type


class ServiceNowAPIError(ServiceNowMCPError):
    """Raised when ServiceNow API returns an error."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        """Initialize ServiceNow API error.
        
        Args:
            message: Error message
            status_code: HTTP status code from ServiceNow
            response_data: Response data from ServiceNow API
        """
        super().__init__(message, error_code="SERVICENOW_API_ERROR")
        self.status_code = status_code
        self.response_data = response_data or {}


class ValidationError(ServiceNowMCPError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field_name: Optional[str] = None, invalid_value: Optional[Any] = None):
        """Initialize validation error.
        
        Args:
            message: Error message
            field_name: Name of the field that failed validation
            invalid_value: The invalid value that caused the error
        """
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field_name = field_name
        self.invalid_value = invalid_value


class ConnectionError(ServiceNowMCPError):
    """Raised when connection to ServiceNow fails."""
    
    def __init__(self, message: str, instance_url: Optional[str] = None):
        """Initialize connection error.
        
        Args:
            message: Error message
            instance_url: ServiceNow instance URL that failed to connect
        """
        super().__init__(message, error_code="CONNECTION_ERROR")
        self.instance_url = instance_url


class RateLimitError(ServiceNowMCPError):
    """Raised when ServiceNow API rate limits are exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        """Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Number of seconds to wait before retrying
        """
        super().__init__(message, error_code="RATE_LIMIT_ERROR")
        self.retry_after = retry_after


class ResourceNotFoundError(ServiceNowMCPError):
    """Raised when a requested ServiceNow resource is not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        """Initialize resource not found error.
        
        Args:
            message: Error message
            resource_type: Type of resource that was not found
            resource_id: ID of the resource that was not found
        """
        super().__init__(message, error_code="RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id


def format_error_response(error: ServiceNowMCPError) -> Dict[str, Any]:
    """Format an error for MCP response.
    
    Args:
        error: ServiceNow MCP error to format
        
    Returns:
        Dict containing formatted error information
    """
    return {
        "success": False,
        "error": error.message,
        "error_code": error.error_code,
        "details": error.details
    }