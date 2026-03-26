#!/bin/bash

# Gemini Voice Agent Startup Script

echo "🚀 Starting Gemini Voice Agent..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your GOOGLE_API_KEY"
    echo "Exiting..."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Check if GOOGLE_API_KEY is set
if ! grep -q "GOOGLE_API_KEY=your_google_api_key_here" .env && grep -q "GOOGLE_API_KEY=" .env; then
    echo "✅ Environment configured"
else
    echo "⚠️  Please set your GOOGLE_API_KEY in the .env file"
    exit 1
fi

# Start the server
echo "🎤 Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python main.py
