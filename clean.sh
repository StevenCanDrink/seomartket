#!/bin/bash
echo "Cleaning FastAPI cache..."
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} +
rm -rf ./tmp/*.* 2>/dev/null || true  
rm -rf project_zip.zip 2>/dev/null