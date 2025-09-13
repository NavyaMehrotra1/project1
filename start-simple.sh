#!/bin/bash

echo "🚀 Starting DealFlow Simple Development Environment"
echo "================================================="

# Install minimal backend dependencies
echo "📦 Installing minimal Python dependencies..."
cd backend
pip install fastapi uvicorn python-dotenv requests
cd ..

# Install frontend dependencies (if not already installed)
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cp package-simple.json package.json
    npm install
fi

# Start backend in background
echo "🔧 Starting Simple FastAPI backend..."
cd backend
python main-simple.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting Next.js frontend..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ DealFlow Simple is running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🎯 This simplified version uses:"
echo "   - Minimal Python dependencies (no pandas, numpy, etc.)"
echo "   - Canvas-based graph instead of D3.js"
echo "   - Mock data instead of external APIs"
echo "   - No complex ML libraries"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait $FRONTEND_PID $BACKEND_PID
