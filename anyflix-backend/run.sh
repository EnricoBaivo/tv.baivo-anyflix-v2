#!/bin/bash

# Anime Backend Service Startup Script

# Install/sync dependencies
echo "📦 Installing dependencies..."
uv sync


uv run fasatapi dev app/main.py



