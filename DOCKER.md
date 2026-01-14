# Docker Deployment Guide

This guide covers deploying the ServiceNow MCP Server using Docker and Docker Compose.

## Quick Start

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your ServiceNow credentials

# 2. Start the server
docker-compose up -d

# 3. Check logs
docker-compose logs -f

# 4. Test the server
curl http://localhost:8000/mcp
```

## Docker Compose Configuration

The `docker-compose.yml` file includes:

- **Port Mapping**: Exposes port 8000 for HTTP access
- **Environment Variables**: Loads from `.env` file
- **Health Check**: Monitors server availability
- **Auto Restart**: Restarts on failure

### Environment Variables

Required:
```bash
SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com
SERVICENOW_USERNAME=your_username
SERVICENOW_PASSWORD=your_password
# OR
SERVICENOW_API_KEY=your_api_key
```

Optional:
```bash
SERVICENOW_TIMEOUT=30
SERVICENOW_RETRY_COUNT=3
LOG_LEVEL=INFO
MAX_CONCURRENT_REQUESTS=10
```

## Docker Commands

### Build and Start
```bash
# Build and start in detached mode
docker-compose up -d

# Build with no cache
docker-compose build --no-cache

# Start with specific service
docker-compose up servicenow-mcp
```

### Manage Container
```bash
# View logs
docker-compose logs -f

# View logs (last 100 lines)
docker-compose logs --tail=100

# Stop the server
docker-compose stop

# Stop and remove containers
docker-compose down

# Restart the server
docker-compose restart
```

### Inspect Container
```bash
# Check container status
docker-compose ps

# Execute command in container
docker-compose exec servicenow-mcp sh

# View container resource usage
docker stats servicenow-mcp-server
```

## Dockerfile Details

The Dockerfile:
- Uses Python 3.12 slim base image
- Installs `uv` for fast dependency management
- Copies only necessary files (see `.dockerignore`)
- Runs with streamable-http transport on 0.0.0.0:8000
- Sets `PYTHONUNBUFFERED=1` for real-time logs

## Custom Configuration

### Change Port
Edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8000"  # Host:Container
```

### Use stdio Transport
Override the command in `docker-compose.yml`:
```yaml
command: ["--transport", "stdio"]
```

### Custom Host/Port
```yaml
command: ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8080"]
ports:
  - "8080:8080"
```

## Production Deployment

### Security Considerations

1. **Use secrets management** instead of `.env` file:
```yaml
secrets:
  servicenow_password:
    external: true
```

2. **Run as non-root user** (add to Dockerfile):
```dockerfile
RUN useradd -m -u 1000 mcpuser
USER mcpuser
```

3. **Use specific image tags** instead of `latest`

4. **Enable TLS/SSL** with reverse proxy (nginx, traefik)

### Resource Limits

Add to `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 512M
    reservations:
      cpus: '0.5'
      memory: 256M
```

### Health Check

The default health check:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/mcp"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 10s
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs servicenow-mcp

# Check if port is already in use
lsof -i :8000

# Rebuild without cache
docker-compose build --no-cache
docker-compose up -d
```

### Connection refused
```bash
# Verify container is running
docker-compose ps

# Check health status
docker inspect servicenow-mcp-server | grep -A 10 Health

# Test from inside container
docker-compose exec servicenow-mcp curl http://localhost:8000/mcp
```

### Environment variables not loading
```bash
# Verify .env file exists
ls -la .env

# Check loaded environment
docker-compose config

# Restart with fresh environment
docker-compose down
docker-compose up -d
```

## Multi-Stage Build (Advanced)

For smaller images, use multi-stage build:

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
ENV PATH="/app/.venv/bin:$PATH"
CMD ["servicenow-mcp-server", "--transport", "streamable-http", "--host", "0.0.0.0"]
```

## Docker Hub / Registry

### Build and Push
```bash
# Build with tag
docker build -t your-registry/servicenow-mcp:latest .

# Push to registry
docker push your-registry/servicenow-mcp:latest

# Use in docker-compose.yml
services:
  servicenow-mcp:
    image: your-registry/servicenow-mcp:latest
```
