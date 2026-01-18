#!/usr/bin/env python3
"""
Example script demonstrating Table API usage.

This script shows how to interact with ServiceNow tables.
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
    """Demonstrate Table API functionality."""
    
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
        print("\n--- Service Table API Demo ---")
        
        # Note: Replace with actual sys_id from your ServiceNow instance
        sys_id = "example_catalog_item_sys_id"
        
        print(f"Search item: {sys_id}")

        result = client.get_user(sys_id)
        print(f"✓ Search successful: {result}")
        
    except Exception as e:
        print(f"Search failed: {e}")

    finally:
        client.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
