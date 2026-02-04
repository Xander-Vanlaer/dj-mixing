#!/bin/bash

# Backend Health Checker for DJ Mixing Platform
# This script verifies that the backend API is running and accessible

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default API URL
API_URL="${REACT_APP_API_URL:-http://localhost:8000}"

echo ""
echo "======================================"
echo "  Backend Health Check"
echo "======================================"
echo ""
echo -e "${BLUE}Checking backend at: ${API_URL}${NC}"
echo ""

# Function to check if backend is responding
check_backend() {
    local url=$1
    
    # Try to reach the health endpoint
    if curl -s -f "${url}/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to get health details
get_health_details() {
    local url=$1
    curl -s "${url}/health" 2>/dev/null || echo "{}"
}

# Check if backend is running
echo "1. Testing connectivity..."
if check_backend "$API_URL"; then
    echo -e "   ${GREEN}✓${NC} Backend is reachable"
    
    # Get detailed health information
    echo ""
    echo "2. Getting health status..."
    HEALTH_DATA=$(get_health_details "$API_URL")
    
    # Parse and display health information
    if command -v jq &> /dev/null; then
        # Use jq for pretty formatting if available
        echo "$HEALTH_DATA" | jq '.'
    else
        # Simple output without jq
        echo "$HEALTH_DATA"
    fi
    
    # Check API root endpoint
    echo ""
    echo "3. Testing API root endpoint..."
    if curl -s -f "${API_URL}/" > /dev/null 2>&1; then
        echo -e "   ${GREEN}✓${NC} API root is accessible"
    else
        echo -e "   ${YELLOW}⚠${NC}  API root returned an error"
    fi
    
    # Test tracks endpoint
    echo ""
    echo "4. Testing tracks endpoint..."
    if curl -s -f "${API_URL}/api/tracks/" > /dev/null 2>&1; then
        echo -e "   ${GREEN}✓${NC} Tracks API is accessible"
    else
        echo -e "   ${YELLOW}⚠${NC}  Tracks API returned an error"
    fi
    
    echo ""
    echo "======================================"
    echo -e "${GREEN}✓ Backend is healthy and running!${NC}"
    echo "======================================"
    echo ""
    echo "Available endpoints:"
    echo "  • API Root:      ${API_URL}/"
    echo "  • Health Check:  ${API_URL}/health"
    echo "  • API Docs:      ${API_URL}/docs"
    echo "  • Tracks API:    ${API_URL}/api/tracks/"
    echo ""
    exit 0
else
    echo -e "   ${RED}✗${NC} Backend is not reachable"
    echo ""
    echo "======================================"
    echo -e "${RED}Backend Connection Failed${NC}"
    echo "======================================"
    echo ""
    echo "Troubleshooting steps:"
    echo ""
    echo "1. Check if backend is running:"
    echo "   • Docker:     docker-compose ps"
    echo "   • Local dev:  ps aux | grep uvicorn"
    echo ""
    echo "2. Start the backend:"
    echo "   • Docker:     docker-compose up -d backend"
    echo "   • Local dev:  ./start-dev.sh"
    echo "   • Manual:     cd backend && uvicorn app.main:app --reload"
    echo ""
    echo "3. Verify the backend URL:"
    echo "   • Current:    ${API_URL}"
    echo "   • Expected:   http://localhost:8000 (for local/docker)"
    echo "   • Set in:     .env file (REACT_APP_API_URL)"
    echo ""
    echo "4. Check backend logs:"
    echo "   • Docker:     docker-compose logs backend"
    echo "   • Local dev:  Check terminal where uvicorn is running"
    echo ""
    echo "5. Verify network connectivity:"
    echo "   • Test:       curl ${API_URL}/health"
    echo "   • Port:       netstat -an | grep 8000"
    echo ""
    echo "6. Check firewall settings:"
    echo "   • Ensure port 8000 is not blocked"
    echo ""
    echo "For more help, see README.md (Troubleshooting section)"
    echo ""
    exit 1
fi
