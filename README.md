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

- **Dual Pipeline Support (Simultaneous)**
  - **Standard Pipeline (`std`)**: Specialized AI models for layout analysis, table extraction, and OCR
  - **VLM Pipeline (`vlm`)**: Vision-Language Models for end-to-end document understanding
  - **No configuration switching required** - select pipeline per request with `?pipeline=` parameter
  
- **Advanced OCR Capabilities**
  - EasyOCR support (multi-language, GPU acceleration)
  - Tesseract integration
  - RapidOCR for high performance
  - Automatic detection of scanned vs. digital PDFs (auto/always/never modes)

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
# Convert file using standard pipeline (default)
curl -X POST "http://localhost:8002/ocr/docling/upload" \
  -F "file=@document.pdf"

# Convert file using VLM pipeline
curl -X POST "http://localhost:8002/ocr/docling/upload?pipeline=vlm" \
  -F "file=@document.pdf"

# Standard pipeline with specific OCR mode
curl -X POST "http://localhost:8002/ocr/docling/upload?pipeline=std&ocr_mode=always" \
  -F "file=@document.pdf"

# Convert to MD file
curl -X POST "http://localhost:8002/ocr/docling/upload/md?pipeline=std" \
  -F "file=@document.pdf" \
  -o output.md
```

### 3. Parse Base64

```bash
# Standard pipeline
curl -X POST "http://localhost:8002/ocr/docling/parse?pipeline=std" \
  -H "Content-Type: application/json" \
  -d '{
    "is_base64_or_document": true,
    "docs": [{
      "filename": "document.pdf",
      "data": "'$(base64 -w0 document.pdf)'",
      "type": "application/pdf"
    }]
  }'

# VLM pipeline
curl -X POST "http://localhost:8002/ocr/docling/parse?pipeline=vlm" \
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
# Standard pipeline
curl -X POST "http://localhost:8002/ocr/docling/extract/tables?pipeline=std" \
  -F "file=@document.pdf"

# VLM pipeline
curl -X POST "http://localhost:8002/ocr/docling/extract/tables?pipeline=vlm" \
  -F "file=@document.pdf"
```

### 5. Chunk for RAG (Docling-Specific)

```bash
# Standard pipeline
curl -X POST "http://localhost:8002/ocr/docling/chunk?pipeline=std&chunk_size=1000&chunk_overlap=200" \
  -F "file=@document.pdf"

# VLM pipeline
curl -X POST "http://localhost:8002/ocr/docling/chunk?pipeline=vlm&chunk_size=1000&chunk_overlap=200" \
  -F "file=@document.pdf"
```

### 6. Pipeline Status (Docling-Specific)

```bash
# Get status of both pipelines
curl http://localhost:8002/ocr/docling/pipeline
```

**Response:**
```json
{
  "pipelines": {
    "std": {
      "name": "Standard Pipeline",
      "available": true,
      "loaded": true,
      "ocr_enabled": true
    },
    "vlm": {
      "name": "VLM Pipeline",
      "available": true,
      "loaded": false,
      "enabled": true,
      "model": "qwen/qwen3-vl-235b-a22b-instruct"
    }
  },
  "usage": {
    "info": "Both pipelines available simultaneously",
    "parameter": "Use ?pipeline=std or ?pipeline=vlm on any endpoint",
    "default": "std (standard pipeline)"
  }
}
```

## ⚙️ Configuration

Edit `.env` file to configure:

```bash
# OCR Configuration (Standard Pipeline)
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr
DOCLING_OCR_LANGUAGES=en,ru
DOCLING_OCR_GPU=false

# VLM Configuration (VLM Pipeline)
DOCLING_VLM_ENABLED=true  # Enable VLM pipeline
DOCLING_VLM_API_URL=http://localhost:8000/v1/chat/completions
DOCLING_VLM_MODEL=qwen/qwen3-vl-235b-a22b-instruct
DOCLING_VLM_PROMPT=Convert this document page to markdown format.

# Table Processing
DOCLING_TABLE_MODE=accurate  # fast or accurate
```

**Note:** Both pipelines can be used simultaneously. Select pipeline per request using `?pipeline=std` or `?pipeline=vlm`.

See `env.example` for all options.

## 🔍 Pipeline Modes

Both pipelines available simultaneously - no configuration switching required!

### Standard Pipeline (`?pipeline=std`) - Default

Uses specialized AI models:
- **Layout Model**: RT-DETR for document structure
- **TableFormer**: Table structure recognition
- **OCR**: EasyOCR/Tesseract for text extraction
  - `ocr_mode=auto` - Auto-detect if OCR needed (default)
  - `ocr_mode=always` - Force OCR
  - `ocr_mode=never` - Disable OCR
- **Picture Classifier**: Image type detection

**Best for**: Production use, offline/on-premise deployment, reliable performance

### VLM Pipeline (`?pipeline=vlm`)

Uses Vision-Language Models for end-to-end processing:
- Single model for entire document
- Supports OpenAI-compatible APIs (vLLM, Ollama, OpenRouter)
- Models: Qwen3-VL, Qwen2.5-VL, Pixtral, Granite-Vision, etc.
- Default: `qwen/qwen3-vl-235b-a22b-instruct`
- Customizable prompts: Use `?vlm_prompt=custom prompt` for specialized instructions

**Best for**: Complex documents, experimental use, custom models, specialized document types

### Usage Examples

```bash
# Standard pipeline with auto OCR (default)
curl -X POST "http://localhost:8002/ocr/docling/upload" -F "file=@doc.pdf"

# Standard pipeline, force OCR
curl -X POST "http://localhost:8002/ocr/docling/upload?pipeline=std&ocr_mode=always" -F "file=@doc.pdf"

# VLM pipeline
curl -X POST "http://localhost:8002/ocr/docling/upload?pipeline=vlm" -F "file=@doc.pdf"

# VLM pipeline with custom prompt
curl -X POST "http://localhost:8002/ocr/docling/upload?pipeline=vlm&vlm_prompt=Extract all text and tables from this document in structured markdown format." -F "file=@doc.pdf"
```

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

