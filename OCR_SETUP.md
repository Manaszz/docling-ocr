# OCR Setup Guide - Docling OCR

## Overview

Docling OCR service supports OCR for scanned documents and images. OCR can be toggled on/off via:
- **Web UI**: Toggle switch in status bar
- **API**: `/ocr/docling/pipeline/ocr/toggle` endpoint
- **Config**: `.env` file `DOCLING_OCR_ENABLED` setting

For PaddleOCR and RapidOCR specifics, see `PADDLEOCR_SETUP.md`.

## When OCR is Needed

### ✅ OCR Not Required (Fast Mode)
- Digital PDFs (from Word, Export, etc.)
- DOCX, XLSX, PPTX files
- HTML, Markdown files
- PDFs with embedded text layers

### ⚠️ OCR Required (For Scans)
- Scanned documents
- Photos of documents
- PDFs without text layer
- Images with text (JPG, PNG)

## Supported OCR Engines

### 1. EasyOCR (Default, Recommended)

**Pros**:
- High accuracy for multiple languages
- GPU support for better performance
- No external dependencies
- Python-native

**Cons**:
- Large models (~500MB)
- Slower on CPU
- Requires model download

**Setup**:
```bash
# Models will auto-download on first use
# Or pre-download:
cd docling-ocr
.\venv\Scripts\activate
python -c "import easyocr; easyocr.Reader(['en', 'ru'], gpu=False)"
```

**Configuration** (`.env`):
```bash
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr
DOCLING_OCR_LANGUAGES=en,ru
DOCLING_OCR_GPU=false  # Set to true if GPU available
```

### 2. Tesseract OCR (Alternative)

**Pros**:
- Fast and lightweight
- Well-established
- No Python model downloads
- Lower memory usage

**Cons**:
- Requires external installation
- Lower accuracy for complex layouts
- Less language support

**Setup Windows**:
```bash
# Option 1: Chocolatey
choco install tesseract

# Option 2: Manual Download
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install with language packs (eng, rus)
```

**Setup Linux**:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-rus
```

**Configuration** (`.env`):
```bash
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=tesseract
```

### 3. RapidOCR (PP-OCRv4, Recommended)

**Pros**:
- High accuracy with PP-OCRv4 models
- Lightweight models (~16MB total)
- Fast on CPU and GPU
- Excellent for production and offline use

**Cons**:
- Requires model download (ONNX files)
- GPU support requires torch backend

**Setup**:
```bash
# Download RapidOCR models (PP-OCRv4)
python scripts/download_rapidocr_models.py -o ./models/rapidocr
```

**Configuration** (`.env`):
```bash
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=rapidocr
DOCLING_RAPIDOCR_BACKEND=onnxruntime  # onnxruntime (CPU) or torch (GPU)
DOCLING_RAPIDOCR_MODELS_PATH=./models/rapidocr
DOCLING_RAPIDOCR_TEXT_SCORE=0.5
```

## UI Control

### Toggle in Web Interface

1. Open Web UI: http://localhost:8002
2. Look at status bar (top)
3. Find "Enable OCR for Scans" toggle
4. Click to enable/disable
5. **Note**: Service restart recommended for full effect

### Visual Indicators

- **OCR Status**: Shows "Enabled" or "Disabled"
- **Toggle**: Green when ON, Gray when OFF
- **Warning**: Shown when restart needed

## API Control

### Get Current Status

```bash
# Check OCR status
curl http://localhost:8002/ocr/docling/pipeline

# Response:
{
  "mode": "standard",
  "ocr_enabled": true,
  "ocr_engine": "easyocr",
  "ocr_languages": ["en", "ru"]
}
```

### Enable OCR

```bash
curl -X POST "http://localhost:8002/ocr/docling/pipeline/ocr/toggle" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Response:
{
  "ocr_enabled": true,
  "message": "OCR enabled. Service restart recommended.",
  "restart_required": true
}
```

### Disable OCR

```bash
curl -X POST "http://localhost:8002/ocr/docling/pipeline/ocr/toggle" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

