#!/bin/bash
# Development setup script for ServiceNow MCP Server

set -e

echo "🚀 Setting up ServiceNow MCP Server development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed ($(uv --version))"
fi

# Sync dependencies
echo "📦 Installing dependencies..."
uv sync

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your ServiceNow credentials"
else
    echo "✅ .env file already exists"
fi

# Run tests to verify setup
echo "🧪 Running tests to verify setup..."
uv run pytest tests/ -v --tb=short

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your ServiceNow credentials"
echo "2. Run tests: uv run pytest tests/"
echo "3. Start the server: uv run servicenow-mcp-server"
echo ""
echo "For more information, see README.md"