"""Tests for Service Catalog API functionality."""

import pytest
from unittest.mock import Mock, patch
import requests

from src.client.servicenow_client import ServiceNowClient
from src.config.settings import ServiceNowConfig
from src.exceptions import ValidationError, ServiceNowAPIError


class TestCatalogAPI:
    """Test Service Catalog API operations."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock ServiceNow configuration."""
        return ServiceNowConfig(
            instance_url="https://test.service-now.com",
            auth_type="basic",
            username="testuser",
            password="testpass",
            timeout=30,
            retry_count=3
        )
    
    @pytest.fixture
    def client(self, mock_config):
        """Create a ServiceNow client with mocked session."""
        client = ServiceNowClient(mock_config)
        client._authenticated = True
        return client
    
    def test_order_catalog_item_success(self, client):
        """Test successful catalog item ordering."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "request_id": "REQ0001234",
                "request_number": "REQ0001234",
                "sys_id": "abc123def456",
                "state": "1"
            }
        }
        
        with patch.object(client.session, 'request', return_value=mock_response):
            data = {
                "sys_id": "catalog_item_sys_id",
                "sysparm_quantity": "1",
                "sysparm_requested_for": "testuser",
                "variables": {}
            }

            result = client.order_catalog_item(data)
            
            assert result["request_number"] == "REQ0001234"
            assert result["sys_id"] == "abc123def456"
    
    def test_order_catalog_item_empty_sys_id(self, client):
        """Test ordering with empty sys_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            data = {
                "sys_id": "",
                "sysparm_quantity": "1",
                "sysparm_requested_for": "testuser",
                "variables": {}
            }
            client.order_catalog_item(data)
        
        assert "sys_id cannot be empty" in str(exc_info.value)
    
    def test_order_catalog_item_no_variables(self, client):
        """Test ordering without variables."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "request_id": "REQ0001234",
                "request_number": "REQ0001234"
            }
        }
        
        with patch.object(client.session, 'request', return_value=mock_response) as mock_request:
            data = {
                "sys_id": "catalog_item_sys_id",
                "sysparm_quantity": "1",
                "sysparm_requested_for": "testuser",
                "variables": {}
                # No variables provided
            }
            client.order_catalog_item(data)
            
            # Verify the request was made with empty variables
            call_args = mock_request.call_args
            print(call_args)
            assert call_args[1]['json']['variables'] == {}
    
    def test_order_catalog_item_api_error(self, client):
        """Test handling of API errors during catalog item ordering."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {"message": "Invalid catalog item"}
        }
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(ServiceNowAPIError):
                data = {
                    "sys_id": "invalid_sys_id",
                    "sysparm_quantity": "1",
                    "sysparm_requested_for": "testuser",
                    "variables": {}
                }
                client.order_catalog_item(data)
    
    def test_order_catalog_item_unexpected_response(self, client):
        """Test handling of unexpected response format."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "format"}
        
        with patch.object(client.session, 'request', return_value=mock_response):
            with pytest.raises(ServiceNowAPIError) as exc_info:
                data = {
                    "sys_id": "catalog_item_sys_id",
                    "sysparm_quantity": "1",
                    "sysparm_requested_for": "testuser",
                    "variables": {}
                }
                client.order_catalog_item(data)
            
            assert "Unexpected response format" in str(exc_info.value)
