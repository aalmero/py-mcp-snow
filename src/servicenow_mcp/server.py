"""Main server module for ServiceNow MCP Server."""

import sys
import argparse
from typing import Optional

from .config.settings import load_servicenow_config, load_server_config
from .utils.logging import setup_logging, get_logger
from .exceptions import ConfigurationError, ServiceNowMCPError
from .client.servicenow_client import ServiceNowClient
from .streaming import StreamingMCPTools
from .tools import mcp, initialize_tools


# Global instances for MCP tools
servicenow_client: Optional[ServiceNowClient] = None
streaming_tools: Optional[StreamingMCPTools] = None


def initialize_server() -> tuple[ServiceNowClient, StreamingMCPTools]:
    """Initialize ServiceNow client and streaming tools.
    
    Returns:
        Tuple of (ServiceNowClient, StreamingMCPTools)
        
    Raises:
        ConfigurationError: If configuration is invalid
        ServiceNowMCPError: If initialization fails
    """
    global servicenow_client, streaming_tools
    
    if servicenow_client is not None and streaming_tools is not None:
        return servicenow_client, streaming_tools
    
    # Load configurations
    server_config = load_server_config()
    servicenow_config = load_servicenow_config()
    
    # Set up logging
    logger = setup_logging(server_config)
    logger.info("Initializing ServiceNow MCP Server components...")
    
    # Initialize ServiceNow client
    servicenow_client = ServiceNowClient(servicenow_config)
    logger.info("ServiceNow client initialized")
    
    # Initialize streaming MCP tools
    streaming_tools = StreamingMCPTools(servicenow_client)
    logger.info("Streaming MCP tools initialized")
    
    # Initialize FastMCP tools with clients
    initialize_tools(servicenow_client, streaming_tools)
    logger.info("FastMCP tools initialized")
    
    logger.info("ServiceNow MCP Server components ready")
    return servicenow_client, streaming_tools


def run_fastmcp_server(transport: str = "stdio", host: str = "127.0.0.1", port: int = 8000):
    """Run the FastMCP server with ServiceNow integration.
    
    Args:
        transport: Transport type ("stdio" or "streamable-http")
        host: Host address for HTTP transport
        port: Port number for HTTP transport
    """
    try:
        # Initialize components
        client, tools = initialize_server()
        
        logger = get_logger()
        logger.info(f"🚀 Starting ServiceNow MCP Server with {transport} transport...")
        
        # Test authentication
        logger.info("Testing ServiceNow authentication...")
        try:
            if client.authenticate():
                logger.info("✅ ServiceNow authentication successful")
            else:
                logger.error("❌ ServiceNow authentication failed")
        except Exception as e:
            logger.warning(f"⚠️ ServiceNow authentication test failed: {e}")
            logger.info("Server will continue - authentication will be retried on first request")
        
        # Log available tools
        logger.info("🔧 FastMCP tools registered:")
        logger.info("   • create_service_request - Create new Service Requests")
        logger.info("   • get_service_request - Retrieve Service Request by ID")
        logger.info("   • update_service_request - Update existing Service Requests")
        logger.info("   • search_service_requests - Search with multiple criteria")
        logger.info("   • stream_search_service_requests - Memory-efficient streaming search")
        logger.info("   • stream_export_service_requests - Large dataset export")
        logger.info("   • get_server_info - Server capabilities and status")
        
        logger.info("🌊 Streaming HTTP support enabled")
        logger.info("📊 Supported formats: JSON, NDJSON, CSV, TEXT")
        
        logger.info("🎯 ServiceNow MCP Server ready for connections!")
        
        # Run FastMCP server with specified transport
        if transport == "stdio":
            mcp.run(transport="stdio")
        elif transport == "streamable-http":
            mcp.run(
                transport="streamable-http",
                host=host,
                port=port,
                path="/mcp"
            )
        else:
            raise ValueError(f"Unsupported transport: {transport}")
        
    except (ConfigurationError, ServiceNowMCPError) as e:
        logger = get_logger()
        logger.error(f"Server error: {e.message}")
        return 1
    except Exception as e:
        logger = get_logger()
        logger.error(f"Unexpected error: {str(e)}")
        return 1


def main() -> None:
    """Main entry point for the ServiceNow MCP Server."""
    parser = argparse.ArgumentParser(
        description="ServiceNow MCP Server - Model Context Protocol server for ServiceNow"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "streamable-http"],
        default="stdio",
        help="Transport type (default: stdio)"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address for HTTP transport (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port number for HTTP transport (default: 8000)"
    )
    
    args = parser.parse_args()
    
    try:
        # Run the FastMCP server
        run_fastmcp_server(
            transport=args.transport,
            host=args.host,
            port=args.port
        )
        
    except KeyboardInterrupt:
        print("\n👋 ServiceNow MCP Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed to start server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()