#!/usr/bin/env python3
"""
Example script demonstrating Service Catalog API usage.

This script shows how to order catalog items using the ServiceNow MCP Server.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from servicenow_mcp.client.servicenow_client import ServiceNowClient
from servicenow_mcp.config.settings import ServiceNowConfig


def main():
    """Demonstrate Service Catalog API functionality."""
    
    # Load configuration from environment
    try:
        config = ServiceNowConfig()
        print(f"Connecting to ServiceNow instance: {config.instance_url}")
    except Exception as e:
        print(f"Configuration error: {e}")
        print("Please ensure your .env file is configured with ServiceNow credentials.")
        return 1
    
    # Create and authenticate client
    client = ServiceNowClient(config)
    
    try:
        print("Authenticating with ServiceNow...")
        client.authenticate()
        print("✓ Authentication successful")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return 1
    
    # Example: Order a catalog item
    try:
        print("\n--- Service Catalog API Demo ---")
        
        # Note: Replace with actual catalog item sys_id from your ServiceNow instance
        catalog_item_sys_id = "example_catalog_item_sys_id"
        
        # Example variables for the catalog item
        variables = {
            "quantity": "1",
            "requested_for": "",  # Leave empty to use current user
            "justification": "Demo order from ServiceNow MCP Server"
        }
        
        print(f"Ordering catalog item: {catalog_item_sys_id}")
        print(f"Variables: {variables}")
        
        # This would fail with the example sys_id, but shows the API usage
        # result = client.order_catalog_item(catalog_item_sys_id, variables)
        # print(f"✓ Order successful: {result.get('request_number', 'Unknown')}")
        
        print("Note: Replace 'catalog_item_sys_id' with a real sys_id to test ordering")
        
    except Exception as e:
        print(f"Catalog order failed: {e}")
    
    finally:
        client.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
