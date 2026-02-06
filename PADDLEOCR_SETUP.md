# PaddleOCR Integration Guide

This guide explains how to configure Docling OCR API to use PaddleOCR models instead of the default EasyOCR.

## Overview

Docling OCR API supports two ways to use PaddleOCR:

1. **Standard Pipeline (RapidOCR)**: Uses PP-OCRv4 models in ONNX format via RapidOCR wrapper
2. **VLM Pipeline (PaddleOCR-VL)**: Uses PaddleOCR-VL 0.9B vision-language model for end-to-end document parsing

## Quick Start

### Option 1: RapidOCR for Standard Pipeline (Recommended)

```bash
# 1. Download models
python scripts/download_rapidocr_models.py -o ./models/rapidocr

# 2. Configure environment
export DOCLING_OCR_ENGINE=rapidocr
export DOCLING_RAPIDOCR_MODELS_PATH=./models/rapidocr

# 3. Start the service
python -m app.main
```

### Option 2: PaddleOCR-VL for VLM Pipeline

If you have PaddleOCR-VL deployed on vLLM:

```bash
# Configure VLM pipeline
export DOCLING_VLM_ENABLED=true
export DOCLING_VLM_API_URL=http://your-vllm-server:8080/v1/chat/completions
export DOCLING_VLM_MODEL=PaddleOCR-VL-0.9B
export DOCLING_VLM_PROMPT=OCR:
```

---

## Standard Pipeline: RapidOCR Configuration

### Model Files

RapidOCR uses PaddleOCR PP-OCRv4 models in ONNX format:

| File | Size | Description |
|------|------|-------------|
| `ch_PP-OCRv4_det_infer.onnx` | ~4.5 MB | Text detection model |
| `ch_PP-OCRv4_rec_infer.onnx` | ~10 MB | Text recognition model |
| `ch_ppocr_mobile_v2.0_cls_infer.onnx` | ~1.4 MB | Text orientation classifier |
| `ppocr_keys_v1.txt` | ~300 KB | Character dictionary (6000+ chars) |

### Downloading Models

#### Using the Download Script

```bash
# Download to default location
python scripts/download_rapidocr_models.py

# Download to custom location
python scripts/download_rapidocr_models.py -o /path/to/models

# Force re-download
python scripts/download_rapidocr_models.py --force

# Verify existing models
python scripts/download_rapidocr_models.py --verify
```

#### Manual Download

Download from HuggingFace:
- https://huggingface.co/SWHL/RapidOCR/tree/main/models

### Environment Variables

```bash
# Required
DOCLING_OCR_ENGINE=rapidocr

# Optional
DOCLING_RAPIDOCR_BACKEND=onnxruntime  # onnxruntime (CPU) or torch (GPU)
DOCLING_RAPIDOCR_MODELS_PATH=/path/to/models
DOCLING_RAPIDOCR_TEXT_SCORE=0.5  # Confidence threshold (0.0-1.0)
```

### Supported Languages

RapidOCR supports multiple languages. Configure via:

```bash
DOCLING_OCR_LANGUAGES=en,ru,chinese
```

Supported language codes: `english`, `chinese`, `korean`, `japan`, `russian`, etc.

---

## VLM Pipeline: PaddleOCR-VL Configuration

### Prerequisites

PaddleOCR-VL must be deployed as an OpenAI-compatible inference server (e.g., via vLLM).

### Environment Variables

```bash
DOCLING_VLM_ENABLED=true
DOCLING_VLM_API_URL=http://your-vllm-server:8080/v1/chat/completions
DOCLING_VLM_API_KEY=your-api-key
DOCLING_VLM_MODEL=PaddleOCR-VL-0.9B
DOCLING_VLM_TIMEOUT=120
DOCLING_VLM_TEMPERATURE=0.0
DOCLING_VLM_MAX_TOKENS=4096
DOCLING_VLM_PROMPT=OCR:
```

### PaddleOCR-VL Prompts

PaddleOCR-VL uses specific prompts for different tasks:

| Task | Prompt |
|------|--------|
| Text recognition | `OCR:` |
| Table recognition | `Table Recognition:` |
| Formula recognition | `Formula Recognition:` |
| Chart recognition | `Chart Recognition:` |

---

## Kubernetes Deployment

### Volume Mounts

```yaml
volumeMounts:
  - name: models-volume
    mountPath: /root/.cache/docling/models
    subPath: models
  - name: models-volume
    mountPath: /root/.EasyOCR/model
    subPath: easy-ocr-models
  - name: models-volume
    mountPath: /root/.cache/rapidocr/models  # RapidOCR models
    subPath: rapidocr-models
```

### PersistentVolume Structure

```
models-volume/
├── models/                          # Docling models
│   ├── ds4sd--CodeFormulaV2/
│   ├── ds4sd--docling-layout-heron/
│   ├── ds4sd--docling-models/
│   └── ds4sd--DocumentFigureClassifier/
├── easy-ocr-models/                 # EasyOCR models (legacy)
│   ├── craft_mlt_25k.pth
│   ├── english_g2.pth
│   └── cyrillic_g2.pth
└── rapidocr-models/                 # RapidOCR/PP-OCR models
    ├── ch_PP-OCRv4_det_infer.onnx
    ├── ch_PP-OCRv4_rec_infer.onnx
    ├── ch_ppocr_mobile_v2.0_cls_infer.onnx
    └── ppocr_keys_v1.txt
```

