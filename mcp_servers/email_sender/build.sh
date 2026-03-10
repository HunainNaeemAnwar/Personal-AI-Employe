#!/bin/bash
# Build script for Email Sender MCP Server

set -e  # Exit on error

echo "Building Email Sender MCP Server..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js v24+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 24 ]; then
    echo "Error: Node.js v24+ is required. Current version: $(node -v)"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Clean previous build
echo "Cleaning previous build..."
npm run clean 2>/dev/null || true

# Compile TypeScript
echo "Compiling TypeScript..."
npm run build

echo "Build complete! Output in dist/"
echo ""
echo "To run the server:"
echo "  npm start"
echo ""
echo "Or directly:"
echo "  node dist/index.js"
