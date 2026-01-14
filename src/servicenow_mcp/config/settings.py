"""Configuration management for ServiceNow MCP Server."""

import os
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ServiceNowCredentials(BaseModel):
    """Secure representation of ServiceNow authentication data."""
    
    instance_url: str = Field(..., description="ServiceNow instance URL")
    auth_type: Literal["basic", "api_key", "oauth"] = Field(..., description="Authentication type")
    username: Optional[str] = Field(None, description="Username for basic authentication")
    password: Optional[str] = Field(None, description="Password for basic authentication")
    api_key: Optional[str] = Field(None, description="API key for key-based authentication")
    timeout: int = Field(30, gt=0, description="API request timeout in seconds")
    retry_count: int = Field(3, ge=0, description="Number of retry attempts")
    
    @field_validator('instance_url')
    @classmethod
    def validate_instance_url(cls, v):
        """Validate ServiceNow instance URL format."""
        if not v:
            raise ValueError("ServiceNow instance URL is required")
        if not v.startswith(('http://', 'https://')):
            raise ValueError("ServiceNow instance URL must start with http:// or https://")
        return v.rstrip('/')  # Remove trailing slash for consistency
    
    @model_validator(mode='after')
    def validate_auth_credentials(self):
        """Validate authentication credentials based on auth type."""
        if self.auth_type == "basic":
            if not self.username or not self.password:
                raise ValueError("Username and password are required for basic authentication")
        elif self.auth_type == "api_key":
            if not self.api_key:
                raise ValueError("API key is required for API key authentication")
        elif self.auth_type == "oauth":
            # OAuth validation will be implemented in future enhancement
            raise ValueError("OAuth authentication is not yet supported")
        
        return self
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"


class ServiceNowConfig(ServiceNowCredentials):
    """Configuration for ServiceNow connection and authentication.
    
    Extends ServiceNowCredentials with additional configuration options.
    """
    pass


class ServerConfig(BaseModel):
    """Configuration for the MCP server itself."""
    
    log_level: str = Field("INFO", description="Logging level")
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    max_concurrent_requests: int = Field(10, gt=0, description="Maximum concurrent requests")
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level is supported."""
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_log_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_log_levels}")
        return v.upper()
    
    class Config:
        """Pydantic configuration."""
        validate_assignment = True
        extra = "forbid"


def load_servicenow_config() -> ServiceNowConfig:
    """Load ServiceNow configuration from environment variables.
    
    Returns:
        ServiceNowConfig: Configured ServiceNow settings
        
    Raises:
        ConfigurationError: If required configuration is missing or invalid
    """
    from ..exceptions import ConfigurationError
    
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    if not instance_url:
        raise ConfigurationError(
            "SERVICENOW_INSTANCE_URL environment variable is required. "
            "Set it to your ServiceNow instance URL (e.g., https://your-instance.service-now.com)",
            missing_config="SERVICENOW_INSTANCE_URL"
        )
    
    # Determine authentication type based on available credentials
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")
    api_key = os.getenv("SERVICENOW_API_KEY")
    
    if api_key:
        auth_type = "api_key"
    elif username and password:
        auth_type = "basic"
    else:
        raise ConfigurationError(
            "Authentication credentials are required. "
            "Set either SERVICENOW_API_KEY or both SERVICENOW_USERNAME and SERVICENOW_PASSWORD",
            missing_config="SERVICENOW_CREDENTIALS"
        )
    
    # Load optional configuration with defaults
    try:
        timeout = int(os.getenv("SERVICENOW_TIMEOUT", "30"))
        retry_count = int(os.getenv("SERVICENOW_RETRY_COUNT", "3"))
    except ValueError as e:
        raise ConfigurationError(f"Invalid numeric configuration value: {e}")
    
    try:
        return ServiceNowConfig(
            instance_url=instance_url,
            auth_type=auth_type,
            username=username,
            password=password,
            api_key=api_key,
            timeout=timeout,
            retry_count=retry_count
        )
    except ValueError as e:
        raise ConfigurationError(f"Configuration validation failed: {e}")


def load_server_config() -> ServerConfig:
    """Load server configuration from environment variables.
    
    Returns:
        ServerConfig: Configured server settings
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    from ..exceptions import ConfigurationError
    
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_format = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    try:
        max_concurrent_requests = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    except ValueError as e:
        raise ConfigurationError(f"Invalid MAX_CONCURRENT_REQUESTS value: {e}")
    
    try:
        return ServerConfig(
            log_level=log_level,
            log_format=log_format,
            max_concurrent_requests=max_concurrent_requests
        )
    except ValueError as e:
        raise ConfigurationError(f"Server configuration validation failed: {e}")