### ConfigMap Example

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: docling-ocr-config
data:
  DOCLING_OCR_ENGINE: "rapidocr"
  DOCLING_OCR_LANGUAGES: "english,chinese,russian"
  DOCLING_RAPIDOCR_BACKEND: "onnxruntime"
  DOCLING_RAPIDOCR_MODELS_PATH: "/root/.cache/rapidocr/models"
  DOCLING_RAPIDOCR_TEXT_SCORE: "0.5"
```

---

## Air-Gapped / Offline Deployment

### Step 1: Prepare Models (Internet-Connected Machine)

```bash
# Download all models
python scripts/download_rapidocr_models.py -o ./rapidocr-models

# Verify
python scripts/download_rapidocr_models.py -o ./rapidocr-models --verify

# Package for transfer
tar -czvf rapidocr-models.tar.gz rapidocr-models/
```

### Step 2: Transfer to Closed Network

```bash
# Via secure copy, USB, etc.
scp rapidocr-models.tar.gz user@offline-server:/path/to/transfer/
```

### Step 3: Deploy on Offline Machine

```bash
# Extract models
tar -xzvf rapidocr-models.tar.gz -C /path/to/pv/rapidocr-models/

# Verify permissions
chmod -R 755 /path/to/pv/rapidocr-models/

# Configure environment
export DOCLING_OCR_ENGINE=rapidocr
export DOCLING_RAPIDOCR_MODELS_PATH=/path/to/pv/rapidocr-models
```

---

## Docker Deployment

### docker-compose.yml

The `docker/docker-compose.yml` already includes RapidOCR configuration:

```yaml
environment:
  - DOCLING_OCR_ENGINE=${DOCLING_OCR_ENGINE:-easyocr}
  - DOCLING_RAPIDOCR_BACKEND=${DOCLING_RAPIDOCR_BACKEND:-onnxruntime}
  - DOCLING_RAPIDOCR_MODELS_PATH=${DOCLING_RAPIDOCR_MODELS_PATH:-/root/.cache/rapidocr/models}
  - DOCLING_RAPIDOCR_TEXT_SCORE=${DOCLING_RAPIDOCR_TEXT_SCORE:-0.5}

volumes:
  - ../models/rapidocr:/root/.cache/rapidocr/models
```

### Running with RapidOCR

```bash
# Create .env file
cat > .env << EOF
DOCLING_OCR_ENGINE=rapidocr
DOCLING_RAPIDOCR_MODELS_PATH=/root/.cache/rapidocr/models
EOF

# Start service
cd docker
docker-compose up -d
```

---

## Comparison: EasyOCR vs RapidOCR

| Feature | EasyOCR | RapidOCR (PP-OCR) |
|---------|---------|-------------------|
| Model Size | ~100 MB | ~16 MB |
| Languages | 80+ | 109+ |
| GPU Support | CUDA | ONNX Runtime / Torch |
| Speed | Medium | Fast |
| Accuracy | Good | Excellent (PP-OCRv4) |
| Offline Support | Yes | Yes |
| Active Development | Moderate | Active (PaddleOCR 3.x) |

---

## Troubleshooting

### Models Not Found

```
Error: RapidOCR models path does not exist
```

**Solution**: Ensure models are downloaded and path is correct:
```bash
python scripts/download_rapidocr_models.py --verify
```

### GPU Not Detected

```
Warning: GPU not available, falling back to CPU
```

**Solution**: For GPU support with RapidOCR, use torch backend:
```bash
export DOCLING_RAPIDOCR_BACKEND=torch
```

### Permission Denied

```
Error: Permission denied accessing models
```

**Solution**: Check file permissions:
```bash
chmod -R 755 /path/to/models/rapidocr
```

---

## API Usage

### Check OCR Engine via Health Endpoint

```bash
curl http://localhost:8002/ocr/docling/health | jq '.ocr_engine'
# Returns: "rapidocr" or "easyocr"
```

### Force OCR Mode

```bash
# Always use OCR
curl -X POST "http://localhost:8002/ocr/docling/upload?ocr_mode=always" \
  -F "file=@document.pdf"

# Auto-detect if OCR needed
curl -X POST "http://localhost:8002/ocr/docling/upload?ocr_mode=auto" \
  -F "file=@document.pdf"
```

### Use VLM Pipeline with PaddleOCR-VL

```bash
curl -X POST "http://localhost:8002/ocr/docling/upload?pipeline=vlm" \
  -F "file=@document.pdf"
```

---

## References

- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR-VL on HuggingFace](https://huggingface.co/PaddlePaddle/PaddleOCR-VL)
- [RapidOCR Documentation](https://rapidai.github.io/RapidOCRDocs/)
- [Docling Documentation](https://docling-project.github.io/docling/)
