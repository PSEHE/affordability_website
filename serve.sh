#!/bin/bash
# Simple local development server for the affordability website
# Usage: ./serve.sh [port]
# Default port: 8000

PORT=${1:-8000}
echo "Starting local server at http://localhost:$PORT"
echo "Open http://localhost:$PORT/pages/overview.html to view the site"
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
python3 -m http.server $PORT
