#!/usr/bin/env python3
"""
Example script demonstrating Service Catalog API Search Item usage.

This script shows how to search catalog items using the ServiceNow MCP Server.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.client.servicenow_client import ServiceNowClient
from src.config.settings import load_servicenow_config


def main():
    """Demonstrate Service Catalog API search item functionality."""
    
    # Load configuration from environment
    try:
        config = load_servicenow_config()
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
        print("\n--- Service Catalog API Search Item Demo ---")
        
        params = {
            "sysparm_limit": 100,
            #"sysparm_category": "ac6eba374fb66200d16f24fe0310c7c2",
            "sysparm_text": "Gitlab*"
        }

        print(f"Searching catalog item: {params}")
        
        result = client.get_catalog_items(params=params)

        print("Catalog Items Search Result:")

        for item in result:
            print(f"- {item.get('name')} (Sys ID: {item.get('sys_id')}, Category: {item.get('category')}, Catalog: {item.get('catalog')})")
        
    except Exception as e:
        print(f"Catalog search failed: {e}")
    
    finally:
        client.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
