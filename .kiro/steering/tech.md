# Technology Stack & Build System

## Core Technologies

- **Python 3.10+**: Primary language with type hints and modern features
- **FastMCP 2.0**: MCP server framework with decorator-based tool registration
- **uv**: Fast Python package manager (10-100x faster than pip)
- **Pydantic**: Data validation and settings management with type safety
- **Requests**: HTTP client library with session management and retry logic
- **python-dotenv**: Environment variable management

## Development Dependencies

- **pytest**: Testing framework with asyncio support
- **black**: Code formatting (line length: 88)
- **isort**: Import sorting with black profile
- **mypy**: Static type checking with strict configuration
- **hypothesis**: Property-based testing (planned)
- **pre-commit**: Git hooks for code quality

## Package Management with uv

This project uses [uv](https://docs.astral.sh/uv/) as the Python package manager:

```bash
# Install dependencies and create virtual environment
uv sync

# Add new dependency
uv add package-name

# Add development dependency
uv add --group dev package-name

# Update dependencies
uv sync --upgrade

# Run commands in virtual environment
uv run python -m servicenow_mcp.server
uv run pytest tests/
```

## Common Commands

### Development Setup
```bash
# Automated setup (recommended)
./scripts/dev-setup.sh

# Manual setup
uv sync
cp .env.example .env
# Edit .env with your ServiceNow credentials
```

### Running the Server
```bash
# stdio transport (default) - for local MCP clients
uv run servicenow-mcp-server

# Streamable HTTP transport - for remote access
uv run servicenow-mcp-server --transport streamable-http

# Custom host and port
uv run servicenow-mcp-server --transport streamable-http --host 0.0.0.0 --port 8080
```

### Testing
```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_servicenow_client.py -v

# Run with coverage
uv run pytest tests/ --cov=src/servicenow_mcp --cov-report=html

# Run streaming demo
uv run python examples/streaming_demo.py
```

### Code Quality
```bash
# Format code
uv run black src/ tests/

# Sort imports
uv run isort src/ tests/

# Type checking
uv run mypy src/

# Run all quality checks
uv run black src/ tests/ && uv run isort src/ tests/ && uv run mypy src/
```

## Configuration Management

- **Environment Variables**: Loaded from `.env` file using python-dotenv
- **Pydantic Models**: Type-safe configuration with validation
- **Required Variables**: `SERVICENOW_INSTANCE_URL` and authentication credentials
- **Optional Variables**: Timeouts, retry counts, logging levels

## Build Configuration

- **pyproject.toml**: Modern Python packaging with hatchling backend
- **Entry Point**: `servicenow-mcp-server` command registered in project.scripts
- **Package Structure**: Source layout with `src/servicenow_mcp/` package
- **Python Versions**: Supports 3.10, 3.11, 3.12

## Testing Strategy

- **Unit Tests**: 52+ tests covering all core operations
- **Fixtures**: Centralized test configuration in `conftest.py`
- **Mocking**: HTTP responses and ServiceNow API interactions
- **Coverage**: Focus on ServiceNow client, streaming, and error handling
- **Property-based Testing**: Planned with hypothesis for robust validation