#!/bin/bash

# Quick Setup Script for DJ Mixing Platform

set -e

echo "======================================"
echo "  DJ Mixing Platform - Quick Setup"
echo "======================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "   Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker is installed"

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    echo "   Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✓ Docker Compose is installed"

echo ""
echo "======================================"
echo "Setting up environment..."
echo "======================================"

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Update .env with generated secret
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-change-in-production/$SECRET_KEY/" .env
    fi
    
    echo "✓ Created .env file with generated secret key"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "======================================"
echo "Building Docker images..."
echo "======================================"

docker-compose build

echo ""
echo "======================================"
echo "Starting services..."
echo "======================================"

docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 15

echo ""
echo "======================================"
echo "Checking service health..."
echo "======================================"

# Check backend health
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is healthy"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠ Backend health check failed, but continuing..."
    fi
    sleep 2
done

# Check frontend
for i in {1..10}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✓ Frontend is accessible"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "⚠ Frontend not accessible yet, but continuing..."
    fi
    sleep 2
done

echo ""
echo "======================================"
echo "  Setup Complete! 🎉"
echo "======================================"
echo ""
echo "Access your DJ Mixing Platform:"
echo ""
echo "  🎵 Frontend:        http://localhost:3000"
echo "  🔧 Backend API:     http://localhost:8000"
echo "  📚 API Docs:        http://localhost:8000/docs"
echo ""
echo "Quick tips:"
echo "  • Navigate to the Library tab to upload your first track"
echo "  • Supported formats: MP3, WAV, FLAC, AAC, M4A"
echo "  • Tracks are automatically analyzed (BPM, key, waveform)"
echo "  • Switch to Mixer tab to start DJing!"
echo ""
echo "Management commands:"
echo "  • View logs:        docker-compose logs -f"
echo "  • Stop platform:    docker-compose down"
echo "  • Restart:          docker-compose restart"
echo "  • View status:      docker-compose ps"
echo ""
echo "For help and documentation:"
echo "  • README.md         - Quick start guide"
echo "  • DEPLOYMENT.md     - Deployment guide"
echo "  • API.md            - API reference"
echo "  • CONTRIBUTING.md   - Contribution guidelines"
echo ""
echo "Happy mixing! 🎧"
