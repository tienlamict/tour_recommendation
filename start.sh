#!/bin/bash
# Start script for Tour Recommendation System (Linux/Mac)

echo "============================================================"
echo "Tour Recommendation System - Starting..."
echo "============================================================"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    echo ""
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate
echo ""

# Install/update dependencies
echo "Checking dependencies..."
pip install -q -r requirements.txt
echo ""

# Check Docker
echo "Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo "[WARNING] Docker is not running!"
    echo "Please start Docker and run this script again."
    echo ""
    exit 1
fi
echo "Docker is running."
echo ""

# Check if database is running
if ! docker ps | grep -q tour_db; then
    echo "Database not running. Starting..."
    cd docker
    docker-compose up -d
    cd ..
    echo "Waiting for database to initialize (20 seconds)..."
    sleep 20
    echo ""
fi

# Run the application
echo "Starting application..."
echo ""
python run.py

# Cleanup
echo ""
echo "Application closed."

