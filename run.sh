#!/bin/bash

# Quick Start Script for Flight Search Agent

echo "================================"
echo "Flight Search AI Agent - Setup"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and set your GROK_API_KEY before continuing!"
    echo ""
    read -p "Press Enter after you've set your API key in .env, or Ctrl+C to exit..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Build the Docker image
echo "🔨 Building Docker image..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

echo ""
echo "🚀 Starting the agent..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Agent started successfully"
    echo ""
    echo "📊 To view logs, run: docker-compose logs -f"
    echo "🛑 To stop the agent, run: docker-compose down"
    echo ""
    echo "The agent will now run daily at the configured time (default: 09:00)"
else
    echo "❌ Failed to start the agent"
    exit 1
fi
