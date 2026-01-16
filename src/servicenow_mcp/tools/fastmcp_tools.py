"""FastMCP tools for ServiceNow operations."""

from typing import Dict, Any, Optional, List
import json

from fastmcp import FastMCP
from ..client.servicenow_client import ServiceNowClient
from ..exceptions import ServiceNowMCPError, ValidationError, format_error_response
from ..utils.logging import get_logger


# Global FastMCP instance
mcp = FastMCP("ServiceNow MCP Server")

# Global client instance (will be initialized by server)
servicenow_client: Optional[ServiceNowClient] = None

def initialize_tools(client: ServiceNowClient) -> None:
    """Initialize the global client instances for tools.
    
    Args:
        client: Authenticated ServiceNow client
    """
    global servicenow_client
    servicenow_client = client
    
    logger = get_logger()
    logger.info("FastMCP tools initialized with ServiceNow client")


@mcp.tool
def create_service_request(
    short_description: str,
    description: str = "",
    requested_for: str = "",
    priority: str = "3"
) -> Dict[str, Any]:
    """Create a new Service Request in ServiceNow.
    
    Args:
        short_description: Brief summary of the request (required)
        description: Detailed description of the request
        requested_for: User sys_id or username for whom the request is made
        priority: Priority level (1=Critical, 2=High, 3=Moderate, 4=Low, 5=Planning)
    
    Returns:
        Dictionary with request number, sys_id, and created request data
    """
    logger = get_logger()
    logger.info(f"Creating Service Request: {short_description}")
    
    try:
        if not servicenow_client:
            raise ServiceNowMCPError("ServiceNow client not initialized")
        
        # Authenticate if not already done
        if not servicenow_client.is_authenticated():
            servicenow_client.authenticate()
        
        # Create the request
        request_data = {
            "short_description": short_description,
            "description": description,
            "requested_for": requested_for,
            "priority": priority
        }
        
        result = servicenow_client.create_request(request_data)
        
        logger.info(f"Service Request created: {result.get('number', 'Unknown')}")
        
        return {
            "success": True,
            "data": result,
            "message": f"Service Request {result.get('number', 'created')} successfully created"
        }
        
    except Exception as e:
        logger.error(f"Failed to create Service Request: {e}")
        if isinstance(e, ServiceNowMCPError):
            return format_error_response(e)
        return {
            "success": False,
            "error": str(e),
            "error_code": "CREATE_REQUEST_ERROR"
        }


@mcp.tool
def get_service_request(
    identifier: str,
    id_type: str = "sys_id"
) -> Dict[str, Any]:
    """Retrieve a Service Request by sys_id or request number.
    
    Args:
        identifier: The sys_id or request number to retrieve
        id_type: Type of identifier ("sys_id" or "number")
    
    Returns:
        Dictionary containing the Service Request data
    """
    logger = get_logger()
    logger.info(f"Retrieving Service Request: {identifier} (type: {id_type})")
    
    try:
        if not servicenow_client:
            raise ServiceNowMCPError("ServiceNow client not initialized")
        
        # Authenticate if not already done
        if not servicenow_client.is_authenticated():
            servicenow_client.authenticate()
        
        result = servicenow_client.get_request(identifier, id_type)
        
        logger.info(f"Service Request retrieved: {result.get('number', 'Unknown')}")
        
        return {
            "success": True,
            "data": result,
            "message": f"Service Request {result.get('number', identifier)} retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve Service Request: {e}")
        if isinstance(e, ServiceNowMCPError):
            return format_error_response(e)
        return {
            "success": False,
            "error": str(e),
            "error_code": "GET_REQUEST_ERROR"
        }


