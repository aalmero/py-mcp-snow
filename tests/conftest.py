"""Pytest configuration and fixtures for ServiceNow MCP Server tests."""

import pytest
import os
from unittest.mock import patch

from src.config.settings import ServiceNowConfig, ServerConfig


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "SERVICENOW_INSTANCE_URL": "https://test-instance.service-now.com",
        "SERVICENOW_USERNAME": "test_user",
        "SERVICENOW_PASSWORD": "test_password",
        "SERVICENOW_TIMEOUT": "30",
        "SERVICENOW_RETRY_COUNT": "3",
        "LOG_LEVEL": "DEBUG",
        "MAX_CONCURRENT_REQUESTS": "5"
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        yield env_vars


@pytest.fixture
def sample_servicenow_config():
    """Sample ServiceNow configuration for testing."""
    return ServiceNowConfig(
        instance_url="https://test-instance.service-now.com",
        auth_type="basic",
        username="test_user",
        password="test_password",
        timeout=30,
        retry_count=3
    )


@pytest.fixture
def sample_server_config():
    """Sample server configuration for testing."""
    return ServerConfig(
        log_level="DEBUG",
        log_format="%(levelname)s - %(message)s",
        max_concurrent_requests=5
    )