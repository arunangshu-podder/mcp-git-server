#!/bin/bash
# Quick start script for MCP Git Server
# Runs the Flask HTTP server for local git operations

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}MCP Git Server - Quick Start${NC}\n"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 not found. Please install Python 3.${NC}"
    exit 1
fi

# If a project virtualenv exists, activate it so installs run inside it
if [ -f ".venv/bin/activate" ]; then
    echo -e "${BLUE}Activating virtualenv .venv...${NC}"
    # shellcheck source=/dev/null
    source .venv/bin/activate
fi

# Check if Flask is installed; install into venv if present, otherwise instruct user
if ! python3 -c "import flask" 2>/dev/null; then
    if [ -n "${VIRTUAL_ENV}" ] || [ -f ".venv/bin/activate" ]; then
        echo -e "${YELLOW}Flask not installed in the active environment. Installing dependencies into virtualenv...${NC}"
        python3 -m pip install --upgrade pip
        python3 -m pip install -r requirements.txt
    else
        echo -e "${YELLOW}Flask not installed and no virtualenv detected.${NC}"
        echo -e "Please create and activate a virtual environment, then run this script again:\n"
        echo -e "  python3 -m venv .venv"
        echo -e "  source .venv/bin/activate"
        echo -e "  python3 -m pip install -r requirements.txt\n"
        echo -e "Alternatively, install Flask system-wide or use pipx. Exiting.${NC}"
        exit 1
    fi
fi

# Get command line arguments
HOST="${1:-127.0.0.1}"
PORT="${2:-5000}"
DEBUG="${3:-}"

# Export environment variables if .env exists
if [ -f ".env" ]; then
    echo -e "${BLUE}Loading .env file...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

echo -e "${GREEN}Starting Flask HTTP Server...${NC}"
echo -e "Host: ${HOST}"
echo -e "Port: ${PORT}"
echo -e "Debug: ${DEBUG:-disabled}\n"

echo -e "${BLUE}Server will be available at: http://${HOST}:${PORT}${NC}"
echo -e "${BLUE}Health check endpoint: http://${HOST}:${PORT}/api/health${NC}\n"

echo -e "${YELLOW}To use with Copilot in VS Code:${NC}"
echo -e "1. Configure MCP settings in VS Code"
echo -e "2. The Flask server must keep running"
echo -e "3. MCP requests will be forwarded to this server\n"

echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}\n"

# Start the server
if [ -n "$DEBUG" ]; then
    python3 run_server.py --host "$HOST" --port "$PORT" --debug
else
    python3 run_server.py --host "$HOST" --port "$PORT"
fi
