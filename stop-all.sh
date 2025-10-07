#!/bin/bash

# Stop all anyflix services

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Stopping Anyflix Services..."
echo ""

# Kill by PID files if they exist
if [ -f "$SCRIPT_DIR/logs/backend.pid" ]; then
    BACKEND_PID=$(cat "$SCRIPT_DIR/logs/backend.pid")
    if kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null && echo "✅ Stopped Backend (PID: $BACKEND_PID)"
    fi
    rm "$SCRIPT_DIR/logs/backend.pid"
fi

if [ -f "$SCRIPT_DIR/logs/proxy.pid" ]; then
    PROXY_PID=$(cat "$SCRIPT_DIR/logs/proxy.pid")
    if kill -0 "$PROXY_PID" 2>/dev/null; then
        kill "$PROXY_PID" 2>/dev/null && echo "✅ Stopped Proxy (PID: $PROXY_PID)"
    fi
    rm "$SCRIPT_DIR/logs/proxy.pid"
fi

if [ -f "$SCRIPT_DIR/logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$SCRIPT_DIR/logs/frontend.pid")
    if kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null && echo "✅ Stopped Frontend (PID: $FRONTEND_PID)"
    fi
    rm "$SCRIPT_DIR/logs/frontend.pid"
fi

# Fallback: kill by process name
echo ""
echo "Cleaning up any remaining processes..."

pkill -f "uvicorn.*anyflix" && echo "✅ Killed uvicorn processes"
pkill -f "anyflix-proxy/main.go" && echo "✅ Killed proxy processes"
pkill -f "vite.*anyflix-player" && echo "✅ Killed vite processes"

echo ""
echo "✅ All services stopped!"

