#!/bin/bash

# QuizMaster Pro - Complete Launcher
echo "🎯 Starting QuizMaster Pro..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python3 init_app.py

# Check if Redis is running, start if not
if ! pgrep -x "redis-server" > /dev/null; then
    echo "🔄 Starting Redis server..."
    redis-server --daemonize yes
    sleep 2
fi

# Start Celery services in background
echo "🔄 Starting Celery worker..."
celery -A celery_worker.celery worker --loglevel=info --detach

echo "⏰ Starting Celery beat scheduler..."  
celery -A celery_worker.celery beat --loglevel=info --detach

# Build frontend for production
echo "📦 Building Vue.js frontend..."
cd frontend

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed! Please install Node.js first."
    exit 1
fi

# Install dependencies and build
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

# Build the frontend
npm run build

if [ $? -eq 0 ]; then
    echo "✅ Frontend build completed successfully!"
else
    echo "❌ Frontend build failed!"
    exit 1
fi

cd ..

# Check if build was successful
if [ ! -f "static/dist/index.html" ]; then
    echo "❌ Frontend build failed - index.html not found!"
    exit 1
fi

echo ""
echo "✅ QuizMaster Pro is ready!"
echo "🌐 Open your browser to: http://localhost:5000"  
echo "👑 Admin login: admin@quizmaster.com / admin123"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    pkill -f "celery.*worker" 2>/dev/null || true
    pkill -f "celery.*beat" 2>/dev/null || true
    echo "✅ All services stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Flask application  
python3 app.py
