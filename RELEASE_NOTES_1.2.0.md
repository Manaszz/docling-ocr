# Release Notes - v1.2.0

**Release Date**: February 6, 2026

## Highlights
- RapidOCR integration using PaddleOCR PP-OCRv4 models (recommended OCR engine)
- PaddleOCR-VL guidance for VLM pipeline usage
- Health endpoint now reports active OCR engine
- New RapidOCR model download script for offline deployments

## What's New
### OCR
- Added RapidOCR configuration options (`DOCLING_RAPIDOCR_BACKEND`, `DOCLING_RAPIDOCR_MODELS_PATH`, `DOCLING_RAPIDOCR_TEXT_SCORE`)
- Updated Docker Compose to mount RapidOCR models by default
- Added `rapidocr-onnxruntime` to `requirements.txt`

### API
- Health response includes `ocr_engine`

### Docs & Tooling
- Added `PADDLEOCR_SETUP.md`
- Added `scripts/download_rapidocr_models.py`
- Updated README and OCR setup guide with RapidOCR/PaddleOCR details

## Upgrade Notes
1. If you want RapidOCR, download models with:
   ```bash
   python scripts/download_rapidocr_models.py -o ./models/rapidocr
   ```
2. Set OCR engine in `.env`:
   ```bash
   DOCLING_OCR_ENGINE=rapidocr
   DOCLING_RAPIDOCR_MODELS_PATH=./models/rapidocr
   ```
3. Restart the service after updating environment variables.
