# Project Structure & Organization

## Directory Layout

```
servicenow-mcp-server/
├── src/servicenow_mcp/          # Main package (source layout)
│   ├── __init__.py
│   ├── server.py                # Main server entry point with FastMCP integration
│   ├── exceptions.py            # Custom exception classes
│   ├── auth/                    # Authentication modules (future)
│   ├── client/                  # ServiceNow HTTP client
│   │   └── servicenow_client.py # Core ServiceNow REST API client
│   ├── config/                  # Configuration management
│   │   └── settings.py          # Pydantic models for settings
│   ├── models/                  # Data models (future expansion)
│   ├── streaming/               # Streaming HTTP support
│   │   ├── http_streaming.py    # HTTP streaming utilities
│   │   └── mcp_streaming.py     # MCP streaming tools
│   ├── tools/                   # FastMCP tool definitions
│   │   └── fastmcp_tools.py     # Decorated MCP tools
│   └── utils/                   # Utility modules
│       └── logging.py           # Logging configuration
├── tests/                       # Test suite
│   ├── conftest.py             # Pytest fixtures and configuration
│   ├── test_setup.py           # Setup and configuration tests
│   ├── test_servicenow_client.py # ServiceNow client tests
│   ├── test_fastmcp_tools.py   # FastMCP tools tests
│   └── test_streaming.py       # Streaming functionality tests
├── examples/                    # Example scripts and demos
│   ├── streaming_demo.py       # Streaming capabilities demonstration
│   ├── mcp_streaming_server.py # MCP streaming server example
│   └── test_streaming_client.py # Streaming client test
├── scripts/                     # Development and deployment scripts
│   └── dev-setup.sh            # Automated development setup
├── .kiro/                      # Kiro IDE configuration
│   └── specs/                  # Feature specifications
│       └── servicenow-mcp-server/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
├── main.py                     # Alternative entry point
├── pyproject.toml              # Project configuration and dependencies
├── uv.lock                     # uv lock file for reproducible builds
├── .python-version             # Python version specification
├── .env.example                # Environment variables template
└── README.md                   # Project documentation
```

## Module Organization Patterns

### Core Architecture Layers

1. **Server Layer** (`server.py`): FastMCP integration and server lifecycle
2. **Tools Layer** (`tools/`): MCP tool definitions with decorators
3. **Client Layer** (`client/`): ServiceNow REST API communication
4. **Streaming Layer** (`streaming/`): Memory-efficient data processing
5. **Configuration Layer** (`config/`): Settings and environment management
6. **Utilities Layer** (`utils/`): Shared utilities and logging

### Import Conventions

- **Relative imports** within the package: `from ..client import ServiceNowClient`
- **Absolute imports** for external dependencies: `from fastmcp import FastMCP`
- **Type imports** separated: `from typing import Dict, Any, Optional`
- **Exception imports** grouped: `from ..exceptions import ValidationError, ServiceNowAPIError`

### File Naming Conventions

- **Snake case** for all Python files: `servicenow_client.py`
- **Package names** match directory names: `servicenow_mcp`
- **Test files** prefixed with `test_`: `test_servicenow_client.py`
- **Configuration files** use standard names: `pyproject.toml`, `.env`

## Code Organization Patterns

### Class Structure
- **Client classes**: Handle external API communication with retry logic
- **Configuration classes**: Pydantic models with validation
- **Exception classes**: Custom exceptions with error codes and context
- **Tool functions**: FastMCP decorated functions with type hints

### Error Handling Strategy
- **Custom exceptions** in `exceptions.py` with inheritance hierarchy
- **Error formatting** utilities for consistent MCP responses
- **Retry logic** in HTTP client with exponential backoff
- **Validation errors** with field-specific context

### Testing Organization
- **Unit tests** for each module in corresponding `test_*.py` files
- **Integration tests** for end-to-end workflows
- **Fixtures** in `conftest.py` for shared test data and mocks
- **Test data** embedded in test files or fixtures

## Configuration Management

### Environment Variables
- **Required**: `SERVICENOW_INSTANCE_URL`, authentication credentials
- **Optional**: Timeouts, retry counts, logging levels
- **Validation**: Pydantic models with field validators
- **Loading**: python-dotenv with `.env` file support

### Settings Hierarchy
1. **Environment variables** (highest priority)
2. **`.env` file** values
3. **Default values** in Pydantic models

## Entry Points and Execution

### Primary Entry Points
- **Command line**: `uv run servicenow-mcp-server` (registered in pyproject.toml)
- **Module execution**: `uv run python -m servicenow_mcp.server`
- **Direct execution**: `uv run python main.py`

### Server Initialization Flow
1. Load configuration from environment
2. Initialize ServiceNow client with authentication
3. Initialize streaming tools
4. Register FastMCP tools with decorators
5. Start FastMCP server with async event loop

## Development Workflow

### Adding New Features
1. **Create module** in appropriate package directory
2. **Add tests** in corresponding test file
3. **Update imports** in `__init__.py` files if needed
4. **Register tools** in `fastmcp_tools.py` if MCP-exposed
5. **Update documentation** in README.md

### Code Quality Standards
- **Type hints** required for all function signatures
- **Docstrings** for all public functions and classes
- **Error handling** with specific exception types
- **Logging** at appropriate levels with structured messages