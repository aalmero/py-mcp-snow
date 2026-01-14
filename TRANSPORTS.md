# Transport Options

The ServiceNow MCP Server supports two transport modes for different use cases.

## stdio Transport (Default)

**Use Case:** Local MCP clients, IDE integrations, command-line tools

**Command:**
```bash
uv run servicenow-mcp-server
# or explicitly
uv run servicenow-mcp-server --transport stdio
```

**Characteristics:**
- Uses standard input/output for communication
- No network configuration needed
- Best for local development and testing
- Default transport mode

**Example Client Connection:**
```python
from fastmcp import Client

async with Client("servicenow-mcp-server") as client:
    await client.ping()
```

## Streamable HTTP Transport

**Use Case:** Remote access, web-based clients, production deployments

**Command:**
```bash
# Default (localhost:8000)
uv run servicenow-mcp-server --transport streamable-http

# Custom host and port
uv run servicenow-mcp-server --transport streamable-http --host 0.0.0.0 --port 8080
```

**Characteristics:**
- HTTP-based communication
- Supports remote connections
- Better for production deployments
- Endpoint: `http://{host}:{port}/mcp`

**Example Client Connection:**
```python
from fastmcp import Client

async with Client("http://127.0.0.1:8000/mcp") as client:
    await client.ping()
```

## Command-Line Options

```
--transport {stdio,streamable-http}
    Transport type (default: stdio)

--host HOST
    Host address for HTTP transport (default: 127.0.0.1)
    
--port PORT
    Port number for HTTP transport (default: 8000)
```

## Testing

### Test stdio Transport
```bash
python test_stdio.py
```

### Test Streamable HTTP Transport
```bash
# Start server
uv run servicenow-mcp-server --transport streamable-http &

# Run test
python test_streamable.py

# Stop server
pkill -f servicenow-mcp-server
```

## Choosing a Transport

| Feature | stdio | Streamable HTTP |
|---------|-------|-----------------|
| Local development | ✅ Best | ✅ Good |
| Remote access | ❌ No | ✅ Yes |
| Network config | ✅ None needed | ⚙️ Host/port required |
| Production ready | ⚠️ Limited | ✅ Yes |
| IDE integration | ✅ Excellent | ⚠️ Varies |
| Web clients | ❌ No | ✅ Yes |
