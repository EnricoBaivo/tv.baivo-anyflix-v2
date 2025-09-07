#!/bin/bash

# Anime Backend Service Startup Script

echo "🎌 Starting Anime Backend Service..."
echo "=================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install/sync dependencies
echo "📦 Installing dependencies..."
uv sync

# Start the service
echo "🚀 Starting FastAPI server..."
echo "API will be available at: http://localhost:8000"
echo "Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the service"
echo ""

uv run python main.py
