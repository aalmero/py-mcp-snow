"""Tests for ServiceNow client operations."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from src.client.servicenow_client import ServiceNowClient
from src.config.settings import ServiceNowConfig
from src.exceptions import (
    AuthenticationError,
    ServiceNowAPIError,
    ConnectionError,
    ValidationError,
    ResourceNotFoundError,
    RateLimitError
)


@pytest.fixture
def mock_servicenow_config():
    """Mock ServiceNow configuration for testing."""
    return ServiceNowConfig(
        instance_url="https://test-instance.service-now.com",
        auth_type="basic",
        username="test_user",
        password="test_password",
        timeout=30,
        retry_count=3
    )


@pytest.fixture
def servicenow_client(mock_servicenow_config):
    """ServiceNow client instance for testing."""
    return ServiceNowClient(mock_servicenow_config)


class TestServiceNowClientAuthentication:
    """Test ServiceNow client authentication functionality."""
    
    @patch('requests.Session.get')
    def test_authenticate_basic_success(self, mock_get, servicenow_client):
        """Test successful basic authentication."""
        # Mock successful validation response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": [{"sys_id": "test"}]}
        mock_get.return_value = mock_response
        
        result = servicenow_client.authenticate()
        
        assert result is True
        assert servicenow_client.is_authenticated() is True
        assert servicenow_client.session.auth is not None
    
    @patch('requests.Session.get')
    def test_authenticate_invalid_credentials(self, mock_get, servicenow_client):
        """Test authentication with invalid credentials."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            servicenow_client.authenticate()
    
    @patch('requests.Session.get')
    def test_authenticate_connection_error(self, mock_get, servicenow_client):
        """Test authentication with connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        with pytest.raises(ConnectionError, match="Failed to validate connection"):
            servicenow_client.authenticate()


class TestServiceNowClientOperations:
    """Test ServiceNow client CRUD operations."""
    
    def setup_method(self):
        """Set up authenticated client for each test."""
        self.config = ServiceNowConfig(
            instance_url="https://test-instance.service-now.com",
            auth_type="basic",
            username="test_user",
            password="test_password"
        )
        self.client = ServiceNowClient(self.config)
        # Mock authentication
        self.client._authenticated = True
    
    @patch('requests.Session.request')
    def test_create_request_success(self, mock_request):
        """Test successful Service Request creation."""
        # Mock successful creation response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "result": {
                "sys_id": "test-sys-id",
                "number": "REQ0001234",
                "short_description": "Test request"
            }
        }
        mock_request.return_value = mock_response
        
        data = {"short_description": "Test request"}
        result = self.client.create_request(data)
        
        assert result["sys_id"] == "test-sys-id"
        assert result["number"] == "REQ0001234"
        mock_request.assert_called_once()
    
    def test_create_request_missing_description(self):
        """Test Service Request creation with missing required field."""
        data = {}  # Missing short_description
        
        with pytest.raises(ValidationError, match="short_description is required"):
            self.client.create_request(data)
    
    @patch('requests.Session.request')
    def test_get_request_by_sys_id_success(self, mock_request):
        """Test successful Service Request retrieval by sys_id."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "sys_id": "test-sys-id",
                "number": "REQ0001234",
                "short_description": "Test request"
            }
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_request("test-sys-id", "sys_id")
        
        assert result["sys_id"] == "test-sys-id"
        assert result["number"] == "REQ0001234"
    
    @patch('requests.Session.request')
    def test_get_request_by_number_success(self, mock_request):
        """Test successful Service Request retrieval by number."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{
                "sys_id": "test-sys-id",
                "number": "REQ0001234",
                "short_description": "Test request"
            }]
        }
        mock_request.return_value = mock_response
        
        result = self.client.get_request("REQ0001234", "number")
        
        assert result["sys_id"] == "test-sys-id"
        assert result["number"] == "REQ0001234"
    
    @patch('requests.Session.request')
    def test_get_request_not_found(self, mock_request):
        """Test Service Request retrieval when request not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": []}
        mock_request.return_value = mock_response
        
        with pytest.raises(ResourceNotFoundError, match="not found"):
            self.client.get_request("NONEXISTENT", "number")
    
    def test_get_request_invalid_identifier(self):
        """Test Service Request retrieval with invalid identifier."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            self.client.get_request("", "sys_id")
    
    @patch('requests.Session.request')
    def test_update_request_success(self, mock_request):
        """Test successful Service Request update."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "sys_id": "test-sys-id",
                "state": "2",
                "priority": "1"
            }
        }
        mock_request.return_value = mock_response
        
        data = {"state": "2", "priority": "1"}
        result = self.client.update_request("test-sys-id", data)
        
        assert result["state"] == "2"
        assert result["priority"] == "1"
    
    def test_update_request_invalid_sys_id(self):
        """Test Service Request update with invalid sys_id."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            self.client.update_request("", {"state": "2"})
    
    @patch('requests.Session.request')
    def test_search_requests_success(self, mock_request):
        """Test successful Service Request search."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [
                {"sys_id": "test-1", "state": "1"},
                {"sys_id": "test-2", "state": "1"}
            ]
        }
        mock_request.return_value = mock_response
        
        filters = {"status": "1", "requested_for": "user123"}
        result = self.client.search_requests(filters)
        
        assert len(result) == 2
        assert result[0]["sys_id"] == "test-1"
    
    @patch('requests.Session.request')
    def test_search_requests_empty_result(self, mock_request):
        """Test Service Request search with no results."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": []}
        mock_request.return_value = mock_response
        
        filters = {"status": "999"}
        result = self.client.search_requests(filters)
        
        assert result == []
    
    @patch('requests.Session.request')
    def test_search_requests_multiple_criteria(self, mock_request):
        """Test Service Request search with multiple criteria (AND logic)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"sys_id": "test-1", "state": "2", "requested_for": "user123"}]
        }
        mock_request.return_value = mock_response
        
        filters = {
            "status": "2",
            "requested_for": "user123",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31"
        }
        result = self.client.search_requests(filters)
        
        # Verify the query was built correctly with AND logic
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        params = call_args[1]['params']
        
        # Should contain all criteria joined with ^
        expected_query_parts = [
            "state=2",
            "requested_for=user123", 
            "opened_at>=2024-01-01",
            "opened_at<=2024-12-31"
        ]
        expected_query = "^".join(expected_query_parts)
        assert params['sysparm_query'] == expected_query
        
        assert len(result) == 1
        assert result[0]["sys_id"] == "test-1"
    
    @patch('requests.Session.request')
    def test_search_requests_by_status(self, mock_request):
        """Test Service Request search by status only."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [
                {"sys_id": "test-1", "state": "1"},
                {"sys_id": "test-2", "state": "1"}
            ]
        }
        mock_request.return_value = mock_response
        
        filters = {"status": "1"}
        result = self.client.search_requests(filters)
        
        # Verify query contains only status filter
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert params['sysparm_query'] == "state=1"
        
        assert len(result) == 2
    
    @patch('requests.Session.request')
    def test_search_requests_by_user(self, mock_request):
        """Test Service Request search by requested_for user."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"sys_id": "test-1", "requested_for": "user123"}]
        }
        mock_request.return_value = mock_response
        
        filters = {"requested_for": "user123"}
        result = self.client.search_requests(filters)
        
        # Verify query contains user filter
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert params['sysparm_query'] == "requested_for=user123"
        
        assert len(result) == 1
    
    @patch('requests.Session.request')
    def test_search_requests_by_date_range(self, mock_request):
        """Test Service Request search by date range."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"sys_id": "test-1", "opened_at": "2024-06-15 10:00:00"}]
        }
        mock_request.return_value = mock_response
        
        filters = {
            "date_from": "2024-01-01",
            "date_to": "2024-12-31"
        }
        result = self.client.search_requests(filters)
        
        # Verify query contains date filters
        call_args = mock_request.call_args
        params = call_args[1]['params']
        expected_query = "opened_at>=2024-01-01^opened_at<=2024-12-31"
        assert params['sysparm_query'] == expected_query
        
        assert len(result) == 1
    
    @patch('requests.Session.request')
    def test_search_requests_with_pagination(self, mock_request):
        """Test Service Request search with pagination parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{"sys_id": "test-1"}]
        }
        mock_request.return_value = mock_response
        
        filters = {
            "status": "1",
            "limit": 10,
            "offset": 20
        }
        result = self.client.search_requests(filters)
        
        # Verify pagination parameters
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert params['sysparm_limit'] == 10
        assert params['sysparm_offset'] == 20
        
        assert len(result) == 1
    
    @patch('requests.Session.request')
    def test_search_requests_no_filters(self, mock_request):
        """Test Service Request search with no filters (returns all)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [
                {"sys_id": "test-1"},
                {"sys_id": "test-2"},
                {"sys_id": "test-3"}
            ]
        }
        mock_request.return_value = mock_response
        
        filters = {}
        result = self.client.search_requests(filters)
        
        # Verify no query parameter when no filters
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert 'sysparm_query' not in params
        
        assert len(result) == 3
    
    @patch('requests.Session.request')
    def test_search_requests_empty_filter_values(self, mock_request):
        """Test Service Request search ignores empty filter values."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": []}
        mock_request.return_value = mock_response
        
        filters = {
            "status": "",  # Empty string should be ignored
            "requested_for": None,  # None should be ignored
            "date_from": "   ",  # Whitespace should be ignored
            "limit": 5
        }
        result = self.client.search_requests(filters)
        
        # Verify no query parameter when all filters are empty
        call_args = mock_request.call_args
        params = call_args[1]['params']
        assert 'sysparm_query' not in params
        assert params['sysparm_limit'] == 5
        
        assert result == []
    
    def test_search_requests_invalid_filters_type(self):
        """Test Service Request search with invalid filters type."""
        with pytest.raises(ValidationError, match="Filters must be a dictionary"):
            self.client.search_requests("invalid")
    
    def test_search_requests_invalid_limit(self):
        """Test Service Request search with invalid limit value."""
        filters = {"limit": "invalid"}
        with pytest.raises(ValidationError, match="Limit must be a valid integer"):
            self.client.search_requests(filters)
        
        filters = {"limit": -1}
        with pytest.raises(ValidationError, match="Limit must be non-negative"):
            self.client.search_requests(filters)
    
    def test_search_requests_invalid_offset(self):
        """Test Service Request search with invalid offset value."""
        filters = {"offset": "invalid"}
        with pytest.raises(ValidationError, match="Offset must be a valid integer"):
            self.client.search_requests(filters)
        
        filters = {"offset": -1}
        with pytest.raises(ValidationError, match="Offset must be non-negative"):
            self.client.search_requests(filters)


