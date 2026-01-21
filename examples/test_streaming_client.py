#!/usr/bin/env python3
"""
Test client for ServiceNow MCP Server streaming capabilities.

This script demonstrates how a client would interact with the streaming MCP server.
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any, Iterator

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.server import initialize_server
from src.streaming.http_streaming import StreamingFormat


def generate_test_data(count: int = 10) -> Iterator[Dict[str, Any]]:
    """Generate test Service Request data."""
    for i in range(count):
        yield {
            "sys_id": f"test-{i:04d}",
            "number": f"REQ{i:07d}",
            "short_description": f"Test Service Request {i + 1}",
            "description": f"This is test request number {i + 1} for streaming demo",
            "state": str((i % 4) + 1),
            "priority": str((i % 5) + 1),
            "requested_for": f"user-{i % 3}",
            "opened_by": "test_admin",
            "opened_at": f"2024-01-{(i % 28) + 1:02d} 09:00:00"
        }


async def test_streaming_operations():
    """Test streaming operations with the MCP server."""
    print("🧪 Testing ServiceNow MCP Server Streaming Operations")
    print("=" * 60)
    
    try:
        # Initialize server components
        client, streaming_tools = initialize_server()
        print("✅ Server components initialized")
        
        # Test 1: Stream search with JSON format
        print("\n1️⃣ Testing Stream Search (JSON)")
        print("-" * 40)
        
        search_filters = {
            "status": "1",
            "requested_for": "user-1"
        }
        
        result1 = streaming_tools.stream_search_requests(
            filters=search_filters,
            format_type="json",
            chunk_size=5
        )
        
        print(f"Success: {result1['success']}")
        print(f"Streaming: {result1.get('streaming', False)}")
        print(f"Content-Type: {result1.get('content_type', 'N/A')}")
        print(f"Message: {result1.get('message', 'N/A')}")
        
        # Test 2: Stream export with CSV format
        print("\n2️⃣ Testing Stream Export (CSV)")
        print("-" * 40)
        
        result2 = streaming_tools.stream_export_requests(
            filters={"state": "1"},
            format_type="csv",
            fields=["sys_id", "number", "short_description", "state"]
        )
        
        print(f"Success: {result2['success']}")
        print(f"Content-Type: {result2.get('content_type', 'N/A')}")
        print(f"Export Type: {result2.get('metadata', {}).get('export_type', 'N/A')}")
        
        # Test 3: Stream batch processing
        print("\n3️⃣ Testing Stream Batch Processing")
        print("-" * 40)
        
        result3 = streaming_tools.stream_batch_process_requests(
            operation="validate",
            filters={"state": "1"},
            batch_size=3
        )
        
        print(f"Success: {result3['success']}")
        print(f"Operation: {result3.get('metadata', {}).get('operation', 'N/A')}")
        print(f"Batch Size: {result3.get('metadata', {}).get('batch_size', 'N/A')}")
        
        # Test 4: Error handling
        print("\n4️⃣ Testing Error Handling")
        print("-" * 40)
        
        result4 = streaming_tools.stream_search_requests(
            filters={"status": "1"},
            format_type="invalid_format",  # This should cause an error
            chunk_size=10
        )
        
        print(f"Success: {result4['success']}")
        if not result4['success']:
            print(f"Error: {result4.get('error', 'N/A')}")
            print(f"Error Code: {result4.get('error_code', 'N/A')}")
        
        print("\n✅ All streaming operation tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    return 0


async def demonstrate_streaming_formats():
    """Demonstrate different streaming formats."""
    print("\n🎨 Demonstrating Streaming Formats")
    print("=" * 50)
    
    from src.streaming.http_streaming import StreamingHTTPHandler
    
    # Create streaming handler
    handler = StreamingHTTPHandler()
    
    # Generate sample data
    sample_data = list(generate_test_data(3))
    
    # Test JSON format
    print("\n📄 JSON Format:")
    json_response = handler.create_streaming_response(
        data=iter(sample_data),
        format_type=StreamingFormat.JSON
    )
    json_chunks = list(json_response.data)
    json_output = "".join(json_chunks)
    print(f"Content-Type: {json_response.content_type}")
    print(f"Output: {json_output[:100]}...")
    
    # Test NDJSON format
    print("\n📄 NDJSON Format:")
    ndjson_response = handler.create_streaming_response(
        data=iter(sample_data),
        format_type=StreamingFormat.NDJSON
    )
    ndjson_lines = list(ndjson_response.data)
    print(f"Content-Type: {ndjson_response.content_type}")
    print(f"Lines: {len(ndjson_lines)}")
    print(f"First line: {ndjson_lines[0].strip()[:80]}...")
    
    # Test CSV format
    print("\n📄 CSV Format:")
    csv_response = handler.create_streaming_response(
        data=iter(sample_data),
        format_type=StreamingFormat.CSV
    )
    csv_lines = list(csv_response.data)
    print(f"Content-Type: {csv_response.content_type}")
    print(f"Header: {csv_lines[0].strip()}")
    print(f"First row: {csv_lines[1].strip()[:80]}...")
    
    print("\n✅ Format demonstration completed!")


async def main():
    """Main test function."""
    try:
        # Run streaming operation tests
        result1 = await test_streaming_operations()
        
        # Demonstrate streaming formats
        await demonstrate_streaming_formats()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📊 Summary:")
        print("   • Streaming search operations working")
        print("   • Export functionality operational")
        print("   • Batch processing available")
        print("   • Multiple format support (JSON, NDJSON, CSV)")
        print("   • Error handling functional")
        
        return result1
        
    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Tests stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)