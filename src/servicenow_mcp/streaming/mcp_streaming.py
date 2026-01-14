"""MCP streaming tools for ServiceNow operations."""

from typing import Dict, Any, Iterator, Optional, List
import json

from ..client.servicenow_client import ServiceNowClient
from ..exceptions import ValidationError, ServiceNowMCPError
from .http_streaming import StreamingHTTPHandler, StreamingFormat, StreamingResponse


class StreamingMCPTools:
    """MCP tools with streaming support for ServiceNow operations."""
    
    def __init__(self, servicenow_client: ServiceNowClient):
        """Initialize streaming MCP tools.
        
        Args:
            servicenow_client: Authenticated ServiceNow client
        """
        self.client = servicenow_client
        self.streaming_handler = StreamingHTTPHandler()
    
    def stream_search_requests(
        self,
        filters: Dict[str, Any],
        format_type: str = "json",
        chunk_size: int = 100
    ) -> Dict[str, Any]:
        """Stream Service Request search results.
        
        This MCP tool provides streaming search results for large datasets,
        allowing clients to process results incrementally.
        
        Args:
            filters: Search criteria (same as regular search)
            format_type: Output format ("json", "ndjson", "csv", "text")
            chunk_size: Number of items to process per chunk
            
        Returns:
            Dict: MCP response with streaming metadata
            
        Raises:
            ValidationError: If parameters are invalid
            ServiceNowMCPError: If streaming fails
        """
        try:
            # Validate format type
            try:
                stream_format = StreamingFormat(format_type.lower())
            except ValueError:
                raise ValidationError(
                    f"Invalid format_type: {format_type}. Must be one of: json, ndjson, csv, text",
                    field_name="format_type",
                    invalid_value=format_type
                )
            
            # Validate chunk size
            if chunk_size <= 0:
                raise ValidationError(
                    "Chunk size must be positive",
                    field_name="chunk_size",
                    invalid_value=chunk_size
                )
            
            # Get streaming data from ServiceNow client
            data_stream = self.client.search_requests_stream(filters)
            
            # Create chunked stream for better performance
            chunked_stream = self._create_chunked_stream(data_stream, chunk_size)
            
            # Create streaming response
            streaming_response = self.streaming_handler.create_streaming_response(
                data=chunked_stream,
                format_type=stream_format,
                metadata={
                    "filters": filters,
                    "format": format_type,
                    "chunk_size": chunk_size
                }
            )
            
            return {
                "success": True,
                "streaming": True,
                "content_type": streaming_response.content_type,
                "metadata": streaming_response.metadata,
                "message": f"Streaming Service Request search results in {format_type} format"
            }
            
        except (ValidationError, ServiceNowMCPError) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, 'error_code', 'STREAMING_ERROR')
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during streaming: {str(e)}",
                "error_code": "UNEXPECTED_STREAMING_ERROR"
            }
    
    def stream_export_requests(
        self,
        filters: Optional[Dict[str, Any]] = None,
        format_type: str = "json",
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Stream Service Request export for large datasets.
        
        This MCP tool provides memory-efficient export of Service Request data,
        suitable for backup, reporting, or data migration purposes.
        
        Args:
            filters: Optional search criteria
            format_type: Export format ("json", "ndjson", "csv")
            fields: Specific fields to include in export
            
        Returns:
            Dict: MCP response with export metadata
            
        Raises:
            ValidationError: If parameters are invalid
            ServiceNowMCPError: If export fails
        """
        try:
            # Validate format type
            try:
                stream_format = StreamingFormat(format_type.lower())
            except ValueError:
                raise ValidationError(
                    f"Invalid format_type: {format_type}. Must be one of: json, ndjson, csv",
                    field_name="format_type",
                    invalid_value=format_type
                )
            
            # Validate fields if provided
            if fields is not None and not isinstance(fields, list):
                raise ValidationError(
                    "Fields must be a list of strings",
                    field_name="fields",
                    invalid_value=type(fields).__name__
                )
            
            # Get export stream from ServiceNow client
            if filters:
                # Use filtered search stream
                data_stream = self.client.search_requests_stream(filters)
            else:
                # Use all requests stream with field filtering
                data_stream = self.client.get_all_requests_stream(fields=fields)
            
            # Filter fields if specified and not using get_all_requests_stream
            if fields and filters:
                data_stream = self._filter_fields_stream(data_stream, fields)
            
            # Create streaming response
            streaming_response = self.streaming_handler.create_streaming_response(
                data=data_stream,
                format_type=stream_format,
                metadata={
                    "filters": filters,
                    "fields": fields,
                    "format": format_type,
                    "export_type": "full" if not filters else "filtered"
                }
            )
            
            return {
                "success": True,
                "streaming": True,
                "content_type": streaming_response.content_type,
                "metadata": streaming_response.metadata,
                "message": f"Streaming Service Request export in {format_type} format"
            }
            
        except (ValidationError, ServiceNowMCPError) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, 'error_code', 'EXPORT_ERROR')
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during export: {str(e)}",
                "error_code": "UNEXPECTED_EXPORT_ERROR"
            }
    
    def stream_batch_process_requests(
        self,
        operation: str,
        filters: Dict[str, Any],
        batch_size: int = 100,
        update_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Stream batch processing of Service Requests.
        
        This MCP tool enables batch operations on large sets of Service Requests
        with streaming progress updates.
        
        Args:
            operation: Batch operation ("update", "export", "validate")
            filters: Criteria for selecting requests to process
            batch_size: Number of requests to process per batch
            update_data: Data for update operations
            
        Returns:
            Dict: MCP response with batch processing metadata
            
        Raises:
            ValidationError: If parameters are invalid
            ServiceNowMCPError: If batch processing fails
        """
        try:
            # Validate operation
            valid_operations = ["update", "export", "validate"]
            if operation not in valid_operations:
                raise ValidationError(
                    f"Invalid operation: {operation}. Must be one of: {', '.join(valid_operations)}",
                    field_name="operation",
                    invalid_value=operation
                )
            
            # Validate batch size
            if batch_size <= 0:
                raise ValidationError(
                    "Batch size must be positive",
                    field_name="batch_size",
                    invalid_value=batch_size
                )
            
            # Validate update_data for update operations
            if operation == "update" and not update_data:
                raise ValidationError(
                    "update_data is required for update operations",
                    field_name="update_data"
                )
            
            # Get streaming data
            data_stream = self.client.search_requests_stream(filters)
            
            # Create batch processing stream
            if operation == "update":
                processed_stream = self._create_batch_update_stream(
                    data_stream, update_data, batch_size
                )
            elif operation == "export":
                processed_stream = self._create_batch_export_stream(
                    data_stream, batch_size
                )
            elif operation == "validate":
                processed_stream = self._create_batch_validate_stream(
                    data_stream, batch_size
                )
            
            # Create streaming response
            streaming_response = self.streaming_handler.create_streaming_response(
                data=processed_stream,
                format_type=StreamingFormat.NDJSON,  # Use NDJSON for batch processing
                metadata={
                    "operation": operation,
                    "filters": filters,
                    "batch_size": batch_size,
                    "update_data": update_data if operation == "update" else None
                }
            )
            
            return {
                "success": True,
                "streaming": True,
                "content_type": streaming_response.content_type,
                "metadata": streaming_response.metadata,
                "message": f"Streaming batch {operation} operation"
            }
            
        except (ValidationError, ServiceNowMCPError) as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": getattr(e, 'error_code', 'BATCH_PROCESSING_ERROR')
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during batch processing: {str(e)}",
                "error_code": "UNEXPECTED_BATCH_ERROR"
            }
    
    def _create_chunked_stream(
        self, 
        data_stream: Iterator[Dict[str, Any]], 
        chunk_size: int
    ) -> Iterator[Dict[str, Any]]:
        """Create chunked stream from data iterator.
        
        Args:
            data_stream: Source data iterator
            chunk_size: Size of each chunk
            
        Yields:
            Dict: Individual items from chunks
        """
        chunk = []
        
        for item in data_stream:
            chunk.append(item)
            
            if len(chunk) >= chunk_size:
                # Yield all items in chunk
                for chunk_item in chunk:
                    yield chunk_item
                chunk = []
        
        # Yield remaining items
        for item in chunk:
            yield item
    
    def _filter_fields_stream(
        self,
        data_stream: Iterator[Dict[str, Any]],
        fields: List[str]
    ) -> Iterator[Dict[str, Any]]:
        """Filter fields from data stream.
        
        Args:
            data_stream: Source data iterator
            fields: Fields to include
            
        Yields:
            Dict: Filtered data items
        """
        for item in data_stream:
            filtered_item = {field: item.get(field) for field in fields if field in item}
            yield filtered_item
    
    def _create_batch_update_stream(
        self,
        data_stream: Iterator[Dict[str, Any]],
        update_data: Dict[str, Any],
        batch_size: int
    ) -> Iterator[Dict[str, Any]]:
        """Create batch update processing stream.
        
        Args:
            data_stream: Source data iterator
            update_data: Data to update
            batch_size: Batch size
            
        Yields:
            Dict: Update results
        """
        batch = []
        batch_number = 1
        
        for item in data_stream:
            batch.append(item)
            
            if len(batch) >= batch_size:
                # Process batch
                results = self._process_update_batch(batch, update_data, batch_number)
                for result in results:
                    yield result
                
                batch = []
                batch_number += 1
        
        # Process remaining items
        if batch:
            results = self._process_update_batch(batch, update_data, batch_number)
            for result in results:
                yield result
    
    def _create_batch_export_stream(
        self,
        data_stream: Iterator[Dict[str, Any]],
        batch_size: int
    ) -> Iterator[Dict[str, Any]]:
        """Create batch export processing stream.
        
        Args:
            data_stream: Source data iterator
            batch_size: Batch size
            
        Yields:
            Dict: Export progress updates
        """
        count = 0
        batch_number = 1
        
        for item in data_stream:
            count += 1
            
            # Yield progress updates every batch_size items
            if count % batch_size == 0:
                yield {
                    "batch_number": batch_number,
                    "items_processed": count,
                    "status": "processing",
                    "last_item_id": item.get("sys_id", "unknown")
                }
                batch_number += 1
            
            # Also yield the actual item
            yield item
        
        # Final progress update
        yield {
            "batch_number": batch_number,
            "items_processed": count,
            "status": "completed",
            "total_items": count
        }
    
    def _create_batch_validate_stream(
        self,
        data_stream: Iterator[Dict[str, Any]],
        batch_size: int
    ) -> Iterator[Dict[str, Any]]:
        """Create batch validation processing stream.
        
        Args:
            data_stream: Source data iterator
            batch_size: Batch size
            
        Yields:
            Dict: Validation results
        """
        batch = []
        batch_number = 1
        
        for item in data_stream:
            batch.append(item)
            
            if len(batch) >= batch_size:
                # Validate batch
                results = self._validate_batch(batch, batch_number)
                for result in results:
                    yield result
                
                batch = []
                batch_number += 1
        
        # Validate remaining items
        if batch:
            results = self._validate_batch(batch, batch_number)
            for result in results:
                yield result
    
    def _process_update_batch(
        self,
        batch: List[Dict[str, Any]],
        update_data: Dict[str, Any],
        batch_number: int
    ) -> List[Dict[str, Any]]:
        """Process update batch.
        
        Args:
            batch: Batch of items to update
            update_data: Update data
            batch_number: Batch number
            
        Returns:
            List[Dict]: Update results
        """
        results = []
        
        for item in batch:
            try:
                sys_id = item.get("sys_id")
                if sys_id:
                    updated_item = self.client.update_request(sys_id, update_data)
                    results.append({
                        "sys_id": sys_id,
                        "status": "updated",
                        "batch_number": batch_number
                    })
                else:
                    results.append({
                        "sys_id": "unknown",
                        "status": "error",
                        "error": "Missing sys_id",
                        "batch_number": batch_number
                    })
            except Exception as e:
                results.append({
                    "sys_id": item.get("sys_id", "unknown"),
                    "status": "error",
                    "error": str(e),
                    "batch_number": batch_number
                })
        
        return results
    
    def _validate_batch(
        self,
        batch: List[Dict[str, Any]],
        batch_number: int
    ) -> List[Dict[str, Any]]:
        """Validate batch of items.
        
        Args:
            batch: Batch of items to validate
            batch_number: Batch number
            
        Returns:
            List[Dict]: Validation results
        """
        results = []
        
        for item in batch:
            validation_result = {
                "sys_id": item.get("sys_id", "unknown"),
                "batch_number": batch_number,
                "validation_errors": []
            }
            
            # Basic validation checks
            if not item.get("sys_id"):
                validation_result["validation_errors"].append("Missing sys_id")
            
            if not item.get("short_description"):
                validation_result["validation_errors"].append("Missing short_description")
            
            if not item.get("state"):
                validation_result["validation_errors"].append("Missing state")
            
            validation_result["status"] = "valid" if not validation_result["validation_errors"] else "invalid"
            results.append(validation_result)
        
        return results