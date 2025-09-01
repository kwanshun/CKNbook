#!/bin/bash

# Production Deployment Script for Tone-Toner

echo "🚀 Starting production deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found! Please create one with your production settings."
    echo "   Copy .env.production as template and fill in your values."
    exit 1
fi

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements_production.txt

# Run basic tests
echo "🧪 Running basic tests..."
python -c "
import google.generativeai as genai
import flask
print('✅ All dependencies imported successfully')
"

# Start with Gunicorn
echo "🌟 Starting production server with Gunicorn..."
echo "   Server will be available at: http://localhost:5001"
echo "   Press Ctrl+C to stop"

gunicorn --config gunicorn.conf.py main_production:app

