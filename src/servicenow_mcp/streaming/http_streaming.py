"""HTTP streaming support for ServiceNow MCP Server."""

import json
import asyncio
from typing import Dict, Any, Iterator, Union, Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum

from ..exceptions import ServiceNowMCPError, ValidationError


class StreamingFormat(Enum):
    """Supported streaming formats."""
    JSON = "json"
    NDJSON = "ndjson"  # Newline-delimited JSON
    CSV = "csv"
    TEXT = "text"


@dataclass
class StreamingResponse:
    """Response object for streaming HTTP operations."""
    
    content_type: str
    data: Union[Iterator[Dict[str, Any]], Iterator[str], AsyncIterator[Dict[str, Any]], AsyncIterator[str]]
    total_count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate streaming response after initialization."""
        if not self.content_type:
            raise ValidationError(
                "Content type is required for streaming response",
                field_name="content_type"
            )


class StreamingHTTPHandler:
    """Handler for streaming HTTP responses in MCP server."""
    
    def __init__(self):
        """Initialize streaming HTTP handler."""
        self.supported_formats = {
            StreamingFormat.JSON: "application/json",
            StreamingFormat.NDJSON: "application/x-ndjson", 
            StreamingFormat.CSV: "text/csv",
            StreamingFormat.TEXT: "text/plain"
        }
    
    def create_streaming_response(
        self,
        data: Iterator[Dict[str, Any]],
        format_type: StreamingFormat = StreamingFormat.JSON,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StreamingResponse:
        """Create a streaming response from data iterator.
        
        Args:
            data: Iterator of data objects
            format_type: Output format for streaming
            metadata: Optional metadata about the stream
            
        Returns:
            StreamingResponse: Configured streaming response
            
        Raises:
            ValidationError: If format_type is unsupported
        """
        if format_type not in self.supported_formats:
            raise ValidationError(
                f"Unsupported streaming format: {format_type.value}",
                field_name="format_type",
                invalid_value=format_type.value
            )
        
        content_type = self.supported_formats[format_type]
        
        if format_type == StreamingFormat.JSON:
            # Convert to JSON array stream
            formatted_data = self._format_json_stream(data)
        elif format_type == StreamingFormat.NDJSON:
            # Convert to newline-delimited JSON
            formatted_data = self._format_ndjson_stream(data)
        elif format_type == StreamingFormat.CSV:
            # Convert to CSV stream
            formatted_data = self._format_csv_stream(data)
        elif format_type == StreamingFormat.TEXT:
            # Convert to text stream
            formatted_data = self._format_text_stream(data)
        else:
            formatted_data = data
        
        return StreamingResponse(
            content_type=content_type,
            data=formatted_data,
            metadata=metadata
        )
    
    def _format_json_stream(self, data: Iterator[Dict[str, Any]]) -> Iterator[str]:
        """Format data as JSON array stream.
        
        Args:
            data: Iterator of dictionaries
            
        Yields:
            str: JSON-formatted chunks
        """
        yield "["
        first = True
        
        for item in data:
            if not first:
                yield ","
            yield json.dumps(item, ensure_ascii=False)
            first = False
        
        yield "]"
    
    def _format_ndjson_stream(self, data: Iterator[Dict[str, Any]]) -> Iterator[str]:
        """Format data as newline-delimited JSON stream.
        
        Args:
            data: Iterator of dictionaries
            
        Yields:
            str: NDJSON-formatted lines
        """
        for item in data:
            yield json.dumps(item, ensure_ascii=False) + "\n"
    
    def _format_csv_stream(self, data: Iterator[Dict[str, Any]]) -> Iterator[str]:
        """Format data as CSV stream.
        
        Args:
            data: Iterator of dictionaries
            
        Yields:
            str: CSV-formatted lines
        """
        headers_written = False
        
        for item in data:
            if not headers_written:
                # Write CSV header
                headers = list(item.keys())
                yield ",".join(headers) + "\n"
                headers_written = True
            
            # Write CSV row
            values = [str(item.get(h, "")).replace('"', '""') for h in headers]
            yield ",".join(f'"{v}"' for v in values) + "\n"
    
    def _format_text_stream(self, data: Iterator[Dict[str, Any]]) -> Iterator[str]:
        """Format data as text stream.
        
        Args:
            data: Iterator of dictionaries
            
        Yields:
            str: Text-formatted lines
        """
        for item in data:
            yield str(item) + "\n"
    
    async def create_async_streaming_response(
        self,
        data: AsyncIterator[Dict[str, Any]],
        format_type: StreamingFormat = StreamingFormat.JSON,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StreamingResponse:
        """Create an async streaming response from async data iterator.
        
        Args:
            data: Async iterator of data objects
            format_type: Output format for streaming
            metadata: Optional metadata about the stream
            
        Returns:
            StreamingResponse: Configured async streaming response
            
        Raises:
            ValidationError: If format_type is unsupported
        """
        if format_type not in self.supported_formats:
            raise ValidationError(
                f"Unsupported streaming format: {format_type.value}",
                field_name="format_type",
                invalid_value=format_type.value
            )
        
        content_type = self.supported_formats[format_type]
        
        if format_type == StreamingFormat.JSON:
            formatted_data = self._format_async_json_stream(data)
        elif format_type == StreamingFormat.NDJSON:
            formatted_data = self._format_async_ndjson_stream(data)
        elif format_type == StreamingFormat.CSV:
            formatted_data = self._format_async_csv_stream(data)
        elif format_type == StreamingFormat.TEXT:
            formatted_data = self._format_async_text_stream(data)
        else:
            formatted_data = data
        
        return StreamingResponse(
            content_type=content_type,
            data=formatted_data,
            metadata=metadata
        )
    
    async def _format_async_json_stream(self, data: AsyncIterator[Dict[str, Any]]) -> AsyncIterator[str]:
        """Format async data as JSON array stream.
        
        Args:
            data: Async iterator of dictionaries
            
        Yields:
            str: JSON-formatted chunks
        """
        yield "["
        first = True
        
        async for item in data:
            if not first:
                yield ","
            yield json.dumps(item, ensure_ascii=False)
            first = False
        
        yield "]"
    
    async def _format_async_ndjson_stream(self, data: AsyncIterator[Dict[str, Any]]) -> AsyncIterator[str]:
        """Format async data as newline-delimited JSON stream.
        
        Args:
            data: Async iterator of dictionaries
            
        Yields:
            str: NDJSON-formatted lines
        """
        async for item in data:
            yield json.dumps(item, ensure_ascii=False) + "\n"
    
    async def _format_async_csv_stream(self, data: AsyncIterator[Dict[str, Any]]) -> AsyncIterator[str]:
        """Format async data as CSV stream.
        
        Args:
            data: Async iterator of dictionaries
            
        Yields:
            str: CSV-formatted lines
        """
        headers_written = False
        headers = []
        
        async for item in data:
            if not headers_written:
                # Write CSV header
                headers = list(item.keys())
                yield ",".join(headers) + "\n"
                headers_written = True
            
            # Write CSV row
            values = [str(item.get(h, "")).replace('"', '""') for h in headers]
            yield ",".join(f'"{v}"' for v in values) + "\n"
    
    async def _format_async_text_stream(self, data: AsyncIterator[Dict[str, Any]]) -> AsyncIterator[str]:
        """Format async data as text stream.
        
        Args:
            data: Async iterator of dictionaries
            
        Yields:
            str: Text-formatted lines
        """
        async for item in data:
            yield str(item) + "\n"
    
    def estimate_response_size(
        self,
        sample_item: Dict[str, Any],
        total_count: int,
        format_type: StreamingFormat = StreamingFormat.JSON
    ) -> int:
        """Estimate the total response size for streaming.
        
        Args:
            sample_item: Sample data item for size estimation
            total_count: Total number of items expected
            format_type: Output format
            
        Returns:
            int: Estimated response size in bytes
        """
        if format_type == StreamingFormat.JSON:
            # JSON array overhead + items + commas
            item_size = len(json.dumps(sample_item, ensure_ascii=False))
            return 2 + (item_size * total_count) + (total_count - 1)  # [] + items + commas
        
        elif format_type == StreamingFormat.NDJSON:
            # Each item + newline
            item_size = len(json.dumps(sample_item, ensure_ascii=False))
            return (item_size + 1) * total_count  # +1 for newline
        
        elif format_type == StreamingFormat.CSV:
            # Header + data rows
            headers = list(sample_item.keys())
            header_size = len(",".join(headers)) + 1  # +1 for newline
            
            # Estimate row size (with CSV escaping)
            values = [str(sample_item.get(h, "")) for h in headers]
            row_size = len(",".join(f'"{v}"' for v in values)) + 1  # +1 for newline
            
            return header_size + (row_size * total_count)
        
        elif format_type == StreamingFormat.TEXT:
            # Each item as string + newline
            item_size = len(str(sample_item))
            return (item_size + 1) * total_count  # +1 for newline
        
        return 0
    
    def get_content_type(self, format_type: StreamingFormat) -> str:
        """Get content type for streaming format.
        
        Args:
            format_type: Streaming format
            
        Returns:
            str: Content type string
            
        Raises:
            ValidationError: If format_type is unsupported
        """
        if format_type not in self.supported_formats:
            raise ValidationError(
                f"Unsupported streaming format: {format_type.value}",
                field_name="format_type",
                invalid_value=format_type.value
            )
        
        return self.supported_formats[format_type]