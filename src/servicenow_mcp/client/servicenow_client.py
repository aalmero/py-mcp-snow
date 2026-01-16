"""ServiceNow HTTP client with authentication support."""

import time
from typing import Dict, Any, Optional, List, Iterator, Union
import requests
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json

from ..config.settings import ServiceNowConfig
from ..exceptions import (
    AuthenticationError,
    ServiceNowAPIError,
    ConnectionError,
    RateLimitError,
    ResourceNotFoundError,
    ValidationError
)


class ServiceNowClient:
    """HTTP client for ServiceNow REST API with authentication and error handling."""
    
    def __init__(self, config: ServiceNowConfig):
        """Initialize ServiceNow client with configuration.
        
        Args:
            config: ServiceNow configuration including credentials and settings
        """
        self.config = config
        self.session = requests.Session()
        self._setup_session()
        self._authenticated = False
    
    def _setup_session(self) -> None:
        """Configure the requests session with retry strategy and timeouts."""
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.retry_count,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'ServiceNow-MCP-Server/0.1.0'
        })
        
        # Set timeout
        self.session.timeout = self.config.timeout
    
    def authenticate(self) -> bool:
        """Authenticate with ServiceNow using configured credentials.
        
        Returns:
            bool: True if authentication successful
            
        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection to ServiceNow fails
        """
        try:
            if self.config.auth_type == "basic":
                self.session.auth = HTTPBasicAuth(
                    self.config.username, 
                    self.config.password
                )
            elif self.config.auth_type == "api_key":
                self.session.headers.update({
                    'Authorization': f'Bearer {self.config.api_key}'
                })
            else:
                raise AuthenticationError(
                    f"Unsupported authentication type: {self.config.auth_type}",
                    auth_type=self.config.auth_type
                )
            
            # Validate authentication by making a test request
            if self.validate_connection():
                self._authenticated = True
                return True
            else:
                raise AuthenticationError(
                    "Authentication validation failed",
                    auth_type=self.config.auth_type
                )
                
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to ServiceNow instance: {e}",
                instance_url=self.config.instance_url
            )
        except requests.exceptions.Timeout as e:
            raise ConnectionError(
                f"Connection timeout to ServiceNow instance: {e}",
                instance_url=self.config.instance_url
            )
    
    def validate_connection(self) -> bool:
        """Validate connection to ServiceNow by making a test API call.
        
        Returns:
            bool: True if connection is valid
            
        Raises:
            ConnectionError: If connection validation fails
            AuthenticationError: If authentication is invalid
        """
        try:
            # Use a lightweight endpoint to test connection
            url = f"{self.config.instance_url}/api/now/table/sys_user"
            params = {'sysparm_limit': 1, 'sysparm_fields': 'sys_id'}
            
            response = self.session.get(url, params=params, timeout=self.config.timeout)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                raise AuthenticationError(
                    "Invalid credentials provided",
                    auth_type=self.config.auth_type
                )
            elif response.status_code == 403:
                raise AuthenticationError(
                    "Access denied - insufficient permissions",
                    auth_type=self.config.auth_type
                )
            else:
                self._handle_error_response(response)
                return False
                
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Failed to validate connection to ServiceNow: {e}",
                instance_url=self.config.instance_url
            )
        except requests.exceptions.Timeout as e:
            raise ConnectionError(
                f"Connection validation timeout: {e}",
                instance_url=self.config.instance_url
            )
    
    def _handle_error_response(self, response: requests.Response) -> None:
        """Handle error responses from ServiceNow API.
        
        Args:
            response: HTTP response object
            
        Raises:
            ServiceNowAPIError: For general API errors
            RateLimitError: For rate limit errors
            ResourceNotFoundError: For 404 errors
            AuthenticationError: For authentication errors
        """
        status_code = response.status_code
        
        try:
            error_data = response.json()
        except ValueError:
            error_data = {"error": {"message": response.text}}
        
        if status_code == 401:
            raise AuthenticationError(
                "Authentication failed - invalid credentials",
                auth_type=self.config.auth_type
            )
        elif status_code == 403:
            raise AuthenticationError(
                "Access denied - insufficient permissions",
                auth_type=self.config.auth_type
            )
        elif status_code == 404:
            raise ResourceNotFoundError(
                "Resource not found",
                resource_id=response.url
            )
        elif status_code == 429:
            # Extract retry-after header if available
            retry_after = response.headers.get('Retry-After')
            retry_seconds = int(retry_after) if retry_after else 60
            
            raise RateLimitError(
                f"Rate limit exceeded. Retry after {retry_seconds} seconds",
                retry_after=retry_seconds
            )
        else:
            error_message = "Unknown ServiceNow API error"
            if isinstance(error_data, dict) and 'error' in error_data:
                if isinstance(error_data['error'], dict):
                    error_message = error_data['error'].get('message', error_message)
                else:
                    error_message = str(error_data['error'])
            
            raise ServiceNowAPIError(
                error_message,
                status_code=status_code,
                response_data=error_data
            )
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """Make authenticated request to ServiceNow API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            stream: Whether to return a streaming response
            
        Returns:
            Dict containing response data or Iterator for streaming responses
            
        Raises:
            AuthenticationError: If not authenticated
            ServiceNowAPIError: For API errors
            ConnectionError: For connection errors
        """
        if not self._authenticated:
            raise AuthenticationError(
                "Client not authenticated. Call authenticate() first.",
                auth_type=self.config.auth_type
            )
        
        url = f"{self.config.instance_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.config.timeout,
                stream=stream
            )
            
            if response.status_code in [200, 201]:
                if stream:
                    return self._stream_json_response(response)
                else:
                    return response.json()
            else:
                self._handle_error_response(response)
                
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(
                f"Connection error during API request: {e}",
                instance_url=self.config.instance_url
            )
        except requests.exceptions.Timeout as e:
            raise ConnectionError(
                f"Request timeout: {e}",
                instance_url=self.config.instance_url
            )
    
    def _stream_json_response(self, response: requests.Response) -> Iterator[Dict[str, Any]]:
        """Stream JSON response line by line.
        
        Args:
            response: HTTP response object with streaming enabled
            
        Yields:
            Dict: Parsed JSON objects from the stream
        """
        try:
            # For ServiceNow API, we expect a JSON response with a 'result' array
            # We'll stream each item in the result array
            buffer = ""
            
            for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
                if chunk:
                    buffer += chunk
                    
                    # Try to parse complete JSON objects
                    while True:
                        try:
                            # Find the end of a complete JSON object
                            obj, idx = json.JSONDecoder().raw_decode(buffer)
                            
                            # If this is a ServiceNow response with 'result' array, yield each item
                            if isinstance(obj, dict) and 'result' in obj:
                                if isinstance(obj['result'], list):
                                    for item in obj['result']:
                                        yield item
                                else:
                                    yield obj['result']
                            else:
                                yield obj
                            
                            # Remove the parsed object from buffer
                            buffer = buffer[idx:].lstrip()
                            
                        except json.JSONDecodeError:
                            # Not enough data for a complete JSON object
                            break
            
            # Handle any remaining data in buffer
            if buffer.strip():
                try:
                    obj = json.loads(buffer)
                    if isinstance(obj, dict) and 'result' in obj:
                        if isinstance(obj['result'], list):
                            for item in obj['result']:
                                yield item
                        else:
                            yield obj['result']
                    else:
                        yield obj
                except json.JSONDecodeError:
                    # Log warning about unparseable data
                    pass
                    
        finally:
            response.close()
    
    def create_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Service Request in ServiceNow.
        
        Args:
            data: Service Request data
            
        Returns:
            Dict containing created request data with sys_id and number
            
        Raises:
            ValidationError: If required fields are missing
            ServiceNowAPIError: If creation fails
        """
        # Validate required fields
        if not data.get('short_description'):
            raise ValidationError(
                "short_description is required for Service Request creation",
                field_name="short_description"
            )
        
        endpoint = "/api/now/table/sc_request"
        response_data = self._make_request("POST", endpoint, data=data)
        
        if 'result' in response_data:
            return response_data['result']
        else:
            raise ServiceNowAPIError(
                "Unexpected response format from ServiceNow",
                response_data=response_data
            )
    
    def get_request(self, identifier: str, id_type: str = "sys_id") -> Dict[str, Any]:
        """Retrieve a Service Request by sys_id or request number.
        
        Args:
            identifier: sys_id or request number
            id_type: "sys_id" or "number"
            
        Returns:
            Dict containing Service Request data
            
        Raises:
            ValidationError: If identifier is invalid
            ResourceNotFoundError: If request not found
            ServiceNowAPIError: If retrieval fails
        """
        if not identifier:
            raise ValidationError(
                f"Service Request {id_type} cannot be empty",
                field_name=id_type,
                invalid_value=identifier
            )
        
        if id_type == "sys_id":
            endpoint = f"/api/now/table/sc_request/{identifier}"
            response_data = self._make_request("GET", endpoint)
        elif id_type == "number":
            endpoint = "/api/now/table/sc_request"
            params = {'sysparm_query': f'number={identifier}'}
            response_data = self._make_request("GET", endpoint, params=params)
            
            if 'result' in response_data and response_data['result']:
                return response_data['result'][0]
            else:
                raise ResourceNotFoundError(
                    f"Service Request with number {identifier} not found",
                    resource_type="sc_request",
                    resource_id=identifier
                )
        else:
            raise ValidationError(
                f"Invalid id_type: {id_type}. Must be 'sys_id' or 'number'",
                field_name="id_type",
                invalid_value=id_type
            )
        
        if 'result' in response_data:
            return response_data['result']
        else:
            raise ServiceNowAPIError(
                "Unexpected response format from ServiceNow",
                response_data=response_data
            )
    
    def update_request(self, sys_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing Service Request.
        
        Args:
            sys_id: Service Request sys_id
            data: Fields to update
            
        Returns:
            Dict containing updated Service Request data
            
        Raises:
            ValidationError: If sys_id is invalid
            ResourceNotFoundError: If request not found
            ServiceNowAPIError: If update fails
        """
        if not sys_id:
            raise ValidationError(
                "Service Request sys_id cannot be empty",
                field_name="sys_id",
                invalid_value=sys_id
            )
        
        endpoint = f"/api/now/table/sc_request/{sys_id}"
        response_data = self._make_request("PUT", endpoint, data=data)
        
        if 'result' in response_data:
            return response_data['result']
        else:
            raise ServiceNowAPIError(
                "Unexpected response format from ServiceNow",
                response_data=response_data
            )
    
    def search_requests(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search Service Requests with multiple criteria.
        
        Supports filtering by status, requested_for user, opened_by user, and date ranges.
        Multiple criteria are combined with AND logic.
        
        Args:
            filters: Search criteria dictionary with optional keys:
                - status: Service Request state (e.g., "1", "2", "3")
                - requested_for: User sys_id or username for whom request was made
                - opened_by: User sys_id or username who opened the request
                - date_from: Start date for opened_at filter (ISO format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
                - date_to: End date for opened_at filter (ISO format: YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)
                - limit: Maximum number of results to return (default: no limit)
                - offset: Number of results to skip for pagination (default: 0)
            
        Returns:
            List of Service Request dictionaries matching the criteria.
            Returns empty list if no matches found.
            
        Raises:
            ValidationError: If filter values are invalid
            ServiceNowAPIError: If search fails
        """
        # Validate filters
        if not isinstance(filters, dict):
            raise ValidationError(
                "Filters must be a dictionary",
                field_name="filters",
                invalid_value=type(filters).__name__
            )
        
        # Build query string from filters using AND logic
        query_parts = []
        
        # Status filter
        if 'status' in filters:
            status = filters['status']
            if status is not None and str(status).strip():
                query_parts.append(f"state={status}")
        
        # Requested for user filter
        if 'requested_for' in filters:
            requested_for = filters['requested_for']
            if requested_for is not None and str(requested_for).strip():
                query_parts.append(f"requested_for={requested_for}")
        
        # Opened by user filter
        if 'opened_by' in filters:
            opened_by = filters['opened_by']
            if opened_by is not None and str(opened_by).strip():
                query_parts.append(f"opened_by={opened_by}")
        
        # Date range filters
        if 'date_from' in filters:
            date_from = filters['date_from']
            if date_from is not None and str(date_from).strip():
                query_parts.append(f"opened_at>={date_from}")
        
        if 'date_to' in filters:
            date_to = filters['date_to']
            if date_to is not None and str(date_to).strip():
                query_parts.append(f"opened_at<={date_to}")
        
        # Additional filters for assignment
        if 'assignment_group' in filters:
            assignment_group = filters['assignment_group']
            if assignment_group is not None and str(assignment_group).strip():
                query_parts.append(f"assignment_group={assignment_group}")
        
        if 'assigned_to' in filters:
            assigned_to = filters['assigned_to']
            if assigned_to is not None and str(assigned_to).strip():
                query_parts.append(f"assigned_to={assigned_to}")
        
        # Combine query parts with AND logic (^ in ServiceNow query syntax)
        query = '^'.join(query_parts) if query_parts else ''
        
        # Prepare API request
        endpoint = "/api/now/table/sc_request"
        params = {}
        
        if query:
            params['sysparm_query'] = query
        
        # Add pagination support with validation
        if 'limit' in filters:
            limit = filters['limit']
            if limit is not None:
                try:
                    limit_int = int(limit)
                    if limit_int < 0:
                        raise ValidationError(
                            "Limit must be non-negative",
                            field_name="limit",
                            invalid_value=limit
                        )
                    params['sysparm_limit'] = limit_int
                except (ValueError, TypeError):
                    raise ValidationError(
                        "Limit must be a valid integer",
                        field_name="limit",
                        invalid_value=limit
                    )
        
        if 'offset' in filters:
            offset = filters['offset']
            if offset is not None:
                try:
                    offset_int = int(offset)
                    if offset_int < 0:
                        raise ValidationError(
                            "Offset must be non-negative",
                            field_name="offset",
                            invalid_value=offset
                        )
                    params['sysparm_offset'] = offset_int
                except (ValueError, TypeError):
                    raise ValidationError(
                        "Offset must be a valid integer",
                        field_name="offset",
                        invalid_value=offset
                    )
        
        # Make the API request
        response_data = self._make_request("GET", endpoint, params=params)
        
        if 'result' in response_data:
            # Return the results (empty list if no matches)
            return response_data['result']
        else:
            raise ServiceNowAPIError(
                "Unexpected response format from ServiceNow",
                response_data=response_data
            )
    
    def search_requests_stream(self, filters: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Search Service Requests with streaming response for large result sets.
        
        This method is useful for processing large numbers of Service Requests without
        loading them all into memory at once. Results are yielded one at a time.
        
        Args:
            filters: Search criteria (same as search_requests method)
            
        Yields:
            Dict: Individual Service Request dictionaries
            
        Raises:
            ValidationError: If filter values are invalid
            ServiceNowAPIError: If search fails
        """
        # Validate filters (reuse validation logic from search_requests)
        if not isinstance(filters, dict):
            raise ValidationError(
                "Filters must be a dictionary",
                field_name="filters",
                invalid_value=type(filters).__name__
            )
        
        # Build query string from filters using AND logic
        query_parts = []
        
        # Status filter
        if 'status' in filters:
            status = filters['status']
            if status is not None and str(status).strip():
                query_parts.append(f"state={status}")
        
        # Requested for user filter
        if 'requested_for' in filters:
            requested_for = filters['requested_for']
            if requested_for is not None and str(requested_for).strip():
                query_parts.append(f"requested_for={requested_for}")
        
        # Opened by user filter
        if 'opened_by' in filters:
            opened_by = filters['opened_by']
            if opened_by is not None and str(opened_by).strip():
                query_parts.append(f"opened_by={opened_by}")
        
        # Date range filters
        if 'date_from' in filters:
            date_from = filters['date_from']
            if date_from is not None and str(date_from).strip():
                query_parts.append(f"opened_at>={date_from}")
        
        if 'date_to' in filters:
            date_to = filters['date_to']
            if date_to is not None and str(date_to).strip():
                query_parts.append(f"opened_at<={date_to}")
        
        # Additional filters for assignment
        if 'assignment_group' in filters:
            assignment_group = filters['assignment_group']
            if assignment_group is not None and str(assignment_group).strip():
                query_parts.append(f"assignment_group={assignment_group}")
        
        if 'assigned_to' in filters:
            assigned_to = filters['assigned_to']
            if assigned_to is not None and str(assigned_to).strip():
                query_parts.append(f"assigned_to={assigned_to}")
        
        # Combine query parts with AND logic
        query = '^'.join(query_parts) if query_parts else ''
        
        endpoint = "/api/now/table/sc_request"
        params = {}
        if query:
            params['sysparm_query'] = query
        
        # Add pagination support with validation
        if 'limit' in filters:
            limit = filters['limit']
            if limit is not None:
                try:
                    limit_int = int(limit)
                    if limit_int < 0:
                        raise ValidationError(
                            "Limit must be non-negative",
                            field_name="limit",
                            invalid_value=limit
                        )
                    params['sysparm_limit'] = limit_int
                except (ValueError, TypeError):
                    raise ValidationError(
                        "Limit must be a valid integer",
                        field_name="limit",
                        invalid_value=limit
                    )
        
        if 'offset' in filters:
            offset = filters['offset']
            if offset is not None:
                try:
                    offset_int = int(offset)
                    if offset_int < 0:
                        raise ValidationError(
                            "Offset must be non-negative",
                            field_name="offset",
                            invalid_value=offset
                        )
                    params['sysparm_offset'] = offset_int
                except (ValueError, TypeError):
                    raise ValidationError(
                        "Offset must be a valid integer",
                        field_name="offset",
                        invalid_value=offset
                    )
        
        # Use streaming request
        stream_response = self._make_request("GET", endpoint, params=params, stream=True)
        
        # Yield each item from the stream
        for item in stream_response:
            yield item
    
    def get_all_requests_stream(
        self, 
        batch_size: int = 1000,
        fields: Optional[List[str]] = None
    ) -> Iterator[Dict[str, Any]]:
        """Stream all Service Requests in batches for memory-efficient processing.
        
        This method fetches Service Requests in batches and yields them one at a time,
        making it suitable for processing large datasets without memory issues.
        
        Args:
            batch_size: Number of records to fetch per batch (default: 1000)
            fields: Specific fields to retrieve (None for all fields)
            
        Yields:
            Dict: Individual Service Request dictionaries
            
        Raises:
            ValidationError: If batch_size is invalid
            ServiceNowAPIError: If retrieval fails
        """
        if batch_size <= 0:
            raise ValidationError(
                "Batch size must be positive",
                field_name="batch_size",
                invalid_value=batch_size
            )
        
        offset = 0
        
        while True:
            endpoint = "/api/now/table/sc_request"
            params = {
                'sysparm_limit': batch_size,
                'sysparm_offset': offset
            }
            
            if fields:
                if not isinstance(fields, list):
                    raise ValidationError(
                        "Fields must be a list of strings",
                        field_name="fields",
                        invalid_value=type(fields).__name__
                    )
                params['sysparm_fields'] = ','.join(fields)
            
            try:
                response_data = self._make_request("GET", endpoint, params=params)
                
                if 'result' in response_data:
                    results = response_data['result']
                    
                    # If no results, we've reached the end
                    if not results:
                        break
                    
                    # Yield each result
                    for item in results:
                        yield item
                    
                    # If we got fewer results than batch_size, we've reached the end
                    if len(results) < batch_size:
                        break
                    
                    offset += batch_size
                else:
                    raise ServiceNowAPIError(
                        "Unexpected response format from ServiceNow",
                        response_data=response_data
                    )
                    
            except Exception as e:
                # Re-raise ServiceNow-specific errors
                if isinstance(e, (ServiceNowAPIError, ValidationError, AuthenticationError, ConnectionError)):
                    raise
                # Wrap other errors
                raise ServiceNowAPIError(f"Error during streaming: {str(e)}")
    
    def export_requests_stream(
        self,
        filters: Optional[Dict[str, Any]] = None,
        format_type: str = "json"
    ) -> Iterator[Union[Dict[str, Any], str]]:
        """Export Service Requests in streaming format for large datasets.
        
        This method provides memory-efficient export of Service Request data
        in JSON or CSV format, suitable for large datasets.
        
        Args:
            filters: Optional search criteria (same as search_requests method)
            format_type: Export format ("json" or "csv")
            
        Yields:
            Union[Dict, str]: Service Request data in specified format
                - For JSON: yields Dict objects
                - For CSV: yields string lines (header first, then data rows)
            
        Raises:
            ValidationError: If format_type is invalid or filters are malformed
            ServiceNowAPIError: If export fails
        """
        if format_type not in ["json", "csv"]:
            raise ValidationError(
                f"Invalid format_type: {format_type}. Must be 'json' or 'csv'",
                field_name="format_type",
                invalid_value=format_type
            )
        
        # Use streaming search if filters provided, otherwise stream all
        if filters:
            stream = self.search_requests_stream(filters)
        else:
            stream = self.get_all_requests_stream()
        
        if format_type == "json":
            for item in stream:
                yield item
        elif format_type == "csv":
            # Yield CSV header first
            first_item = next(stream, None)
            if first_item:
                headers = list(first_item.keys())
                yield ",".join(headers)
                
                # Yield first item
                values = [str(first_item.get(h, "")).replace('"', '""') for h in headers]
                yield ",".join(f'"{v}"' for v in values)
                
                # Yield remaining items
                for item in stream:
                    values = [str(item.get(h, "")).replace('"', '""') for h in headers]
                    yield ",".join(f'"{v}"' for v in values)
    
    def is_authenticated(self) -> bool:
        """Check if client is authenticated.
        
        Returns:
            bool: True if authenticated
        """
        return self._authenticated
    
    def order_catalog_item(self, sys_id: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Order a catalog item using the Service Catalog API.
        
        Args:
            sys_id: Catalog item sys_id
            variables: Variables for the catalog item order
            
        Returns:
            Dict containing order information and request details
            
        Raises:
            ValidationError: If sys_id is invalid
            ResourceNotFoundError: If catalog item not found
            ServiceNowAPIError: If order fails
        """
        if not sys_id:
            raise ValidationError(
                "Catalog item sys_id cannot be empty",
                field_name="sys_id",
                invalid_value=sys_id
            )
        
        endpoint = f"/api/sn_sc/servicecatalog/items/{sys_id}/order_now"
        data = {"variables": variables or {}}
        
        response_data = self._make_request("POST", endpoint, data=data)
        
        if 'result' in response_data:
            return response_data['result']
        else:
            raise ServiceNowAPIError(
                "Unexpected response format from ServiceNow",
                response_data=response_data
            )
    
    def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            self.session.close()