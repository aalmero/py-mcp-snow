> is the streaming operations used in the mcp framework?

> Let me check how the streaming operations are integrated with the MCP 
framework.
Reading file: /Users/aalmero/source/mcp-projects/py-mcp-snow/src/servicenow_mcp/tools/fastmcp_tools.py, all lines (using tool: read)
 ✓ Successfully read 16200 bytes from /Users/aalmero/source/mcp-projects/py-mcp-snow/src/servicenow_mcp/tools/fastmcp_tools.py
 - Completed in 0.0s

Reading file: /Users/aalmero/source/mcp-projects/py-mcp-snow/src/servicenow_mcp/streaming/mcp_streaming.py, all lines (using tool: read)
 ✓ Successfully read 18484 bytes from /Users/aalmero/source/mcp-projects/py-mcp-snow/src/servicenow_mcp/streaming/mcp_streaming.py
 - Completed in 0.0s

> Now I can see the issue. The streaming operations are defined as MCP tools but 
they return metadata dictionaries instead of actual streaming data. The MCP 
protocol doesn't natively support streaming responses - it's a request/response 
protocol. The streaming functionality exists but isn't properly integrated with 
MCP.

Let me check if there's actual streaming happening:
Searching for: search_requests_stream|get_all_requests_stream (*.py) (using tool: grep)
 ✓ Successfully found 13 matches in 3 files under current directory
 - Completed in 0.49s

> The streaming methods exist in the ServiceNow client, but the MCP tools are not
actually streaming the data. They're just returning metadata about what would be
streamed. This is because:

1. MCP protocol limitation: MCP is a request/response protocol - tools return a 
single response, not a stream
2. The streaming tools return metadata only: They don't actually stream data 
through the MCP protocol
3. HTTP streaming exists separately: The HTTP streaming functionality is there 
but disconnected from MCP tools

Summary:

❌ No, the streaming operations are NOT actually used in the MCP framework. 

The code has:
- ✅ HTTP streaming infrastructure (http_streaming.py)
- ✅ Streaming methods in ServiceNow client (search_requests_stream, etc.)
- ✅ MCP tools that reference streaming (stream_search_service_requests, etc.)
- ❌ But the MCP tools only return metadata, not actual streams

The streaming functionality is built but not integrated with MCP. The MCP tools 
would need to either:
1. Return the full dataset (defeating the purpose of streaming)
2. Use a different mechanism like SSE or WebSockets (not standard MCP)
3. Return pagination tokens for chunked retrieval (more MCP-appropriate)

Would you like me to either:
1. Remove the non-functional streaming MCP tools?
2. Convert them to pagination-based tools that work with MCP?
3. Document this limitation clearly?
 ▸ Credits: 0.78 • Time: 28s
