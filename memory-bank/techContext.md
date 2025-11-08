# Technical Context: Docling OCR API

## Technology Stack

### Core Framework
- **FastAPI 0.115+**: Modern async Python web framework
- **Python 3.10+**: Language requirement with type hints
- **Uvicorn**: ASGI server for production deployment

### AI & Document Processing
- **Docling 2.0+**: IBM's document AI processing library
- **Docling Core 2.0+**: Core processing components
- **Docling IBM Models 2.0+**: Pre-trained AI models

### OCR Engines
- **EasyOCR 1.7+**: Primary OCR engine (80+ languages, GPU support)
- **Tesseract**: Alternative OCR engine (system installation required)
- **RapidOCR**: High-performance OCR option

### Data Processing & Validation
- **Pydantic 2.0+**: Data validation and settings management
- **Pydantic Settings**: Environment configuration handling

### File & Archive Handling
- **python-magic**: File type detection (Windows/Linux variants)
- **PyPDF2/PyPDF**: PDF processing and scanned/digital detection
- **python-multipart**: FastAPI file upload handling
- **rarfile**: RAR archive support
- **py7zr**: 7Z archive support

### External API Integration
- **OpenAI 1.0+**: VLM pipeline API client
- **httpx**: HTTP client for API calls

### Utilities & Dependencies
- **Pillow**: Image processing
- **opencv-python-headless**: Computer vision operations
- **tqdm**: Progress bars for model downloads
- **python-dotenv**: Environment file loading

## Development Environment

### Local Development Setup

#### Prerequisites
```bash
# Python 3.10+
python --version  # Must be 3.10 or higher

# Git for version control
git --version

# Optional: CUDA for GPU acceleration
nvidia-smi  # Check GPU availability
```

#### Installation Scripts
- **Linux/Mac**: `./install.sh` - Automated dependency installation
- **Windows**: `install.bat` - Windows-specific setup
- **Docker**: `docker-compose up -d` - Containerized deployment

### Environment Configuration

#### Required Environment Variables
```bash
# API Configuration
API_PREFIX=/ocr/docling
PORT=8002
HOST=0.0.0.0

# Model Configuration
DOCLING_ARTIFACTS_PATH=./models

# OCR Configuration
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr
DOCLING_OCR_LANGUAGES=en,ru
DOCLING_OCR_GPU=false

# VLM Configuration
DOCLING_VLM_ENABLED=false
DOCLING_VLM_API_URL=http://localhost:8000/v1/chat/completions
DOCLING_VLM_MODEL=qwen/qwen3-vl-235b-a22b-instruct
```

#### Optional Configuration
```bash
# Performance Tuning
MAX_WORKERS=4
TEMP_DIR=./temp

# Security
MAX_FILE_SIZE_MB=100
ALLOWED_EXTENSIONS=pdf,docx,xlsx,pptx,txt,html,xml,epub,jpg,jpeg,png,gif,bmp,tiff,zip,rar,7z

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## Technical Constraints

### System Requirements

#### Minimum Requirements
- **RAM**: 4GB
- **CPU**: 2 cores
- **Disk**: 10GB (including models)
- **Network**: Internet for initial model download

#### Recommended Requirements
- **RAM**: 8GB+
- **CPU**: 4+ cores
- **Disk**: 20GB+ SSD
- **GPU**: NVIDIA GPU with CUDA (optional, 2-3x speedup)

### Operating System Support

#### Primary Support
- **Linux**: Ubuntu 20.04+, CentOS 7+, RHEL 8+
- **macOS**: 11.0+ (Intel/Apple Silicon)
- **Windows**: 10/11 with WSL2 recommended

#### Container Support
- **Docker**: 20.10+
- **docker-compose**: 2.0+

### Python Version Constraints

#### Supported Versions
- **Python 3.10**: Minimum required
- **Python 3.11**: Fully supported, recommended
- **Python 3.12**: Compatible (latest features)

#### Dependency Conflicts
- **Pydantic**: Must use v2.x (incompatible with v1.x)
- **OpenCV**: Must use headless version to avoid GUI dependencies

## Dependencies Management

### Core Dependencies

#### Production Dependencies (`requirements.txt`)
```txt
# Web Framework
fastapi>=0.115.0
uvicorn[standard]>=0.32.0

# Document AI
docling>=2.0.0
docling-core>=2.0.0
docling-ibm-models>=2.0.0

# OCR
easyocr>=1.7.0

# File Handling
python-multipart>=0.0.9
python-magic-bin>=0.4.14; sys_platform == 'win32'
python-magic>=0.4.27; sys_platform != 'win32'
rarfile>=4.2
py7zr>=0.21.0

# PDF Processing
pypdfium2>=4.30.0
pypdf>=3.0.0

# Image Processing
Pillow>=10.0.0
opencv-python-headless>=4.8.0

