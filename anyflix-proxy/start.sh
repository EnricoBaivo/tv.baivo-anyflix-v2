#!/bin/bash

# Start script for anyflix-proxy

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "Error: Go is not installed. Please install Go 1.21 or higher."
    echo "Visit: https://golang.org/dl/"
    exit 1
fi

# Check Go version
GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
REQUIRED_VERSION="1.21"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$GO_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "Error: Go version $REQUIRED_VERSION or higher is required. Current version: $GO_VERSION"
    exit 1
fi

echo "Starting anyflix-proxy..."

# Download dependencies if not already present
if [ ! -d "vendor" ]; then
    echo "Downloading dependencies..."
    go mod download
fi

# Set default port if not set
export PORT=${PORT:-8081}

echo "Server will start on port $PORT"
echo "Press Ctrl+C to stop"

# Run the server
go run main.go

