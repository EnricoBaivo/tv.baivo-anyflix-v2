#!/bin/bash

# Start all anyflix services
# This script starts the backend, proxy, and frontend in separate terminals/processes

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting Anyflix Services..."
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if services are already running
if check_port 8000; then
    echo "⚠️  Backend already running on port 8000"
fi

if check_port 8081; then
    echo "⚠️  Proxy already running on port 8081"
fi

if check_port 8080; then
    echo "⚠️  Frontend already running on port 8080"
fi

echo ""
echo "Starting services..."
echo ""

# Start backend
echo "1️⃣  Starting Backend (port 8000)..."
cd "$SCRIPT_DIR/anyflix-backend"
if [ -f "run.sh" ]; then
    ./run.sh > ../logs/backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   Backend started (PID: $BACKEND_PID)"
else
    echo "   ⚠️  Backend run script not found, skipping..."
fi

# Start proxy
echo "2️⃣  Starting Proxy Service (port 8081)..."
cd "$SCRIPT_DIR/anyflix-proxy"
if command -v go &> /dev/null; then
    go run main.go > ../logs/proxy.log 2>&1 &
    PROXY_PID=$!
    echo "   Proxy started (PID: $PROXY_PID)"
else
    echo "   ⚠️  Go not installed, skipping proxy service..."
fi

# Start frontend
echo "3️⃣  Starting Frontend (port 8080)..."
cd "$SCRIPT_DIR/anyflix-player"
if [ -d "node_modules" ]; then
    npm run dev > ../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "   Frontend started (PID: $FRONTEND_PID)"
else
    echo "   ⚠️  node_modules not found. Run 'npm install' first."
fi

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Service URLs:"
echo "   Backend:  http://localhost:8000"
echo "   Proxy:    http://localhost:8081"
echo "   Frontend: http://localhost:8080"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f $SCRIPT_DIR/logs/backend.log"
echo "   Proxy:    tail -f $SCRIPT_DIR/logs/proxy.log"
echo "   Frontend: tail -f $SCRIPT_DIR/logs/frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   pkill -f 'uvicorn|go run|vite'"
echo ""

# Save PIDs for cleanup
mkdir -p "$SCRIPT_DIR/logs"
echo "$BACKEND_PID" > "$SCRIPT_DIR/logs/backend.pid"
echo "$PROXY_PID" > "$SCRIPT_DIR/logs/proxy.pid"
echo "$FRONTEND_PID" > "$SCRIPT_DIR/logs/frontend.pid"

# Wait a bit to let services start
sleep 3

# Health checks
echo "🏥 Health Checks:"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is healthy"
else
    echo "   ❌ Backend is not responding"
fi

if curl -s http://localhost:8081/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Proxy is healthy"
else
    echo "   ❌ Proxy is not responding"
fi

if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "   ✅ Frontend is responding"
else
    echo "   ⏳ Frontend is starting... (may take a moment)"
fi

echo ""
echo "Press Ctrl+C to see logs in real-time, or use the tail commands above"
echo ""

# Follow logs
tail -f "$SCRIPT_DIR/logs/proxy.log" "$SCRIPT_DIR/logs/backend.log" "$SCRIPT_DIR/logs/frontend.log" 2>/dev/null