# Configuration
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0

# External APIs
openai>=1.0.0
httpx>=0.25.0

# Utilities
tqdm>=4.66.0
```

#### Development Dependencies (`requirements-dev.txt`)
```txt
# Testing
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0

# Code Quality
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0

# Documentation
mkdocs>=1.4.0
mkdocs-material>=9.0.0
```

## Model Management

### AI Models Required

#### Docling Models (Local Storage)
```
models/
├── ds4sd--CodeFormulaV2/          # Code and formula detection
├── ds4sd--docling-layout-heron/   # Layout analysis
├── ds4sd--docling-models/         # Table and structure models
├── ds4sd--DocumentFigureClassifier/ # Image classification
└── EasyOcr/                       # OCR models (en, ru, etc.)
```

#### Model Download Process
```bash
# Download all models
python scripts/download_models.py -o ./models

# Verify downloads
python scripts/download_models.py --verify

# Check model sizes
python scripts/download_models.py --sizes
```

#### Offline Deployment
```bash
# Prepare offline package
./scripts/prepare_offline.sh

# Transfer to air-gapped environment
scp -r offline-deploy/ user@offline-server:/path/to/install/

# Install offline
cd offline-deploy && ./install_offline.sh
```

## Development Workflow

### Code Organization

#### Directory Structure
```
docling-ocr/
├── app/                    # Application code
│   ├── main.py            # FastAPI application
│   ├── core/              # Configuration
│   ├── api/v1/            # API endpoints
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── static/            # Web assets
│   ├── templates/         # HTML templates
│   └── utils/             # Utilities
├── scripts/               # Management scripts
├── models/                # AI models
├── temp/                  # Temporary files
├── tests/                 # Test suite
└── docs/                  # Documentation
```

### Development Commands

#### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python -m app.main

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

# Run tests
pytest

# Code formatting
black app/
isort app/
```

#### Docker Development
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up -d --build

# Enter container
docker-compose exec app bash
```

### Testing Strategy

#### Unit Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_health.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run async tests
pytest -k "async"
```

#### Integration Tests
```bash
# Test API endpoints
python test_live_api.py

# Test model downloads
python scripts/verify_installation.py
```

### Deployment Options

#### Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  docling-ocr:
    build: .
    ports:
      - "8002:8002"
    volumes:
      - ./models:/app/models
      - ./temp:/app/temp
    environment:
      - DOCLING_ARTIFACTS_PATH=/app/models
      - TEMP_DIR=/app/temp
```

#### Systemd Service
```ini
# /etc/systemd/system/docling-ocr.service
[Unit]
Description=Docling OCR API
After=network.target

[Service]
Type=simple
User=docling
WorkingDirectory=/opt/docling-ocr
ExecStart=/opt/docling-ocr/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8002
Restart=always

[Install]
WantedBy=multi-user.target
```

## Performance Considerations

### Resource Usage Patterns

#### Memory Usage
- **Base**: 2-3GB (models loaded)
- **Per Request**: 500MB-2GB (document processing)
- **Peak**: 4-6GB (concurrent processing)

#### CPU Usage
- **Idle**: <5% (health checks, background tasks)
- **Active**: 50-100% per core (document processing)
- **Concurrent**: Scales with CPU cores

#### GPU Usage (Optional)
- **OCR Processing**: 2-3x faster with CUDA
- **Memory**: 2-4GB VRAM required
- **Compatibility**: CUDA 11.8+ required

### Scaling Considerations

#### Vertical Scaling
- **RAM**: More RAM allows larger documents
- **CPU**: More cores allow concurrent processing
- **GPU**: Accelerates OCR operations

#### Horizontal Scaling
- **Stateless Design**: Supports load balancing
- **Shared Storage**: Models can be shared across instances
- **Session Affinity**: Not required (no state)

### Monitoring & Observability

#### Health Endpoints
```json
GET /ocr/docling/health
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": true,
  "memory_usage": "2.3GB",
  "processing_queue": 0
}
```

#### Logging Configuration
```python
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)
```

## Security Considerations

### File Upload Security
- **Type Validation**: Magic number checking
- **Size Limits**: Configurable maximum file sizes
- **Path Traversal**: Secure temporary file handling
- **Cleanup**: Automatic temporary file removal

### Network Security
- **CORS**: Configurable origin restrictions
- **Rate Limiting**: Not implemented (can be added)
- **HTTPS**: Recommended for production
- **API Keys**: Not implemented (can be added)

### Data Privacy
- **Local Processing**: All processing happens locally
- **No External Calls**: Except for VLM pipeline (optional)
- **Temp File Security**: Secure deletion and cleanup
- **Log Security**: No sensitive data in logs

---

**Document Purpose**: Defines the technical foundation, dependencies, and operational requirements for development and deployment.

