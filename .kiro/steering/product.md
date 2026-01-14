# ServiceNow MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with standardized tools for managing ServiceNow Service Requests. Built with FastMCP 2.0 and Python, this server enables natural language interactions with ServiceNow's REST API.

## Core Features

- **Service Request Management**: Create, read, update, and search Service Requests
- **Streaming HTTP Support**: Memory-efficient processing of large datasets with multiple output formats (JSON, NDJSON, CSV, TEXT)
- **Secure Authentication**: Support for basic auth and API key authentication
- **Advanced Search**: Filter requests by status, user, date range, and assignment
- **Batch Processing**: Efficient batch operations on large result sets
- **Comprehensive Error Handling**: Detailed error messages and retry logic with exponential backoff

## Target Use Cases

- AI-powered ServiceNow automation and management
- Large-scale data export and reporting from ServiceNow
- Batch processing of Service Request updates
- Integration with AI assistants for ServiceNow operations
- Memory-efficient processing of large ServiceNow datasets

## Architecture

The server follows a layered architecture with streaming support:
- **FastMCP Framework**: Handles MCP protocol communication and tool discovery
- **Decorated Tools**: Python functions that expose ServiceNow operations
- **Streaming Layer**: Memory-efficient processing for large datasets
- **ServiceNow Client**: Manages HTTP communication with ServiceNow REST API
- **Authentication Manager**: Handles credentials and authentication lifecycle
- **Configuration Manager**: Manages server configuration and environment settings