class TestServiceNowClientErrorHandling:
    """Test ServiceNow client error handling."""
    
    def setup_method(self):
        """Set up authenticated client for each test."""
        self.config = ServiceNowConfig(
            instance_url="https://test-instance.service-now.com",
            auth_type="basic",
            username="test_user",
            password="test_password"
        )
        self.client = ServiceNowClient(self.config)
        self.client._authenticated = True
    
    def test_unauthenticated_request(self):
        """Test making request without authentication."""
        self.client._authenticated = False
        
        with pytest.raises(AuthenticationError, match="not authenticated"):
            self.client.create_request({"short_description": "test"})
    
    @patch('requests.Session.request')
    def test_handle_404_error(self, mock_request):
        """Test handling of 404 errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.url = "https://test.com/api/resource"
        mock_response.json.return_value = {"error": {"message": "Not found"}}
        mock_request.return_value = mock_response
        
        with pytest.raises(ResourceNotFoundError, match="Resource not found"):
            self.client.get_request("nonexistent", "sys_id")
    
    @patch('requests.Session.request')
    def test_handle_rate_limit_error(self, mock_request):
        """Test handling of rate limit errors."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"error": {"message": "Rate limited"}}
        mock_request.return_value = mock_response
        
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            self.client.create_request({"short_description": "test"})
    
    @patch('requests.Session.request')
    def test_handle_connection_timeout(self, mock_request):
        """Test handling of connection timeouts."""
        mock_request.side_effect = requests.exceptions.Timeout("Request timeout")
        
        with pytest.raises(ConnectionError, match="Request timeout"):
            self.client.create_request({"short_description": "test"})

