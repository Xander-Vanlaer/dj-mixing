#!/bin/bash

# Development Startup Script for DJ Mixing Platform
# This script starts the backend in development mode

set -e

echo "======================================"
echo "  DJ Mixing Platform - Dev Mode"
echo "======================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "   Please install Python 3.8+ from: https://www.python.org/downloads/"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} is installed"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  PostgreSQL client not found in PATH"
    echo "   You'll need PostgreSQL running (via Docker or local install)"
else
    echo -e "${GREEN}✓${NC} PostgreSQL client is installed"
fi

# Check Redis
if ! command -v redis-cli &> /dev/null; then
    echo -e "${YELLOW}⚠${NC}  Redis client not found in PATH"
    echo "   You'll need Redis running (via Docker or local install)"
else
    echo -e "${GREEN}✓${NC} Redis client is installed"
fi

echo ""
echo "======================================"
echo "Setting up environment..."
echo "======================================"
echo ""

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    
    # Generate a random secret key if on Linux/Mac
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
        else
            sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
        fi
        echo -e "${GREEN}✓${NC} Created .env file with generated secret key"
    else
        echo -e "${GREEN}✓${NC} Created .env file (please update SECRET_KEY manually)"
    fi
else
    echo -e "${GREEN}✓${NC} .env file exists"
fi

# Source the .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo ""
echo "======================================"
echo "Starting required services..."
echo "======================================"
echo ""

# Check if PostgreSQL is running
echo "Checking PostgreSQL connection..."
if pg_isready -h localhost -p 5432 &> /dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL is running"
elif docker ps | grep -q dj-mixing-db; then
    echo -e "${GREEN}✓${NC} PostgreSQL is running in Docker"
else
    echo -e "${YELLOW}⚠${NC}  PostgreSQL is not running"
    echo ""
    echo "Would you like to start PostgreSQL and Redis with Docker? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Starting database services..."
        docker-compose up -d db redis
        echo "Waiting for services to be ready..."
        sleep 5
        echo -e "${GREEN}✓${NC} Database services started"
    else
        echo -e "${YELLOW}Please start PostgreSQL manually before continuing${NC}"
        echo "You can use: docker-compose up -d db redis"
        exit 1
    fi
fi

# Check if Redis is running
echo "Checking Redis connection..."
if redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✓${NC} Redis is running"
elif docker ps | grep -q dj-mixing-redis; then
    echo -e "${GREEN}✓${NC} Redis is running in Docker"
else
    echo -e "${YELLOW}⚠${NC}  Redis is not running (optional, but recommended)"
fi

echo ""
echo "======================================"
echo "Setting up backend..."
echo "======================================"
echo ""

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Run migrations
echo "Running database migrations..."
if alembic upgrade head; then
    echo -e "${GREEN}✓${NC} Database migrations complete"
else
    echo -e "${YELLOW}⚠${NC}  Migrations failed or not configured"
fi

# Create upload directory
UPLOAD_DIR=${UPLOAD_DIR:-./uploads}
mkdir -p "$UPLOAD_DIR"
echo -e "${GREEN}✓${NC} Upload directory ready: $UPLOAD_DIR"

echo ""
echo "======================================"
echo "Starting backend server..."
echo "======================================"
echo ""

echo -e "${GREEN}Backend will start on: http://localhost:8000${NC}"
echo -e "${GREEN}API Documentation: http://localhost:8000/docs${NC}"
echo ""
echo "To start the frontend (in a separate terminal):"
echo "  cd frontend"
echo "  npm install"
echo "  npm start"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
