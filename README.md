# ServiceNow MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with standardized tools for managing ServiceNow Service Requests. Built with **FastMCP 2.0** and Python, this server enables natural language interactions with ServiceNow's REST API.

## Features

- 🔐 **Secure Authentication** - Support for basic auth and API key authentication
- 📝 **Service Request Management** - Create, read, update, and search Service Requests
- 🛒 **Service Catalog Integration** - Order catalog items using the Service Catalog API
- 🔍 **Advanced Search** - Filter requests by status, user, date range, and more
- ⚡ **FastMCP 2.0** - Simplified MCP server development with decorators
- 🛡️ **Comprehensive Error Handling** - Detailed error messages and retry logic
- ✅ **Fully Tested** - 52+ unit tests covering all core operations
- 🔄 **Automatic Retry** - Configurable retry logic for transient failures
- 📊 **Structured Logging** - Detailed logging for debugging and monitoring
- 🌐 **Multiple Transports** - Support for stdio and streamable HTTP

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- ServiceNow instance with API access
- ServiceNow credentials (username/password or API key)

**OR**

- Docker and Docker Compose (for containerized deployment)

### Docker Deployment (Recommended for Production)

1. Clone the repository:
```bash
git clone <repository-url>
cd servicenow-mcp-server
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your ServiceNow credentials
```

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

The server will be available at `http://localhost:8000/mcp`

4. View logs:
```bash
docker-compose logs -f
```

5. Stop the server:
```bash
docker-compose down
```

### Quick Setup (Recommended for Development)

For a quick automated setup, run the development setup script:

```bash
./scripts/dev-setup.sh
```

This script will:
- Install uv if not already installed
- Install all dependencies
- Create .env file from template
- Run tests to verify setup

### Manual Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd servicenow-mcp-server
```

2. Install uv (if not already installed):
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

3. Install dependencies and create virtual environment:
```bash
uv sync
```

4. Activate the virtual environment:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your ServiceNow credentials
```

## Configuration

Create a `.env` file in the project root with the following variables:

```bash
# ServiceNow Instance Configuration
SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password
# OR use API key authentication
# SERVICENOW_API_KEY=your_api_key

# Optional Configuration
SERVICENOW_TIMEOUT=30
SERVICENOW_RETRY_COUNT=3

# Server Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=10
```

### Authentication Methods

The server supports two authentication methods:

1. **Basic Authentication** (username/password):
   - Set `SERVICENOW_USERNAME` and `SERVICENOW_PASSWORD`

2. **API Key Authentication**:
   - Set `SERVICENOW_API_KEY`
   - API key takes precedence if both methods are configured

## Usage

### Running the Server

The server supports two transport modes:

#### 1. stdio Transport (Default)
For local MCP clients and IDE integrations:
```bash
uv run servicenow-mcp-server
# or explicitly
uv run servicenow-mcp-server --transport stdio
```

#### 2. Streamable HTTP Transport
For remote access and web-based clients:
```bash
uv run servicenow-mcp-server --transport streamable-http
# Custom host and port
uv run servicenow-mcp-server --transport streamable-http --host 0.0.0.0 --port 8080
```

The HTTP server will be available at `http://{host}:{port}/mcp` (default: `http://127.0.0.1:8000/mcp`)

### Command-Line Options

```bash
servicenow-mcp-server --help

Options:
  --transport {stdio,streamable-http}  Transport type (default: stdio)
  --host HOST                          Host for HTTP transport (default: 127.0.0.1)
  --port PORT                          Port for HTTP transport (default: 8000)
```

### Available Operations

The ServiceNow MCP Server provides the following operations:

#### Standard Operations

#### Create Service Request
```python
create_request({
    "short_description": "Request new laptop",
    "description": "Need a new laptop for development work",
    "requested_for": "user_sys_id",
    "priority": "2"
})
```

#### Get Service Request
```python
# By sys_id
get_request("abc123", "sys_id")

# By request number
get_request("REQ0001234", "number")
```

#### Update Service Request
```python
update_request("abc123", {
    "state": "2",
    "priority": "1",
    "work_notes": "Updated priority to high"
})
```

#### Order Catalog Item
```python
order_catalog_item("catalog_item_sys_id", {
    "quantity": "1",
    "requested_for": "user_sys_id",
    "custom_variable": "value"
})
```

#### Search Service Requests
```python
search_requests({
    "status": "1",
    "requested_for": "user_sys_id",
    "date_from": "2024-01-01",
    "limit": 50
})
```

## Why uv?

