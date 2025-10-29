# Installation Guide

Complete installation instructions for Docling OCR API.

## Table of Contents

- [Requirements](#requirements)
- [Local Installation](#local-installation)
  - [Linux/Mac](#linuxmac)
  - [Windows](#windows)
- [Docker Installation](#docker-installation)
- [Model Setup](#model-setup)
- [OCR Engine Setup](#ocr-engine-setup)
- [Verification](#verification)

## Requirements

### System Requirements

- **OS**: Linux, macOS, or Windows 10/11
- **Python**: 3.10 or higher
- **RAM**: Minimum 4GB, recommended 8GB+
- **Disk Space**: 2-5GB (depending on models)

### Optional Requirements

- **GPU**: NVIDIA GPU with CUDA for GPU-accelerated OCR
- **Docker**: For containerized deployment

## Local Installation

### Linux/Mac

#### 1. Clone Repository

```bash
git clone <repository-url>
cd docling-ocr
```

#### 2. Run Installation Script

```bash
chmod +x install.sh
./install.sh
```

The script will:
- Check Python version
- Create virtual environment
- Install dependencies
- Download models (optional)
- Verify installation

#### 3. Configure Environment

```bash
# Copy example environment file
cp env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

Key settings to configure:
- `PORT` - API port (default: 8002)
- `DOCLING_OCR_LANGUAGES` - OCR languages (e.g., en,ru,de)
- `DOCLING_OCR_GPU` - Enable GPU acceleration (true/false)

#### 4. Start Service

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

Or with hot reload for development:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### Windows

#### 1. Clone Repository

```powershell
git clone <repository-url>
cd docling-ocr
```

#### 2. Run Installation Script

```cmd
install.bat
```

The script will:
- Check Python version
- Create virtual environment
- Install dependencies
- Download models (optional)
- Verify installation

#### 3. Configure Environment

```cmd
# Copy example environment file
copy env.example .env

# Edit with notepad or your preferred editor
notepad .env
```

#### 4. Start Service

```cmd
venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## Docker Installation

### Quick Start

```bash
# 1. Copy environment file
cp env.example .env

# 2. Build and run with docker-compose
docker-compose up -d

# 3. View logs
docker-compose logs -f

# 4. Stop service
docker-compose down
```

### Custom Build

```bash
# Build image
docker build -t docling-ocr:latest .

# Run container
docker run -d \
  --name docling-ocr \
  -p 8002:8002 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/temp:/app/temp \
  -e DOCLING_OCR_LANGUAGES=en,ru \
  docling-ocr:latest
```

### With GPU Support

Modify `docker-compose.yml`:

```yaml
services:
  docling-ocr:
    # ... other settings ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - DOCLING_OCR_GPU=true
```

Then run:

```bash
docker-compose up -d
```

## Model Setup

### Automatic Download

During installation, you can choose to download models automatically.

### Manual Download

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Download models
python scripts/download_models.py -o ./models
```

### Verify Models

```bash
python scripts/download_models.py --verify
```

### Model Storage

Models are stored in:
- Local: `./models/`
- Docker: `/app/models` (mounted volume)

Set `DOCLING_ARTIFACTS_PATH` to use custom location.

## OCR Engine Setup

### EasyOCR (Default)

Installed automatically with dependencies. Supports 80+ languages.

**Configuration:**

```bash
DOCLING_OCR_ENGINE=easyocr
DOCLING_OCR_LANGUAGES=en,ru,de  # Add languages as needed
DOCLING_OCR_GPU=false  # Set to true for GPU
```

**Supported Languages**: en, ru, de, fr, es, it, pt, zh_sim, zh_tra, ja, ko, ar, and more.

### Tesseract

Requires system installation.

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-rus  # Russian
sudo apt-get install tesseract-ocr-deu  # German
```

**macOS:**

```bash
brew install tesseract
brew install tesseract-lang  # All languages
```

**Windows:**

Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

**Configuration:**

```bash
DOCLING_OCR_ENGINE=tesseract
```

### RapidOCR

Install additional package:

```bash
pip install rapidocr-onnxruntime
```

**Configuration:**

```bash
DOCLING_OCR_ENGINE=rapidocr
```

## Verification

### Run Verification Script

```bash
python scripts/verify_installation.py
```

This checks:
- Python version
- Dependencies
- Models
- Directories
- Environment configuration

### Test API

#### Health Check

```bash
curl http://localhost:8002/ocr/docling/health
```

Expected response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "pipeline_mode": "standard",
  "models_loaded": true,
  "ocr_enabled": true
}
```

#### Convert Test Document

```bash
# Create test file
echo "Hello, Docling!" > test.txt

# Convert
curl -X POST "http://localhost:8002/ocr/docling/upload" \
  -F "file=@test.txt"
```

#### Access Web UI

Open browser: http://localhost:8002

## Troubleshooting

### Models Not Found

**Symptom:** `models_loaded: false` in health check

**Solution:**

```bash
python scripts/download_models.py -o ./models
# Set environment variable
export DOCLING_ARTIFACTS_PATH=./models
```

### OCR Not Working

**Symptom:** Empty text from scanned PDFs

**Solution:**

1. Check OCR is enabled:
   ```bash
   DOCLING_OCR_ENABLED=true
   ```

2. Verify OCR engine installed:
   ```bash
   # For EasyOCR
   pip list | grep easyocr
   
   # For Tesseract
   tesseract --version
   ```

3. Check logs for errors:
   ```bash
   # Docker
   docker-compose logs -f
   
   # Local
   # Check console output
   ```

### Port Already in Use

**Symptom:** "Address already in use" error

**Solution:**

Change port in `.env`:

```bash
PORT=8003  # Use different port
```

Or stop service using port 8002:

```bash
# Find process
lsof -i :8002  # Linux/Mac
netstat -ano | findstr :8002  # Windows

# Kill process
kill -9 <PID>
```

### GPU Not Detected

**Symptom:** OCR slow, GPU not used

**Solution:**

1. Check CUDA installation:
   ```bash
   nvidia-smi
   ```

2. Install GPU-enabled packages:
   ```bash
   pip install easyocr[gpu]
   ```

3. Enable GPU in config:
   ```bash
   DOCLING_OCR_GPU=true
   ```

## Next Steps

- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [On-Premise Deployment](ON_PREMISE_DEPLOYMENT.md) - Air-gapped setup
- [API Documentation](http://localhost:8002/docs) - Interactive API docs

## Support

For issues and questions:
- GitHub Issues: [repository issues](https://github.com/your-repo/issues)
- Docling Documentation: https://docling-project.github.io/docling/

