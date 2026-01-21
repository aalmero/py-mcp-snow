#!/usr/bin/env python3
"""
ServiceNow MCP Server with Streaming HTTP - Interactive Demo

This script demonstrates the MCP server running with streaming HTTP capabilities.
It simulates MCP tool calls and shows streaming responses.
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any

# Add src to path for demo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.server import initialize_server
from src.streaming.http_streaming import StreamingFormat
from src.utils.logging import setup_logging, get_logger
from src.config.settings import load_server_config


async def simulate_mcp_tool_call(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Simulate an MCP tool call with streaming response.
    
    Args:
        tool_name: Name of the MCP tool to call
        parameters: Tool parameters
        
    Returns:
        Dict: MCP tool response
    """
    logger = get_logger()
    logger.info(f"🔧 MCP Tool Call: {tool_name}")
    logger.info(f"📋 Parameters: {json.dumps(parameters, indent=2)}")
    
    try:
        # Initialize server components
        client, streaming_tools = initialize_server()
        
        # Route to appropriate streaming tool
        if tool_name == "stream_search_requests":
            response = streaming_tools.stream_search_requests(
                filters=parameters.get("filters", {}),
                format_type=parameters.get("format_type", "json"),
                chunk_size=parameters.get("chunk_size", 100)
            )
        elif tool_name == "stream_export_requests":
            response = streaming_tools.stream_export_requests(
                filters=parameters.get("filters"),
                format_type=parameters.get("format_type", "json"),
                fields=parameters.get("fields")
            )
        elif tool_name == "stream_batch_process_requests":
            response = streaming_tools.stream_batch_process_requests(
                operation=parameters.get("operation", "validate"),
                filters=parameters.get("filters", {}),
                batch_size=parameters.get("batch_size", 100),
                update_data=parameters.get("update_data")
            )
        else:
            response = {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "error_code": "UNKNOWN_TOOL"
            }
        
        logger.info(f"✅ Tool Response: {json.dumps(response, indent=2)}")
        return response
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": str(e),
            "error_code": "TOOL_EXECUTION_ERROR"
        }
        logger.error(f"❌ Tool Error: {json.dumps(error_response, indent=2)}")
        return error_response


async def demo_streaming_tools():
    """Demonstrate streaming MCP tools."""
    logger = get_logger()
    
    print("🌊 ServiceNow MCP Server - Streaming Tools Demo")
    print("=" * 60)
    
    # Demo 1: Stream search requests
    print("\n1️⃣ Streaming Search Requests")
    print("-" * 40)
    
    search_params = {
        "filters": {
            "status": "1",
            "date_from": "2024-01-01"
        },
        "format_type": "json",
        "chunk_size": 50
    }
    
    response1 = await simulate_mcp_tool_call("stream_search_requests", search_params)
    
    if response1.get("success"):
        print("✅ Streaming search configured successfully")
        print(f"📊 Content-Type: {response1.get('content_type')}")
        print(f"🔧 Metadata: {json.dumps(response1.get('metadata'), indent=2)}")
    else:
        print(f"❌ Search failed: {response1.get('error')}")
    
    await asyncio.sleep(1)
    
    # Demo 2: Stream export requests
    print("\n2️⃣ Streaming Export Requests")
    print("-" * 40)
    
    export_params = {
        "filters": None,  # Export all
        "format_type": "csv",
        "fields": ["sys_id", "number", "short_description", "state", "priority"]
    }
    
    response2 = await simulate_mcp_tool_call("stream_export_requests", export_params)
    
    if response2.get("success"):
        print("✅ Streaming export configured successfully")
        print(f"📊 Content-Type: {response2.get('content_type')}")
        print(f"📁 Export Type: {response2.get('metadata', {}).get('export_type')}")
        print(f"🏷️ Fields: {response2.get('metadata', {}).get('fields')}")
    else:
        print(f"❌ Export failed: {response2.get('error')}")
    
    await asyncio.sleep(1)
    
    # Demo 3: Stream batch processing
    print("\n3️⃣ Streaming Batch Processing")
    print("-" * 40)
    
    batch_params = {
        "operation": "validate",
        "filters": {
            "state": "1"
        },
        "batch_size": 25
    }
    
    response3 = await simulate_mcp_tool_call("stream_batch_process_requests", batch_params)
    
    if response3.get("success"):
        print("✅ Streaming batch processing configured successfully")
        print(f"📊 Content-Type: {response3.get('content_type')}")
        print(f"⚙️ Operation: {response3.get('metadata', {}).get('operation')}")
        print(f"📦 Batch Size: {response3.get('metadata', {}).get('batch_size')}")
    else:
        print(f"❌ Batch processing failed: {response3.get('error')}")
    
    await asyncio.sleep(1)
    
    # Demo 4: Error handling
    print("\n4️⃣ Error Handling Demo")
    print("-" * 40)
    
    error_params = {
        "filters": "invalid",  # Invalid filters type
        "format_type": "json"
    }
    
    response4 = await simulate_mcp_tool_call("stream_search_requests", error_params)
    
    if not response4.get("success"):
        print("✅ Error handling working correctly")
        print(f"❌ Error: {response4.get('error')}")
        print(f"🏷️ Error Code: {response4.get('error_code')}")
    else:
        print("⚠️ Expected error but got success")


async def run_interactive_server():
    """Run interactive MCP server demo."""
    logger = get_logger()
    
    try:
        # Initialize server
        logger.info("🚀 Starting ServiceNow MCP Server with Streaming HTTP...")
        
        # Test server initialization
        client, streaming_tools = initialize_server()
        logger.info("✅ Server components initialized successfully")
        
        # Run streaming tools demo
        await demo_streaming_tools()
        
        print("\n🎉 Streaming Tools Demo Complete!")
        print("\n📋 Summary of Streaming Capabilities:")
        print("   • Memory-efficient processing of large datasets")
        print("   • Multiple output formats (JSON, CSV, NDJSON)")
        print("   • Configurable batch sizes and chunking")
        print("   • Real-time progress tracking")
        print("   • Comprehensive error handling")
        print("   • MCP protocol compatibility")
        
        print("\n🔧 Available MCP Tools:")
        print("   • stream_search_requests - Search with streaming response")
        print("   • stream_export_requests - Export large datasets")
        print("   • stream_batch_process_requests - Batch operations")
        
        print("\n💡 Next Steps:")
        print("   1. Integrate with FastMCP framework")
        print("   2. Add real ServiceNow authentication")
        print("   3. Deploy as production MCP server")
        
        # Keep server running for demonstration
        print("\n🖥️ Server running in demo mode...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Demo server stopped")
            return 0
            
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        return 1


async def main():
    """Main entry point for the demo."""
    # Set up logging
    try:
        server_config = load_server_config()
        setup_logging(server_config)
    except Exception:
        # Fallback logging setup
        import logging
        logging.basicConfig(level=logging.INFO)
    
    return await run_interactive_server()


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)