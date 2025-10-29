#!/bin/bash
# Docling OCR Installation Script for Linux/Mac

set -e

echo "========================================"
echo "Docling OCR Installation"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if Python 3.10+ is available
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    echo "Error: Python 3.10 or higher is required"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p temp models logs

# Copy environment file if not exists
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from example..."
    cp env.example .env
    echo "Please edit .env file to configure the service"
fi

# Download models
echo ""
echo "========================================"
echo "Model Download"
echo "========================================"
read -p "Do you want to download Docling models now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Downloading models..."
    python scripts/download_models.py -o ./models
else
    echo "Skipping model download. You can download later with:"
    echo "  python scripts/download_models.py"
fi

# Verify installation
echo ""
echo "========================================"
echo "Verifying Installation"
echo "========================================"
python scripts/verify_installation.py

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "To start the service:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8002"
echo ""
echo "Or use Docker:"
echo "  docker-compose up -d"
echo ""
echo "Access the web UI at: http://localhost:8002"
echo "API documentation at: http://localhost:8002/docs"
echo ""

