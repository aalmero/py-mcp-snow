"""Tests for streaming HTTP functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Iterator, Dict, Any

from src.servicenow_mcp.streaming.http_streaming import (
    StreamingHTTPHandler, 
    StreamingResponse, 
    StreamingFormat
)
from src.servicenow_mcp.streaming.mcp_streaming import StreamingMCPTools
from src.servicenow_mcp.client.servicenow_client import ServiceNowClient
from src.servicenow_mcp.config.settings import ServiceNowConfig
from src.servicenow_mcp.exceptions import ValidationError


@pytest.fixture
def sample_data():
    """Sample Service Request data for testing."""
    return [
        {
            "sys_id": "test-1",
            "number": "REQ0001",
            "short_description": "Test request 1",
            "state": "1"
        },
        {
            "sys_id": "test-2", 
            "number": "REQ0002",
            "short_description": "Test request 2",
            "state": "2"
        },
        {
            "sys_id": "test-3",
            "number": "REQ0003", 
            "short_description": "Test request 3",
            "state": "1"
        }
    ]


@pytest.fixture
def streaming_handler():
    """StreamingHTTPHandler instance for testing."""
    return StreamingHTTPHandler()


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


@pytest.fixture
def streaming_mcp_tools(mock_servicenow_client):
    """StreamingMCPTools instance for testing."""
    return StreamingMCPTools(mock_servicenow_client)


class TestStreamingHTTPHandler:
    """Test StreamingHTTPHandler functionality."""
    
    def test_create_streaming_response_json(self, streaming_handler, sample_data):
        """Test creating JSON streaming response."""
        data_iter = iter(sample_data)
        
        response = streaming_handler.create_streaming_response(
            data=data_iter,
            format_type=StreamingFormat.JSON
        )
        
        assert response.content_type == "application/json"
        assert response.metadata is None
        
        # Consume the stream and verify JSON format
        chunks = list(response.data)
        json_output = "".join(chunks)
        
        assert json_output.startswith("[")
        assert json_output.endswith("]")
        assert "test-1" in json_output
        assert "REQ0001" in json_output
    
    def test_create_streaming_response_ndjson(self, streaming_handler, sample_data):
        """Test creating NDJSON streaming response."""
        data_iter = iter(sample_data)
        
        response = streaming_handler.create_streaming_response(
            data=data_iter,
            format_type=StreamingFormat.NDJSON
        )
        
        assert response.content_type == "application/x-ndjson"
        
        # Consume the stream and verify NDJSON format
        lines = list(response.data)
        
        assert len(lines) == 3
        for line in lines:
            assert line.endswith("\n")
            assert "sys_id" in line
    
    def test_create_streaming_response_csv(self, streaming_handler, sample_data):
        """Test creating CSV streaming response."""
        data_iter = iter(sample_data)
        
        response = streaming_handler.create_streaming_response(
            data=data_iter,
            format_type=StreamingFormat.CSV
        )
        
        assert response.content_type == "text/csv"
        
        # Consume the stream and verify CSV format
        lines = list(response.data)
        
        # Should have header + 3 data rows
        assert len(lines) == 4
        assert "sys_id,number,short_description,state" in lines[0]
        assert '"test-1","REQ0001"' in lines[1]
    
    def test_create_streaming_response_invalid_format(self, streaming_handler, sample_data):
        """Test creating streaming response with invalid format."""
        data_iter = iter(sample_data)
        
        # Test with invalid enum value - this should raise ValueError during enum creation
        with pytest.raises(ValueError):
            StreamingFormat("invalid_format")
        
        # Test the actual validation in create_streaming_response
        # We need to pass a valid enum but test the validation logic
        with pytest.raises(ValidationError, match="Unsupported streaming format"):
            # Create a mock format that's not in supported_formats
            mock_format = Mock()
            mock_format.value = "unsupported"
            streaming_handler.create_streaming_response(
                data=data_iter,
                format_type=mock_format
            )
    
    def test_estimate_response_size_json(self, streaming_handler, sample_data):
        """Test response size estimation for JSON format."""
        sample_item = sample_data[0]
        total_count = 100
        
        estimated_size = streaming_handler.estimate_response_size(
            sample_item=sample_item,
            total_count=total_count,
            format_type=StreamingFormat.JSON
        )
        
        assert estimated_size > 0
        assert isinstance(estimated_size, int)
    
    def test_estimate_response_size_csv(self, streaming_handler, sample_data):
        """Test response size estimation for CSV format."""
        sample_item = sample_data[0]
        total_count = 50
        
        estimated_size = streaming_handler.estimate_response_size(
            sample_item=sample_item,
            total_count=total_count,
            format_type=StreamingFormat.CSV
        )
        
        assert estimated_size > 0
        assert isinstance(estimated_size, int)
    
    def test_get_content_type(self, streaming_handler):
        """Test getting content type for formats."""
        assert streaming_handler.get_content_type(StreamingFormat.JSON) == "application/json"
        assert streaming_handler.get_content_type(StreamingFormat.NDJSON) == "application/x-ndjson"
        assert streaming_handler.get_content_type(StreamingFormat.CSV) == "text/csv"
        assert streaming_handler.get_content_type(StreamingFormat.TEXT) == "text/plain"


class TestStreamingMCPTools:
    """Test StreamingMCPTools functionality."""
    
    @patch.object(ServiceNowClient, 'search_requests_stream')
    def test_stream_search_requests_success(self, mock_stream, streaming_mcp_tools, sample_data):
        """Test successful streaming search requests."""
        mock_stream.return_value = iter(sample_data)
        
        filters = {"status": "1"}
        result = streaming_mcp_tools.stream_search_requests(
            filters=filters,
            format_type="json",
            chunk_size=2
        )
        
        assert result["success"] is True
        assert result["streaming"] is True
        assert result["content_type"] == "application/json"
        assert result["metadata"]["filters"] == filters
        assert result["metadata"]["format"] == "json"
        assert result["metadata"]["chunk_size"] == 2
        
        mock_stream.assert_called_once_with(filters)
    
    def test_stream_search_requests_invalid_format(self, streaming_mcp_tools):
        """Test streaming search with invalid format."""
        filters = {"status": "1"}
        result = streaming_mcp_tools.stream_search_requests(
            filters=filters,
            format_type="invalid",
            chunk_size=10
        )
        
        assert result["success"] is False
        assert "Invalid format_type" in result["error"]
        assert result["error_code"] == "VALIDATION_ERROR"
    
    def test_stream_search_requests_invalid_chunk_size(self, streaming_mcp_tools):
        """Test streaming search with invalid chunk size."""
        filters = {"status": "1"}
        result = streaming_mcp_tools.stream_search_requests(
            filters=filters,
            format_type="json",
            chunk_size=0
        )
        
        assert result["success"] is False
        assert "Chunk size must be positive" in result["error"]
        assert result["error_code"] == "VALIDATION_ERROR"
    
    @patch.object(ServiceNowClient, 'search_requests_stream')
    def test_stream_export_requests_with_filters(self, mock_stream, streaming_mcp_tools, sample_data):
        """Test streaming export with filters."""
        mock_stream.return_value = iter(sample_data)
        
        filters = {"state": "1"}
        result = streaming_mcp_tools.stream_export_requests(
            filters=filters,
            format_type="csv",
            fields=["sys_id", "number"]
        )
        
        assert result["success"] is True
        assert result["streaming"] is True
        assert result["content_type"] == "text/csv"
        assert result["metadata"]["filters"] == filters
        assert result["metadata"]["fields"] == ["sys_id", "number"]
        assert result["metadata"]["export_type"] == "filtered"
        
        mock_stream.assert_called_once_with(filters)
    
    @patch.object(ServiceNowClient, 'get_all_requests_stream')
    def test_stream_export_requests_all(self, mock_stream, streaming_mcp_tools, sample_data):
        """Test streaming export of all requests."""
        mock_stream.return_value = iter(sample_data)
        
        result = streaming_mcp_tools.stream_export_requests(
            filters=None,
            format_type="ndjson",
            fields=["sys_id", "state"]
        )
        
        assert result["success"] is True
        assert result["streaming"] is True
        assert result["content_type"] == "application/x-ndjson"
        assert result["metadata"]["filters"] is None
        assert result["metadata"]["export_type"] == "full"
        
        mock_stream.assert_called_once_with(fields=["sys_id", "state"])
    
    def test_stream_export_requests_invalid_fields(self, streaming_mcp_tools):
        """Test streaming export with invalid fields parameter."""
        result = streaming_mcp_tools.stream_export_requests(
            filters=None,
            format_type="json",
            fields="invalid"  # Should be list, not string
        )
        
        assert result["success"] is False
        assert "Fields must be a list" in result["error"]
        assert result["error_code"] == "VALIDATION_ERROR"
    
    @patch.object(ServiceNowClient, 'search_requests_stream')
    def test_stream_batch_process_update(self, mock_stream, streaming_mcp_tools, sample_data):
        """Test streaming batch update processing."""
        mock_stream.return_value = iter(sample_data)
        
        filters = {"state": "1"}
        update_data = {"priority": "1"}
        
        result = streaming_mcp_tools.stream_batch_process_requests(
            operation="update",
            filters=filters,
            batch_size=2,
            update_data=update_data
        )
        
        assert result["success"] is True
        assert result["streaming"] is True
        assert result["content_type"] == "application/x-ndjson"
        assert result["metadata"]["operation"] == "update"
        assert result["metadata"]["update_data"] == update_data
        
        mock_stream.assert_called_once_with(filters)
    
    def test_stream_batch_process_invalid_operation(self, streaming_mcp_tools):
        """Test streaming batch processing with invalid operation."""
        result = streaming_mcp_tools.stream_batch_process_requests(
            operation="invalid",
            filters={"state": "1"},
            batch_size=10
        )
        
        assert result["success"] is False
        assert "Invalid operation" in result["error"]
        assert result["error_code"] == "VALIDATION_ERROR"
    
    def test_stream_batch_process_update_missing_data(self, streaming_mcp_tools):
        """Test streaming batch update without update_data."""
        result = streaming_mcp_tools.stream_batch_process_requests(
            operation="update",
            filters={"state": "1"},
            batch_size=10,
            update_data=None
        )
        
        assert result["success"] is False
        assert "update_data is required" in result["error"]
        assert result["error_code"] == "VALIDATION_ERROR"
    
    def test_chunked_stream(self, streaming_mcp_tools, sample_data):
        """Test chunked stream creation."""
        data_iter = iter(sample_data)
        chunked = streaming_mcp_tools._create_chunked_stream(data_iter, chunk_size=2)
        
        # Should yield all items, but in chunks
        result = list(chunked)
        assert len(result) == 3
        assert result[0]["sys_id"] == "test-1"
        assert result[1]["sys_id"] == "test-2"
        assert result[2]["sys_id"] == "test-3"
    
    def test_filter_fields_stream(self, streaming_mcp_tools, sample_data):
        """Test field filtering in stream."""
        data_iter = iter(sample_data)
        fields = ["sys_id", "number"]
        filtered = streaming_mcp_tools._filter_fields_stream(data_iter, fields)
        
        result = list(filtered)
        assert len(result) == 3
        
        for item in result:
            assert "sys_id" in item
            assert "number" in item
            assert "short_description" not in item
            assert "state" not in item


class TestStreamingResponse:
    """Test StreamingResponse data class."""
    
    def test_streaming_response_creation(self, sample_data):
        """Test creating StreamingResponse."""
        data_iter = iter(sample_data)
        
        response = StreamingResponse(
            content_type="application/json",
            data=data_iter,
            total_count=3,
            metadata={"test": "value"}
        )
        
        assert response.content_type == "application/json"
        assert response.total_count == 3
        assert response.metadata == {"test": "value"}
    
    def test_streaming_response_validation(self):
        """Test StreamingResponse validation."""
        with pytest.raises(ValidationError, match="Content type is required"):
            StreamingResponse(
                content_type="",  # Empty content type should fail
                data=iter([])
            )