FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock README.md main.py ./
COPY src/ ./src/

# Install dependencies and project (production only)
RUN uv sync --frozen --no-dev

# Expose port for HTTP transport
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Default to streamable-http transport for container deployments
ENTRYPOINT ["servicenow-mcp-server"]
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
