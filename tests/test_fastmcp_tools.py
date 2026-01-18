"""Tests for FastMCP tools."""

import pytest
from unittest.mock import patch

from src.servicenow_mcp.tools.fastmcp_tools import (
    mcp,
    initialize_tools
)
from src.servicenow_mcp.client.servicenow_client import ServiceNowClient
from src.servicenow_mcp.config.settings import ServiceNowConfig


@pytest.fixture
def mock_servicenow_client():
    """Mock ServiceNow client for testing."""
    config = ServiceNowConfig(
        instance_url="https://test.service-now.com",
        auth_type="basic",
        username="test",
        password="test"
    )
    client = ServiceNowClient(config)
    client._authenticated = True
    return client

# @pytest.fixture
# def mock_streaming_tools(mock_servicenow_client):
#     """Mock streaming tools for testing."""
#     return StreamingMCPTools(mock_servicenow_client)


@pytest.fixture
def initialized_tools(mock_servicenow_clients):
    """Initialize tools with mock clients."""
    initialize_tools(mock_servicenow_client)
    return mock_servicenow_client

class TestFastMCPToolsInitialization:
    """Test FastMCP tools initialization."""

    def test_mcp_instance_exists(self):
        """Test that FastMCP instance is created."""
        assert mcp is not None
        assert mcp.name == "ServiceNow MCP Server"

    def test_initialize_tools(self, mock_servicenow_client):
        """Test tools initialization."""
        initialize_tools(mock_servicenow_client)

        # Tools should be initialized (we can't easily test globals, but no errors should occur)
        assert True  # If we get here, initialization succeeded

    def test_mcp_tools_registered(self):
        """Test that tools are registered with FastMCP."""
        # Get the list of registered tools
        tools = mcp._tool_manager._tools
        tool_names = list(tools.keys())

        expected_tools = [
            "create_service_request",
            "get_service_request",
            "update_service_request", 
            "search_service_requests",
            "order_catalog_item",
            "get_server_info",
            "get_user"
        ]

        for tool_name in expected_tools:
            assert tool_name in tool_names


class TestServiceRequestToolsIntegration:
    """Test Service Request MCP tools integration."""
    
    @patch('src.servicenow_mcp.tools.fastmcp_tools.servicenow_client')
    def test_create_service_request_tool_exists(self, mock_client):
        """Test that create_service_request tool is properly registered."""
        # Get the tool from the FastMCP tool manager
        tools = mcp._tool_manager._tools
        assert "create_service_request" in tools

        create_tool = tools["create_service_request"]
        assert create_tool is not None
        assert create_tool.description is not None
        assert "Create a new Service Request" in create_tool.description

    @patch('src.servicenow_mcp.tools.fastmcp_tools.servicenow_client')
    def test_get_service_request_tool_exists(self, mock_client):
        """Test that get_service_request tool is properly registered."""
        tools = mcp._tool_manager._tools
        assert "get_service_request" in tools
        
        get_tool = tools["get_service_request"]
        assert get_tool is not None
        assert get_tool.description is not None
        assert "Retrieve a Service Request" in get_tool.description

    @patch('src.servicenow_mcp.tools.fastmcp_tools.servicenow_client')
    def test_update_service_request_tool_exists(self, mock_client):
        """Test that update_service_request tool is properly registered."""
        tools = mcp._tool_manager._tools
        assert "update_service_request" in tools

        update_tool = tools["update_service_request"]
        assert update_tool is not None
        assert update_tool.description is not None
        assert "Update an existing Service Request" in update_tool.description

    @patch('src.servicenow_mcp.tools.fastmcp_tools.servicenow_client')
    def test_order_catalog_item_tool_exists(self, mock_client):
        """Test that order_catalog_item tool is properly registered."""
        tools = mcp._tool_manager._tools
        assert "order_catalog_item" in tools
        order_tool = tools["order_catalog_item"]
        assert order_tool is not None
        assert order_tool.description is not None
        assert "Order a catalog item" in order_tool.description

    @patch('src.servicenow_mcp.tools.fastmcp_tools.servicenow_client')
    def test_search_service_requests_tool_exists(self, mock_client):
        """Test that search_service_requests tool is properly registered."""
        tools = mcp._tool_manager._tools
        assert "search_service_requests" in tools

        search_tool = tools["search_service_requests"]
        assert search_tool is not None
        assert search_tool.description is not None
        assert "Search Service Requests" in search_tool.description

    @patch('src.servicenow_mcp.tools.fastmcp_tools.servicenow_client')
    def test_get_user_tool_exists(self, mock_client):
        """Test that get_user tool is properly registered."""
        tools = mcp._tool_manager._tools
        assert "get_user" in tools

        get_user_tool = tools["get_user"]
        assert get_user_tool is not None
        assert get_user_tool.description is not None
        assert "Retrieve a User by sys_id, user_name or email." in get_user_tool.description

class TestServerInfoTool:
    """Test server info tool integration."""

    def test_server_info_tool_exists(self):
        """Test that get_server_info tool is properly registered."""
        tools = mcp._tool_manager._tools
        assert "get_server_info" in tools

        server_info_tool = tools["get_server_info"]
        assert server_info_tool is not None
        assert server_info_tool.description is not None
        assert "Get information about the ServiceNow MCP Server" in server_info_tool.description


class TestToolSchemas:
    """Test that tools have proper schemas."""

    def test_create_service_request_schema(self):
        """Test create_service_request tool schema."""
        tools = mcp._tool_manager._tools
        assert "create_service_request" in tools

        create_tool = tools["create_service_request"]
        assert create_tool is not None

        # Check that required parameters are in schema
        schema = create_tool.parameters
        assert "properties" in schema
        assert "short_description" in schema["properties"]
        assert "description" in schema["properties"]
        assert "priority" in schema["properties"]

        # Check required fields
        assert "required" in schema
        assert "short_description" in schema["required"]

    def test_search_service_requests_schema(self):
        """Test search_service_requests tool schema."""
        tools = mcp._tool_manager._tools
        assert "search_service_requests" in tools

        search_tool = tools["search_service_requests"]
        assert search_tool is not None

        # Check that search parameters are in schema
        schema = search_tool.parameters
        assert "properties" in schema
        assert "status" in schema["properties"]
        assert "requested_for" in schema["properties"]
        assert "date_from" in schema["properties"]
        assert "limit" in schema["properties"]


class TestFastMCPIntegration:
    """Test overall FastMCP integration."""

    def test_mcp_server_configuration(self):
        """Test FastMCP server configuration."""
        assert mcp.name == "ServiceNow MCP Server"
        tools = mcp._tool_manager._tools
        assert len(tools) >= 6  # Should have at least 6 tools

    def test_all_tools_have_descriptions(self):
        """Test that all tools have proper descriptions."""
        tools = mcp._tool_manager._tools
        for tool_name, tool in tools.items():
            assert tool.description is not None
            assert len(tool.description) > 0
            assert tool_name is not None

    def test_all_tools_have_schemas(self):
        """Test that all tools have proper parameter schemas."""
        tools = mcp._tool_manager._tools
        for tool_name, tool in tools.items():
            assert hasattr(tool, 'parameters')
            assert tool.parameters is not None
            assert "type" in tool.parameters
            assert tool.parameters["type"] == "object"