This project uses [uv](https://docs.astral.sh/uv/) as the Python package manager for several benefits:

- ⚡ **10-100x faster** than pip for dependency resolution and installation
- 🔒 **Deterministic builds** with automatic lock file generation
- 🎯 **Unified toolchain** - replaces pip, pip-tools, pipx, poetry, and more
- 🐍 **Python version management** - automatically installs and manages Python versions
- 📦 **Modern dependency groups** - cleaner separation of dev/test/prod dependencies

## Development

### Running Tests

Run all tests:
```bash
uv run pytest tests/ -v
```

Run specific test file:
```bash
uv run pytest tests/test_servicenow_client.py -v
```

Run with coverage:
```bash
uv run pytest tests/ --cov=src/servicenow_mcp --cov-report=html
```

### Code Quality

Format code with Black:
```bash
uv run black src/ tests/
```

Sort imports with isort:
```bash
uv run isort src/ tests/
```

Type checking with mypy:
```bash
uv run mypy src/
```

### Adding Dependencies

Add a new dependency:
```bash
uv add package-name
```

Add a development dependency:
```bash
uv add --group dev package-name
```

Update dependencies:
```bash
uv sync --upgrade
```

## Project Structure

```
servicenow-mcp-server/
├── src/
│   └── servicenow_mcp/
│       ├── client/           # ServiceNow HTTP client
│       │   └── servicenow_client.py
│       ├── config/           # Configuration management
│       │   └── settings.py
│       ├── tools/            # FastMCP tool definitions
│       │   └── fastmcp_tools.py
│       ├── utils/            # Utilities (logging, etc.)
│       │   └── logging.py
│       ├── exceptions.py     # Custom exceptions
│       └── server.py         # Main server entry point
├── tests/                    # Test suite
│   ├── conftest.py          # Pytest fixtures
│   ├── test_setup.py        # Setup tests
│   └── test_servicenow_client.py  # Client tests
├── scripts/                  # Development scripts
│   └── dev-setup.sh         # Automated development setup
├── .kiro/
│   └── specs/               # Feature specifications
│       └── servicenow-mcp-server/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
├── Dockerfile               # Docker container definition
├── docker-compose.yml       # Docker Compose configuration
├── pyproject.toml           # Project configuration
├── uv.lock                  # uv lock file
├── .python-version          # Python version specification
├── .env.example             # Example environment variables
└── README.md                # This file
```

## Architecture

The server follows a layered architecture:

- **FastMCP Framework**: Handles MCP protocol communication and tool discovery
- **Decorated Tools**: Python functions that expose ServiceNow operations
- **ServiceNow Client**: Manages HTTP communication with ServiceNow REST API
- **Authentication Manager**: Handles credentials and authentication lifecycle
- **Configuration Manager**: Manages server configuration and environment settings

## Error Handling

The server provides comprehensive error handling for:

- **Authentication Errors**: Invalid credentials, expired tokens
- **Connection Errors**: Network failures, timeouts, DNS issues
- **Validation Errors**: Missing required fields, invalid data types
- **API Errors**: ServiceNow-specific errors with detailed messages
- **Rate Limiting**: Automatic retry with exponential backoff

## Testing

The project includes comprehensive test coverage:

- ✅ Authentication and connection validation
- ✅ CRUD operations (Create, Read, Update, Search)
- ✅ Error handling and edge cases
- ✅ Input validation
- ✅ Configuration management

**Test Statistics:**
- 52+ unit tests
- 100% pass rate
- Covers all core ServiceNow operations

## Implementation Status

### Completed ✅
- [x] Project structure and dependencies
- [x] Configuration management
- [x] ServiceNow client with authentication
- [x] Service Request creation
- [x] Service Request retrieval
- [x] Service Request updates
- [x] Search and filtering
- [x] Comprehensive error handling
- [x] Unit tests for all operations
- [x] FastMCP tool decorators
- [x] MCP protocol integration
- [x] Multiple transport support (stdio, streamable HTTP)
- [x] Docker deployment

### In Progress 🚧
- [ ] Property-based testing

### Planned 📋
- [ ] OAuth 2.0 authentication
- [ ] Additional ServiceNow table support
- [ ] Webhook support
- [ ] Performance optimizations
- [ ] Pagination support for large result sets

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`uv run pytest tests/`)
5. Format code (`uv run black src/ tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the [design documentation](.kiro/specs/servicenow-mcp-server/design.md)
- Review the [requirements](.kiro/specs/servicenow-mcp-server/requirements.md)

## Acknowledgments

- Built with [FastMCP 2.0](https://github.com/jlowin/fastmcp) for simplified MCP server development
- Uses [uv](https://docs.astral.sh/uv/) for fast and reliable Python package management
- Uses [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- Powered by [ServiceNow REST API](https://developer.servicenow.com/dev.do)
