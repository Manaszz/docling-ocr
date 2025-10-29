#!/bin/bash
# Prepare offline deployment package for Docling OCR

set -e

echo "========================================"
echo "Docling OCR Offline Package Preparation"
echo "========================================"
echo ""

# Configuration
OFFLINE_DIR="offline-deploy"
WHEELS_DIR="$OFFLINE_DIR/wheels"
MODELS_DIR="$OFFLINE_DIR/models"

# Create directories
echo "Creating directory structure..."
mkdir -p "$OFFLINE_DIR"
mkdir -p "$WHEELS_DIR"
mkdir -p "$MODELS_DIR"
mkdir -p "$OFFLINE_DIR/app"

# Download Python packages
echo ""
echo "========================================"
echo "Downloading Python packages..."
echo "========================================"
pip download -r requirements.txt -d "$WHEELS_DIR"

# Copy application code
echo ""
echo "Copying application code..."
cp -r app/* "$OFFLINE_DIR/app/"
cp requirements.txt "$OFFLINE_DIR/"
cp env.example "$OFFLINE_DIR/"

# Download models
echo ""
echo "========================================"
echo "Downloading Docling models..."
echo "========================================"
python scripts/download_models.py -o "$MODELS_DIR"

# Create installation scripts
echo ""
echo "Creating installation scripts..."

# Linux installation script
cat > "$OFFLINE_DIR/install_offline.sh" << 'EOF'
#!/bin/bash
# Offline installation script for Docling OCR

set -e

echo "========================================"
echo "Docling OCR Offline Installation"
echo "========================================"
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found"
    exit 1
fi

python3 --version

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --no-index --find-links=wheels/

# Install dependencies from wheels
echo "Installing dependencies..."
pip install --no-index --find-links=wheels/ -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p temp logs

# Copy environment file
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "Created .env file - please configure"
fi

echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Configure .env file and then start with:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8002"
EOF

chmod +x "$OFFLINE_DIR/install_offline.sh"

# Windows installation script
cat > "$OFFLINE_DIR/install_offline.bat" << 'EOF'
@echo off
REM Offline installation script for Docling OCR (Windows)

echo ========================================
echo Docling OCR Offline Installation
echo ========================================
echo.

REM Check Python
echo Checking Python...
python --version 2>nul
if errorlevel 1 (
    echo Error: Python not found
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --no-index --find-links=wheels\

REM Install dependencies
echo Installing dependencies...
pip install --no-index --find-links=wheels\ -r requirements.txt

REM Create directories
echo Creating directories...
if not exist "temp" mkdir temp
if not exist "logs" mkdir logs

REM Copy environment file
if not exist ".env" (
    copy env.example .env
    echo Created .env file - please configure
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Configure .env file and then start with:
echo   venv\Scripts\activate
echo   uvicorn app.main:app --host 0.0.0.0 --port 8002
pause
EOF

# Create README for offline package
cat > "$OFFLINE_DIR/README.md" << 'EOF'
# Docling OCR - Offline Installation Package

This package contains everything needed to install Docling OCR in an air-gapped/offline environment.

## Contents

- `wheels/` - All Python dependencies
- `models/` - Docling AI models
- `app/` - Application code
- `requirements.txt` - Dependencies list
- `env.example` - Configuration template
- `install_offline.sh` - Linux/Mac installation script
- `install_offline.bat` - Windows installation script

## Requirements

- Python 3.10 or higher (must be pre-installed)
- 5GB+ disk space

## Installation

### Linux/Mac

```bash
chmod +x install_offline.sh
./install_offline.sh
```

### Windows

```cmd
install_offline.bat
```

## Configuration

Edit `.env` file:

```bash
# Important: Set models path
DOCLING_ARTIFACTS_PATH=./models

# Configure OCR
DOCLING_OCR_ENABLED=true
DOCLING_OCR_LANGUAGES=en,ru
```

## Start Service

```bash
# Linux/Mac
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002

# Windows
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## Access

- Web UI: http://localhost:8002
- API Docs: http://localhost:8002/docs
- Health Check: http://localhost:8002/ocr/docling/health

## Support

See main documentation in parent repository.
EOF

# Create package info
echo ""
echo "Creating package information..."
cat > "$OFFLINE_DIR/PACKAGE_INFO.txt" << EOF
Docling OCR Offline Package
Generated: $(date)
Platform: $(uname -s) $(uname -m)
Python: $(python3 --version)

Package Contents:
- Python wheels: $(ls -1 "$WHEELS_DIR" | wc -l) files
- Models: $(du -sh "$MODELS_DIR" | cut -f1)
- Total size: $(du -sh "$OFFLINE_DIR" | cut -f1)

Installation instructions: See README.md
EOF

# Summary
echo ""
echo "========================================"
echo "Offline Package Created Successfully!"
echo "========================================"
echo ""
echo "Package location: $OFFLINE_DIR/"
echo "Package size: $(du -sh "$OFFLINE_DIR" | cut -f1)"
echo ""
echo "To create archive for transfer:"
echo "  tar -czf docling-ocr-offline.tar.gz $OFFLINE_DIR/"
echo ""
echo "Or for Windows:"
echo "  zip -r docling-ocr-offline.zip $OFFLINE_DIR/"
echo ""

