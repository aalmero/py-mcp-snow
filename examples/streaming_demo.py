#!/usr/bin/env python3
"""
Demonstration of ServiceNow MCP Server streaming capabilities.

This script shows how to use the streaming HTTP features for processing
large ServiceNow datasets efficiently.
"""

import sys
import os
from typing import Iterator, Dict, Any

# Add src to path for demo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from servicenow_mcp.streaming.http_streaming import StreamingHTTPHandler, StreamingFormat
from servicenow_mcp.streaming.mcp_streaming import StreamingMCPTools
from servicenow_mcp.client.servicenow_client import ServiceNowClient
from servicenow_mcp.config.settings import ServiceNowConfig


def generate_sample_data(count: int = 1000) -> Iterator[Dict[str, Any]]:
    """Generate sample Service Request data for demonstration.
    
    Args:
        count: Number of sample records to generate
        
    Yields:
        Dict: Sample Service Request data
    """
    for i in range(count):
        yield {
            "sys_id": f"sample-{i:06d}",
            "number": f"REQ{i:07d}",
            "short_description": f"Sample request {i + 1}",
            "description": f"This is a sample Service Request for demonstration purposes. Request ID: {i + 1}",
            "state": str((i % 4) + 1),  # States 1-4
            "priority": str((i % 5) + 1),  # Priorities 1-5
            "requested_for": f"user-{i % 10}",  # 10 different users
            "opened_by": f"admin-{i % 3}",  # 3 different admins
            "opened_at": f"2024-01-{(i % 28) + 1:02d} 10:00:00",
            "updated_at": f"2024-01-{(i % 28) + 1:02d} 15:30:00"
        }


def demo_streaming_formats():
    """Demonstrate different streaming formats."""
    print("🌊 ServiceNow MCP Server - Streaming Demo")
    print("=" * 50)
    
    # Initialize streaming handler
    streaming_handler = StreamingHTTPHandler()
    
    # Generate sample data
    sample_count = 100
    print(f"\n📊 Generating {sample_count} sample Service Requests...")
    
    # Demo JSON streaming
    print("\n1️⃣ JSON Streaming Format:")
    print("-" * 30)
    
    data_iter = generate_sample_data(5)  # Small sample for demo
    json_response = streaming_handler.create_streaming_response(
        data=data_iter,
        format_type=StreamingFormat.JSON,
        metadata={"demo": "json_format", "count": 5}
    )
    
    print(f"Content-Type: {json_response.content_type}")
    print("Sample output:")
    
    # Show first few chunks
    chunks = list(json_response.data)
    output = "".join(chunks[:3]) + "..." if len(chunks) > 3 else "".join(chunks)
    print(output[:200] + "..." if len(output) > 200 else output)
    
    # Demo NDJSON streaming
    print("\n2️⃣ NDJSON Streaming Format:")
    print("-" * 30)
    
    data_iter = generate_sample_data(3)
    ndjson_response = streaming_handler.create_streaming_response(
        data=data_iter,
        format_type=StreamingFormat.NDJSON,
        metadata={"demo": "ndjson_format", "count": 3}
    )
    
    print(f"Content-Type: {ndjson_response.content_type}")
    print("Sample output:")
    
    lines = list(ndjson_response.data)
    for i, line in enumerate(lines[:2]):
        print(f"Line {i + 1}: {line.strip()}")
    
    # Demo CSV streaming
    print("\n3️⃣ CSV Streaming Format:")
    print("-" * 30)
    
    data_iter = generate_sample_data(3)
    csv_response = streaming_handler.create_streaming_response(
        data=data_iter,
        format_type=StreamingFormat.CSV,
        metadata={"demo": "csv_format", "count": 3}
    )
    
    print(f"Content-Type: {csv_response.content_type}")
    print("Sample output:")
    
    csv_lines = list(csv_response.data)
    for i, line in enumerate(csv_lines[:3]):
        print(f"Row {i + 1}: {line.strip()}")
    
    # Demo response size estimation
    print("\n4️⃣ Response Size Estimation:")
    print("-" * 30)
    
    sample_item = next(generate_sample_data(1))
    
    for format_type in [StreamingFormat.JSON, StreamingFormat.NDJSON, StreamingFormat.CSV]:
        estimated_size = streaming_handler.estimate_response_size(
            sample_item=sample_item,
            total_count=10000,
            format_type=format_type
        )
        print(f"{format_type.value.upper()}: ~{estimated_size:,} bytes for 10,000 records")


def demo_memory_efficiency():
    """Demonstrate memory efficiency of streaming."""
    print("\n💾 Memory Efficiency Demo:")
    print("-" * 30)
    
    print("Streaming allows processing of large datasets without loading all data into memory.")
    print("Each record is processed individually as it's generated/received.")
    print("\nExample: Processing 1 million records")
    print("- Traditional: Load 1M records → ~500MB+ memory usage")
    print("- Streaming: Process 1 record at a time → ~1KB memory usage")
    print("\nThis enables:")
    print("• Processing datasets larger than available RAM")
    print("• Real-time data processing")
    print("• Reduced server resource requirements")
    print("• Better scalability for concurrent users")


def demo_use_cases():
    """Demonstrate practical use cases for streaming."""
    print("\n🎯 Practical Use Cases:")
    print("-" * 30)
    
    use_cases = [
        {
            "title": "Large Data Export",
            "description": "Export 100,000+ Service Requests for reporting",
            "format": "CSV",
            "benefit": "Memory-efficient export without server timeouts"
        },
        {
            "title": "Real-time Monitoring",
            "description": "Stream live updates of Service Request changes",
            "format": "NDJSON",
            "benefit": "Immediate processing of updates as they occur"
        },
        {
            "title": "Batch Processing",
            "description": "Update thousands of requests in batches",
            "format": "JSON",
            "benefit": "Progress tracking and error handling per batch"
        },
        {
            "title": "Data Migration",
            "description": "Migrate Service Requests between systems",
            "format": "NDJSON",
            "benefit": "Reliable transfer of large datasets"
        }
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"{i}. {use_case['title']}")
        print(f"   Description: {use_case['description']}")
        print(f"   Format: {use_case['format']}")
        print(f"   Benefit: {use_case['benefit']}")
        print()


def main():
    """Run the streaming demonstration."""
    try:
        demo_streaming_formats()
        demo_memory_efficiency()
        demo_use_cases()
        
        print("\n🎉 Streaming Demo Complete!")
        print("\nNext Steps:")
        print("1. Configure your ServiceNow credentials in .env")
        print("2. Run the MCP server: uv run servicenow-mcp-server")
        print("3. Use streaming tools for large dataset operations")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())