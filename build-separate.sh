#!/bin/bash

# Script for building binaries using Docker (separate build)
# YT Sprint Tool - YouTrack Sprint automation utilities
# Author: Sergei Sveshnikov (svesh87@gmail.com)
# Repository: https://github.com/svesh/yt-sprint-tool/

echo "🔨 Starting binary build using Docker (separately)..."

# Create folder for artifacts
mkdir -p dist

# Build Linux binaries
echo "🐧 Building Linux binaries..."
docker build -f Dockerfile.debian -t yt-sprint-tool:linux .

echo "🔍 Extracting Linux binaries..."
LINUX_CONTAINER_ID=$(docker create yt-sprint-tool:linux)
docker cp $LINUX_CONTAINER_ID:/usr/local/bin/make-sprint ./dist/make-sprint-linux || echo "⚠️  Linux make-sprint not found"
docker cp $LINUX_CONTAINER_ID:/usr/local/bin/default-sprint ./dist/default-sprint-linux || echo "⚠️  Linux default-sprint not found"
docker rm $LINUX_CONTAINER_ID

# Build Windows binaries
echo "🪟 Building Windows binaries..."
if docker build -f Dockerfile.windows -t yt-sprint-tool:windows .; then
    echo "🔍 Extracting Windows binaries..."
    # Use docker build with --output to extract from scratch image
    docker build -f Dockerfile.windows --target export-stage --output ./dist .
else
    echo "⚠️  Windows build failed, but Linux binaries are ready"
fi

echo "✅ Build completed! Binaries are in ./dist/ folder"
echo "📋 Contents of dist folder:"
ls -la ./dist/

echo "🧪 Testing Linux binaries..."
if [ -f "./dist/make-sprint-linux" ]; then
    chmod +x ./dist/make-sprint-linux
    echo "🔍 Version make-sprint-linux:"
    ./dist/make-sprint-linux --help | head -5 || echo "⚠️  Error running make-sprint-linux"
fi

if [ -f "./dist/default-sprint-linux" ]; then
    chmod +x ./dist/default-sprint-linux
    echo "🔍 Version default-sprint-linux:"
    ./dist/default-sprint-linux --help | head -5 || echo "⚠️  Error running default-sprint-linux"
fi

echo "🧪 Checking Windows binaries..."
if [ -f "./dist/make-sprint.exe" ]; then
    echo "✅ Windows make-sprint.exe found ($(du -h ./dist/make-sprint.exe | cut -f1))"
fi

if [ -f "./dist/default-sprint.exe" ]; then
    echo "✅ Windows default-sprint.exe found ($(du -h ./dist/default-sprint.exe | cut -f1))"
fi

echo ""
echo "🎯 Build result:"
echo "Linux binaries: $(ls ./dist/*-linux 2>/dev/null | wc -l) files"
echo "Windows binaries: $(ls ./dist/*.exe 2>/dev/null | wc -l) files"
