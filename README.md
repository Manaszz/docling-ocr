# Docling OCR API

<div align="center">

![Docling Logo](https://docling-project.github.io/docling/assets/docling_processing.png)

**AI-Powered Document Conversion API using Docling**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Docling](https://img.shields.io/badge/Docling-2.0+-orange.svg)](https://docling-project.github.io/docling/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 🚀 Features

- **Dual Pipeline Modes**
  - **Standard Pipeline**: Specialized AI models for layout analysis, table extraction, and OCR
  - **VLM Pipeline**: Vision-Language Models for end-to-end document understanding
  
- **Advanced OCR Capabilities**
  - EasyOCR support (multi-language, GPU acceleration)
  - Tesseract integration
  - RapidOCR for high performance
  - Automatic detection of scanned vs. digital PDFs

- **Intelligent Document Processing**
  - Layout analysis with RT-DETR
  - Table structure recognition with TableFormer
  - Image classification
  - Code and formula detection
  
- **MiD-OCR API Compatibility**
  - Drop-in replacement for MiD-OCR
  - Same API endpoints and response formats
  - Easy migration path

- **RAG-Ready Features**
  - Document chunking for vector databases
  - Metadata extraction
  - Structured table data export
  - Multiple output formats (Markdown, HTML, JSON, DocTags)

- **Production Features**
  - Archive support (ZIP, RAR, 7Z)
  - Docker deployment
  - On-premise/air-gapped environment support
  - RESTful API with OpenAPI documentation
  - Modern web UI

## 📋 Supported Formats

| Category | Formats |
|----------|---------|
| **Documents** | PDF, DOCX, DOC, TXT |
| **Spreadsheets** | XLSX, XLS, CSV |
| **Presentations** | PPTX, PPT |
| **Web** | HTML, HTM, XML |
| **Images** | JPG, JPEG, PNG, GIF, BMP, TIFF |
| **E-books** | EPUB |
| **Archives** | ZIP, RAR, 7Z |

## 🔧 Quick Start

### Docker (Recommended)

```bash
# 1. Clone repository
git clone <repository-url>
cd docling-ocr

# 2. Create environment file
cp env.example .env

# 3. Build and run
docker-compose up -d

# 4. Access service
# Web UI: http://localhost:8002
# API Docs: http://localhost:8002/docs
```

### Local Installation

```bash
# Linux/Mac
./install.sh

# Windows
install.bat
```

## 📖 API Documentation

### Base URL

```
/ocr/docling
```

### 1. Health Check

```http
GET /ocr/docling/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "pipeline_mode": "standard",
  "docling_version": "2.0.0",
  "models_loaded": true,
  "ocr_enabled": true,
  "vlm_enabled": false
}
```

### 2. Upload File

```bash
# Convert file to JSON
curl -X POST "http://localhost:8002/ocr/docling/upload" \
  -F "file=@document.pdf"

# Convert file to MD
curl -X POST "http://localhost:8002/ocr/docling/upload/md" \
  -F "file=@document.pdf" \
  -o output.md
```

### 3. Parse Base64

```bash
curl -X POST "http://localhost:8002/ocr/docling/parse" \
  -H "Content-Type: application/json" \
  -d '{
    "is_base64_or_document": true,
    "docs": [{
      "filename": "document.pdf",
      "data": "'$(base64 -w0 document.pdf)'",
      "type": "application/pdf"
    }]
  }'
```

### 4. Extract Tables (Docling-Specific)

```bash
curl -X POST "http://localhost:8002/ocr/docling/extract/tables" \
  -F "file=@document.pdf"
```

### 5. Chunk for RAG (Docling-Specific)

```bash
curl -X POST "http://localhost:8002/ocr/docling/chunk?chunk_size=1000&chunk_overlap=200" \
  -F "file=@document.pdf"
```

### 6. Pipeline Configuration (Docling-Specific)

```bash
# Get current pipeline config
curl http://localhost:8002/ocr/docling/pipeline

# Switch to VLM mode (requires VLM service)
curl -X POST "http://localhost:8002/ocr/docling/pipeline" \
  -H "Content-Type: application/json" \
  -d '{"mode": "vlm"}'
```

## ⚙️ Configuration

Edit `.env` file to configure:

```bash
# Pipeline Mode
DOCLING_PIPELINE_MODE=standard  # standard or vlm

# OCR Configuration
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr
DOCLING_OCR_LANGUAGES=en,ru
DOCLING_OCR_GPU=false

# VLM Configuration (for VLM mode)
DOCLING_VLM_ENABLED=false
DOCLING_VLM_API_URL=http://localhost:8000/v1/chat/completions
DOCLING_VLM_MODEL=qwen-vl-3b

# Table Processing
DOCLING_TABLE_MODE=accurate  # fast or accurate
```

See `env.example` for all options.

## 🔍 Pipeline Modes

### Standard Pipeline (Default)

Uses specialized AI models:
- **Layout Model**: RT-DETR for document structure
- **TableFormer**: Table structure recognition
- **OCR**: EasyOCR/Tesseract for text extraction
- **Picture Classifier**: Image type detection

**Best for**: Production use, offline/on-premise deployment, reliable performance

### VLM Pipeline

Uses Vision-Language Models for end-to-end processing:
- Single model for entire document
- Supports OpenAI-compatible APIs (vLLM, Ollama)
- Models: Qwen-VL, Pixtral, Granite-Vision, etc.

**Best for**: Experimental use, custom models, specialized document types

## 📥 Model Management

### Download Models

```bash
# Download all required models
python scripts/download_models.py -o ./models

# Verify models
python scripts/download_models.py --verify
```

### Use Local Models

```bash
export DOCLING_ARTIFACTS_PATH=./models
# Or set in .env file
DOCLING_ARTIFACTS_PATH=./models
```

## 🌐 On-Premise Deployment

Docling OCR fully supports air-gapped/offline environments:

1. **Prepare offline package** (on internet-connected machine):
   ```bash
   ./scripts/prepare_offline.sh
   ```

2. **Transfer to offline machine**:
   ```bash
   # Copy offline-deploy/ directory
   scp -r offline-deploy/ user@offline-server:/path/to/install/
   ```

3. **Install on offline machine**:
   ```bash
   cd offline-deploy
   ./install_offline.sh
   ```

See [ON_PREMISE_DEPLOYMENT.md](ON_PREMISE_DEPLOYMENT.md) for detailed instructions.

## 🔄 Migration from MiD-OCR

Docling OCR is API-compatible with MiD-OCR:

1. Change API prefix in client: `/ocr/mid` → `/ocr/docling`
2. Update environment variables (see [MIGRATION_FROM_MID.md](MIGRATION_FROM_MID.md))
3. Test endpoints - response format is compatible

**Advantages over MiD-OCR:**
- Better PDF handling and OCR
- Table structure extraction
- Document chunking for RAG
- Pipeline mode selection
- More output formats

## 🧪 Examples

See `examples/` directory:
- `example_standard_pipeline.py` - Standard mode usage
- `example_vlm_pipeline.py` - VLM mode usage
- `example_table_extraction.py` - Extract structured tables
- `example_chunking.py` - Document chunking for RAG
- `example_batch.py` - Batch processing

## 📚 Documentation

- [Installation Guide](INSTALLATION.md)
- [Deployment Guide](DEPLOYMENT.md)
- [On-Premise Deployment](ON_PREMISE_DEPLOYMENT.md)
- [VLM Setup Guide](VLM_SETUP.md)
- [Migration from MiD-OCR](MIGRATION_FROM_MID.md)
- [API Reference](http://localhost:8002/docs) (when service is running)

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- [Docling](https://docling-project.github.io/docling/) - Core document processing
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - OCR engine
- [MiD-OCR](https://github.com/Manaszz/MiD-OCR) - API design inspiration

## 📞 Support

- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Documentation: [https://docling-project.github.io/docling/](https://docling-project.github.io/docling/)
- Docling Community: [https://github.com/docling-project](https://github.com/docling-project)

---

**Built with ❤️ using Docling**