## Model Download

### EasyOCR Models

**Automatic Download** (on first use):
```bash
# OCR will auto-download when processing first scan
# Models stored in: ~/.EasyOCR/model/
```

**Manual Pre-Download**:
```bash
cd docling-ocr
.\venv\Scripts\python.exe download_easyocr.py
```

**Expected Models**:
- `craft_mlt_25k.pth` (~85MB) - Text detection
- `latin_g2.pth` (~50MB) - Latin recognition
- `cyrillic_g2.pth` (~50MB) - Cyrillic recognition

**Total Size**: ~500MB

### RapidOCR Models (PP-OCRv4)

**Download Script**:
```bash
python scripts/download_rapidocr_models.py -o ./models/rapidocr
```

**Expected Models**:
- `ch_PP-OCRv4_det_infer.onnx` (~4.5MB)
- `ch_PP-OCRv4_rec_infer.onnx` (~10MB)
- `ch_ppocr_mobile_v2.0_cls_infer.onnx` (~1.4MB)
- `ppocr_keys_v1.txt` (~300KB)

**Total Size**: ~16MB

### Verify Models

```bash
# Check EasyOCR models location
python -c "import easyocr; r = easyocr.Reader(['en'], verbose=False); print(r.model_storage_directory)"

# Check if models exist
ls ~/.EasyOCR/model/  # Linux/Mac
dir %USERPROFILE%\.EasyOCR\model\  # Windows
```

## Configuration Options

### Environment Variables (`.env`)

```bash
# Enable/Disable OCR
DOCLING_OCR_ENABLED=true

# OCR Engine: easyocr, tesseract, rapidocr
DOCLING_OCR_ENGINE=easyocr

# Languages (comma-separated)
DOCLING_OCR_LANGUAGES=en,ru

# GPU Support (EasyOCR and RapidOCR with torch backend)
DOCLING_OCR_GPU=false

# RapidOCR configuration (when engine=rapidocr)
DOCLING_RAPIDOCR_BACKEND=onnxruntime  # onnxruntime (CPU) or torch (GPU)
DOCLING_RAPIDOCR_MODELS_PATH=./models/rapidocr
DOCLING_RAPIDOCR_TEXT_SCORE=0.5
```

### Supported Languages