class TestServiceNowClientCatalogItems:
    """Test ServiceNow client catalog items functionality."""

    def setup_method(self):
        """Set up authenticated client for each test."""
        self.config = ServiceNowConfig(
            instance_url="https://test-instance.service-now.com",
            auth_type="basic",
            username="test_user",
            password="test_password"
        )
        self.client = ServiceNowClient(self.config)
        self.client._authenticated = True

    @patch('requests.Session.request')
    def test_get_catalog_items_success(self, mock_request):
        """Test successful catalog items retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [
                {
                    "sys_id": "item1",
                    "name": "Test Item 1",
                    "short_description": "Test catalog item 1"
                },
                {
                    "sys_id": "item2",
                    "name": "Test Item 2",
                    "short_description": "Test catalog item 2"
                }
            ]
        }
        mock_request.return_value = mock_response

        params = {
            "sysparm_catalog": "catalog123",
            "sysparm_limit": 10,
            "sysparm_text": "test"
        }

        result = self.client.get_catalog_items(params)

        assert len(result) == 2
        assert result[0]["sys_id"] == "item1"
        assert result[1]["name"] == "Test Item 2"

        # Verify the request was made
        mock_request.assert_called_once()

class TestServiceNowClientGetUser:
    """Test ServiceNow client get_user functionality."""

    def setup_method(self):
        """Set up authenticated client for each test."""
        self.config = ServiceNowConfig(
            instance_url="https://test-instance.service-now.com",
            auth_type="basic",
            username="test_user",
            password="test_password"
        )
        self.client = ServiceNowClient(self.config)
        self.client._authenticated = True

    @patch('requests.Session.request')
    def test_get_user_by_sys_id_success(self, mock_request):
        """Test successful user retrieval by sys_id."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "sys_id": "user-sys-id",
                "user_name": "testuser",
                "email": "testuser@example.com"
            }
        }
        mock_request.return_value = mock_response
        result = self.client.get_user("user-sys-id", "sys_id")
        assert result["sys_id"] == "user-sys-id"
        assert result["user_name"] == "testuser"

    @patch('requests.Session.request')
    def test_get_user_by_username_success(self, mock_request):
        """Test successful user retrieval by user name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{
                "sys_id": "user-sys-id",
                "user_name": "testuser",
                "email": "testuser@example.com"
            }]
        }
        mock_request.return_value = mock_response
        result = self.client.get_user("testuser", "user_name")
        assert result["sys_id"] == "user-sys-id"
        assert result["user_name"] == "testuser"

    @patch('requests.Session.request')
    def test_get_user_by_email_success(self, mock_request):
        """Test successful user retrieval by email."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": [{
                "sys_id": "user-sys-id",
                "user_name": "testuser",
                "email": "testuser@example.com"
            }]
        }
        mock_request.return_value = mock_response
        result = self.client.get_user("testuser@example.com", "email")
        assert result["email"] == "testuser@example.com"

    @patch('requests.Session.request')
    def test_get_user_not_found(self, mock_request):
        """Test user retrieval when user not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": []}
        mock_request.return_value = mock_response

        with pytest.raises(ResourceNotFoundError, match="not found"):
            self.client.get_user("NONEXISTENT", "user_name")

    @patch('requests.Session.request')
    def test_get_user_invalid_identifier(self, mock_request):
        """Test user retrieval with invalid identifier."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            self.client.get_user("", "sys_id")