@mcp.tool
def update_service_request(
    sys_id: str,
    state: Optional[str] = None,
    priority: Optional[str] = None,
    assignment_group: Optional[str] = None,
    assigned_to: Optional[str] = None,
    work_notes: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing Service Request.
    
    Args:
        sys_id: The sys_id of the Service Request to update
        state: New state (1=New, 2=In Progress, 3=Resolved, 4=Closed, 6=Cancelled)
        priority: New priority (1=Critical, 2=High, 3=Moderate, 4=Low, 5=Planning)
        assignment_group: sys_id of the assignment group
        assigned_to: sys_id of the assigned user
        work_notes: Additional work notes to add
    
    Returns:
        Dictionary containing the updated Service Request data
    """
    logger = get_logger()
    logger.info(f"Updating Service Request: {sys_id}")
    
    try:
        if not servicenow_client:
            raise ServiceNowMCPError("ServiceNow client not initialized")
        
        # Authenticate if not already done
        if not servicenow_client.is_authenticated():
            servicenow_client.authenticate()
        
        # Build update data from provided parameters
        update_data = {}
        if state is not None:
            update_data["state"] = state
        if priority is not None:
            update_data["priority"] = priority
        if assignment_group is not None:
            update_data["assignment_group"] = assignment_group
        if assigned_to is not None:
            update_data["assigned_to"] = assigned_to
        if work_notes is not None:
            update_data["work_notes"] = work_notes
        
        if not update_data:
            raise ValidationError("At least one field must be provided for update")
        
        result = servicenow_client.update_request(sys_id, update_data)
        
        logger.info(f"Service Request updated: {result.get('number', 'Unknown')}")
        
        return {
            "success": True,
            "data": result,
            "message": f"Service Request {result.get('number', sys_id)} updated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to update Service Request: {e}")
        if isinstance(e, ServiceNowMCPError):
            return format_error_response(e)
        return {
            "success": False,
            "error": str(e),
            "error_code": "UPDATE_REQUEST_ERROR"
        }


@mcp.tool
def search_service_requests(
    status: Optional[str] = None,
    requested_for: Optional[str] = None,
    opened_by: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    assignment_group: Optional[str] = None,
    assigned_to: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None
) -> Dict[str, Any]:
    """Search Service Requests with multiple criteria.
    
    Args:
        status: Service Request state to filter by
        requested_for: User sys_id or username to filter by
        opened_by: User sys_id or username who opened the request
        date_from: Start date for opened_at filter (YYYY-MM-DD format)
        date_to: End date for opened_at filter (YYYY-MM-DD format)
        assignment_group: Assignment group sys_id to filter by
        assigned_to: Assigned user sys_id to filter by
        limit: Maximum number of results to return
        offset: Number of results to skip for pagination
    
    Returns:
        Dictionary containing list of matching Service Requests
    """
    logger = get_logger()
    logger.info("Searching Service Requests with filters")
    
    try:
        if not servicenow_client:
            raise ServiceNowMCPError("ServiceNow client not initialized")
        
        # Authenticate if not already done
        if not servicenow_client.is_authenticated():
            servicenow_client.authenticate()
        
        # Build filters from provided parameters
        filters = {}
        if status is not None:
            filters["status"] = status
        if requested_for is not None:
            filters["requested_for"] = requested_for
        if opened_by is not None:
            filters["opened_by"] = opened_by
        if date_from is not None:
            filters["date_from"] = date_from
        if date_to is not None:
            filters["date_to"] = date_to
        if assignment_group is not None:
            filters["assignment_group"] = assignment_group
        if assigned_to is not None:
            filters["assigned_to"] = assigned_to
        if limit is not None:
            filters["limit"] = limit
        if offset is not None:
            filters["offset"] = offset
        
        results = servicenow_client.search_requests(filters)
        
        logger.info(f"Search returned {len(results)} Service Requests")
        
        return {
            "success": True,
            "data": results,
            "count": len(results),
            "message": f"Found {len(results)} Service Requests matching criteria"
        }
        
    except Exception as e:
        logger.error(f"Failed to search Service Requests: {e}")
        if isinstance(e, ServiceNowMCPError):
            return format_error_response(e)
        return {
            "success": False,
            "error": str(e),
            "error_code": "SEARCH_REQUESTS_ERROR"
        }


@mcp.tool
def order_catalog_item(
    sys_id: str,
    variables: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Order a catalog item using the Service Catalog API.
    
    Args:
        sys_id: The sys_id of the catalog item to order
        variables: Dictionary of variables for the catalog item (optional)
    
    Returns:
        Dictionary containing order information and request details
    """
    logger = get_logger()
    logger.info(f"Ordering catalog item: {sys_id}")
    
    try:
        if not servicenow_client:
            raise ServiceNowMCPError("ServiceNow client not initialized")
        
        # Authenticate if not already done
        if not servicenow_client.is_authenticated():
            servicenow_client.authenticate()
        
        result = servicenow_client.order_catalog_item(sys_id, variables)
        
        logger.info(f"Catalog item ordered successfully: {sys_id}")
        
        return {
            "success": True,
            "data": result,
            "message": f"Catalog item {sys_id} ordered successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to order catalog item: {e}")
        if isinstance(e, ServiceNowMCPError):
            return format_error_response(e)
        return {
            "success": False,
            "error": str(e),
            "error_code": "ORDER_CATALOG_ITEM_ERROR"
        }


@mcp.tool
def get_server_info() -> Dict[str, Any]:
    """Get information about the ServiceNow MCP Server.
    
    Returns:
        Dictionary containing server information and capabilities
    """
    logger = get_logger()
    logger.info("Retrieving server information")
    
    try:
        server_info = {
            "name": "ServiceNow MCP Server",
            "version": "0.1.0",
            "description": "MCP server for ServiceNow Service Request management",
            "capabilities": {
                "service_requests": {
                    "create": True,
                    "read": True,
                    "update": True,
                    "search": True
                },
                "authentication": {
                    "basic_auth": True,
                    "api_key": True,
                    "oauth": False
                }
            },
            "tools": [
                "create_service_request",
                "get_service_request", 
                "update_service_request",
                "search_service_requests",
                "order_catalog_item",
                "get_server_info"
            ],
            "status": "ready" if servicenow_client and servicenow_client.is_authenticated() else "not_authenticated"
        }
        
        return {
            "success": True,
            "data": server_info,
            "message": "Server information retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to get server info: {e}")
        return {
            "success": False,
            "error": str(e),
            "error_code": "SERVER_INFO_ERROR"
        }