#!/bin/bash

echo "🚀 Starting M&A Intelligence System"
echo "=================================="

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env and add your EXA_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Check if EXA_API_KEY is set
if ! grep -q "EXA_API_KEY=.*[^=]" backend/.env; then
    echo "❌ EXA_API_KEY not set in backend/.env"
    echo "📝 Please add your Exa API key to backend/.env"
    exit 1
fi

echo "✅ Environment configured"

# Start backend server
echo "🔧 Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend server running on http://localhost:8000"
else
    echo "❌ Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start the M&A agent
echo "🤖 Starting M&A monitoring agent..."
curl -s -X POST http://localhost:8000/ma-agent/start > /dev/null

if [ $? -eq 0 ]; then
    echo "✅ M&A agent started successfully"
else
    echo "⚠️  Could not start M&A agent via API"
fi

echo ""
echo "🎉 System is running!"
echo "📊 Dashboard: http://localhost:3000/ma-agent"
echo "🔗 API: http://localhost:8000/ma-agent/dashboard"
echo "📋 Status: http://localhost:8000/ma-agent/status"
echo ""
echo "Press Ctrl+C to stop all services"

# Keep script running and handle shutdown
trap 'echo ""; echo "🛑 Shutting down..."; curl -s -X POST http://localhost:8000/ma-agent/stop > /dev/null; kill $BACKEND_PID 2>/dev/null; exit 0' INT

# Wait for user interrupt
while true; do
    sleep 1
done
