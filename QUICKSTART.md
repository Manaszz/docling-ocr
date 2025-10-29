# Quick Start Guide

Get Docling OCR running in 5 minutes!

## Prerequisites

- Python 3.10+ or Docker
- 5GB+ disk space

## Option 1: Docker (Easiest)

```bash
# 1. Clone and enter directory
git clone <repository-url>
cd docling-ocr

# 2. Create environment file
cp env.example .env

# 3. Start service
docker-compose up -d

# 4. Check health
curl http://localhost:8002/ocr/docling/health

# 5. Open web UI
open http://localhost:8002
```

Done! The service is running.

## Option 2: Local Installation

### Linux/Mac

```bash
# 1. Clone and enter directory
git clone <repository-url>
cd docling-ocr

# 2. Run install script
chmod +x install.sh
./install.sh

# 3. Activate environment
source venv/bin/activate

# 4. Start service
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Windows

```cmd
REM 1. Clone and enter directory
git clone <repository-url>
cd docling-ocr

REM 2. Run install script
install.bat

REM 3. Activate environment
venv\Scripts\activate

REM 4. Start service
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## First Steps

### 1. Check Service Health

```bash
curl http://localhost:8002/ocr/docling/health
```

Expected response:
```json
{
  "status": "healthy",
  "pipeline_mode": "standard",
  "models_loaded": true
}
```

### 2. Convert Your First Document

#### Via Web UI

1. Open http://localhost:8002
2. Drag & drop a PDF file
3. Click "Convert Documents"
4. Download result

#### Via API

```bash
# Convert to JSON
curl -X POST "http://localhost:8002/ocr/docling/upload" \
  -F "file=@your-document.pdf"

# Convert to Markdown file
curl -X POST "http://localhost:8002/ocr/docling/upload/md" \
  -F "file=@your-document.pdf" \
  -o output.md
```

### 3. Extract Tables

```bash
curl -X POST "http://localhost:8002/ocr/docling/extract/tables" \
  -F "file=@document-with-tables.pdf"
```

### 4. Chunk for RAG

```bash
curl -X POST "http://localhost:8002/ocr/docling/chunk?chunk_size=1000" \
  -F "file=@your-document.pdf"
```

## Configuration

Edit `.env` file to customize:

```bash
# Change port
PORT=8003

# Add OCR languages
DOCLING_OCR_LANGUAGES=en,ru,de,fr

# Enable GPU acceleration
DOCLING_OCR_GPU=true

# Use fast table mode (lower quality, faster)
DOCLING_TABLE_MODE=fast
```

Restart service after changes.

## Common Issues

### Models Not Found

**Solution**: Download models

```bash
python scripts/download_models.py -o ./models
```

### Port Already in Use

**Solution**: Change port in `.env`

```bash
PORT=8003
```

### OCR Not Working

**Solution**: Enable OCR in `.env`

```bash
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr
```

## Next Steps

- [Full Installation Guide](INSTALLATION.md)
- [API Documentation](http://localhost:8002/docs)
- [Configuration Options](README.md#configuration)
- [Examples](examples/)

## Getting Help

- Check [README.md](README.md) for full documentation
- Review [INSTALLATION.md](INSTALLATION.md) for detailed setup
- See [API Docs](http://localhost:8002/docs) for endpoint reference

## Quick Commands

```bash
# Start service
docker-compose up -d

# Stop service
docker-compose down

# View logs
docker-compose logs -f

# Check health
curl http://localhost:8002/ocr/docling/health

# Test conversion
echo "Test" > test.txt
curl -X POST "http://localhost:8002/ocr/docling/upload" -F "file=@test.txt"
```

That's it! You're ready to convert documents with Docling OCR! 🚀

