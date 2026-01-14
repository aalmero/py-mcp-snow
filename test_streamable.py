#!/usr/bin/env python3
"""Test script for streamable HTTP server."""

import asyncio
import sys
import os
from fastmcp import Client


async def test_server():
    """Test the streamable HTTP server."""
    # Allow port override via environment variable
    port = os.environ.get("MCP_PORT", "8000")
    url = f"http://127.0.0.1:{port}/mcp"
    
    print(f"Connecting to ServiceNow MCP Server at {url}...")
    
    try:
        client = Client(url)
        
        async with client:
            # Test ping
            print("Testing ping...")
            await client.ping()
            print("✅ Ping successful!")
            
            # List available tools
            print("\nListing available tools...")
            tools = await client.list_tools()
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   • {tool.name}: {tool.description}")
            
            # Test get_server_info tool
            print("\nTesting get_server_info tool...")
            result = await client.call_tool("get_server_info", {})
            print(f"✅ Server info retrieved successfully")
            print(f"   Result: {result}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_server())
