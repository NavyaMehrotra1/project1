#!/bin/bash

echo "🚀 Starting DealFlow Development Environment"
echo "============================================="

# Check if backend dependencies are installed
if [ ! -d "backend/venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
fi

# Start backend in background
echo "🔧 Starting FastAPI backend..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "⚛️  Starting Next.js frontend..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ DealFlow is starting up!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait $FRONTEND_PID $BACKEND_PID
