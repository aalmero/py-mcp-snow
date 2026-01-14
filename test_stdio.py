#!/usr/bin/env python3
"""Test stdio transport."""

import subprocess
import json
import sys

def test_stdio():
    """Test stdio transport with MCP protocol."""
    print("Testing stdio transport...")
    
    # Start server with stdio transport
    proc = subprocess.Popen(
        ["uv", "run", "servicenow-mcp-server", "--transport", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test", "version": "1.0"}
        }
    }
    
    try:
        proc.stdin.write(json.dumps(init_request) + "\n")
        proc.stdin.flush()
        
        # Read response (with timeout)
        import select
        if select.select([proc.stdout], [], [], 5)[0]:
            response = proc.stdout.readline()
            if response:
                print(f"✅ Received response: {response[:200]}...")
                return True
        else:
            print("❌ Timeout waiting for response")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        proc.terminate()
        proc.wait(timeout=2)

if __name__ == "__main__":
    success = test_stdio()
    sys.exit(0 if success else 1)
