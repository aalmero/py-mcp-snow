"""Test basic setup and imports."""

import pytest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src import __version__
from src.config.settings import ServiceNowConfig, ServerConfig
from src.exceptions import ConfigurationError
from src.utils.logging import setup_logging


def test_package_version():
    """Test that package version is accessible."""
    assert __version__ == "0.1.0"


def test_servicenow_config_creation():
    """Test ServiceNow configuration creation."""
    config = ServiceNowConfig(
        instance_url="https://test.service-now.com",
        auth_type="basic",
        username="test",
        password="test"
    )
    assert config.instance_url == "https://test.service-now.com"
    assert config.auth_type == "basic"
    assert config.timeout == 30  # default value


def test_servicenow_config_validation():
    """Test ServiceNow configuration validation."""
    with pytest.raises(ValueError, match="ServiceNow instance URL is required"):
        ServiceNowConfig(
            instance_url="",
            auth_type="basic",
            username="test",
            password="test"
        )


def test_server_config_creation():
    """Test server configuration creation."""
    config = ServerConfig(log_level="DEBUG")
    assert config.log_level == "DEBUG"
    assert config.max_concurrent_requests == 10  # default value


def test_logging_setup():
    """Test logging setup."""
    config = ServerConfig(log_level="INFO")
    logger = setup_logging(config)
    assert logger.name == "src"
    assert logger.level == 20  # INFO level