**EasyOCR**:
- English (`en`)
- Russian (`ru`)
- Chinese (`ch_sim`, `ch_tra`)
- German (`de`)
- French (`fr`)
- Spanish (`es`)
- [80+ more languages](https://github.com/JaidedAI/EasyOCR#supported-languages)

**Tesseract**:
- Depends on installed language packs
- Common: `eng`, `rus`, `deu`, `fra`, `spa`

**RapidOCR (PP-OCRv4)**:
- 109+ languages supported (PaddleOCR models)
- Configure via `DOCLING_OCR_LANGUAGES`

## Performance Comparison

### EasyOCR
- **Accuracy**: ★★★★★ (95%+)
- **Speed (CPU)**: ★★☆☆☆ (3-10 sec/page)
- **Speed (GPU)**: ★★★★☆ (1-3 sec/page)
- **Memory**: ~1-2GB
- **Setup**: Easy (Python only)

### Tesseract
- **Accuracy**: ★★★★☆ (85-90%)
- **Speed**: ★★★★☆ (1-3 sec/page)
- **Memory**: ~500MB
- **Setup**: Medium (external install)

### RapidOCR (PP-OCRv4)
- **Accuracy**: ★★★★☆ (90-95%)
- **Speed**: ★★★★★ (<1 sec/page)
- **Memory**: ~200MB
- **Setup**: Easy (download ONNX models once)

## Recommendations

### For Digital Documents Only
```bash
# Disable OCR for best performance
DOCLING_OCR_ENABLED=false
```

**Benefits**:
- Faster conversion (1-3 sec vs 3-10 sec)
- Lower memory usage
- Simpler setup

### For Mixed (Digital + Scans)
```bash
# Use EasyOCR for maximum scan accuracy
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr
```

**Benefits**:
- High accuracy on scans
- Works for both types
- Automatic model management

### For Production (High Volume)
```bash
# Use RapidOCR (PP-OCRv4) for speed + accuracy
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=rapidocr
DOCLING_TABLE_MODE=fast
```

**Benefits**:
- Fastest processing
- Lower resource usage
- Strong accuracy with PP-OCRv4

### For Highest Accuracy
```bash
# Use EasyOCR with GPU
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr
DOCLING_OCR_GPU=true
DOCLING_TABLE_MODE=accurate
```

**Benefits**:
- Best accuracy
- Reasonable speed with GPU
- Best table extraction

## Troubleshooting

### Models Not Downloading

**Problem**: EasyOCR fails to download models

**Solution 1**: Pre-download manually
```bash
python download_easyocr.py
```

**Solution 2**: Download to custom location
```bash
# Set custom model directory
export EASYOCR_MODULE_PATH=/path/to/models  # Linux
$env:EASYOCR_MODULE_PATH="C:\path\to\models"  # Windows
```

**Solution 3**: Use alternative OCR
```bash
# Switch to Tesseract or RapidOCR
DOCLING_OCR_ENGINE=tesseract
```

### OCR Too Slow

**Problem**: OCR takes too long

**Solutions**:
1. Enable GPU (if available)
```bash
DOCLING_OCR_GPU=true
```

2. Switch to faster engine
```bash
DOCLING_OCR_ENGINE=rapidocr
```

3. Reduce languages
```bash
DOCLING_OCR_LANGUAGES=en  # Only English
```

### OCR Not Working After Toggle

**Problem**: Toggle in UI doesn't activate OCR

**Solution**: Restart service
```bash
# Stop current service
Stop-Process -Name python -Force

# Restart
cd docling-ocr
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

### Memory Issues

**Problem**: Out of memory during OCR

**Solutions**:
1. Switch to lighter OCR
```bash
DOCLING_OCR_ENGINE=rapidocr  # or tesseract
```

2. Disable table accuracy
```bash
DOCLING_TABLE_MODE=fast
```

3. Reduce workers
```bash
WORKERS=1  # or 2
```

## Testing OCR

### Test Script

```bash
cd docling-ocr
.\venv\Scripts\python.exe -c "
import easyocr
import numpy as np
from PIL import Image

# Create test image with text
img = Image.new('RGB', (400, 100), color='white')
from PIL import ImageDraw, ImageFont
draw = ImageDraw.Draw(img)
draw.text((10, 30), 'Test OCR Text', fill='black')
img.save('test_ocr.png')

# Test OCR
reader = easyocr.Reader(['en'], gpu=False)
result = reader.readtext('test_ocr.png')
print('OCR Result:', result)
"
```

### Test via API

```bash
# Create test document
echo "Test Document" > test.txt

# Convert (should work without OCR)
curl -X POST "http://localhost:8002/ocr/docling/upload" \
  -F "file=@test.txt"

# For scan testing, use actual scanned PDF or image
```

## Current Status

**Default Configuration**:
- OCR: **ENABLED** ✅
- Engine: **EasyOCR**
- Languages: **English, Russian**
- GPU: **Disabled** (CPU mode)
- Auto-download: **Enabled**

**Models**:
- Docling models: ✅ Downloaded (2.5GB)
- EasyOCR models: ⏳ Will download on first scan

**UI Control**: ✅ Toggle available in status bar

---

**Quick Start**:
1. Toggle OCR in UI if needed
2. Upload digital PDFs (OCR optional)
3. Upload scanned PDFs (OCR required, auto-downloads models)
4. Models download automatically on first use

**For immediate use**: OCR is **ready** - models will download when needed!

