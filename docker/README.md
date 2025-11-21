# Docker Deployment Guide

This directory contains Docker configurations for different deployment scenarios.

## 📁 Structure

| File | Purpose | Size | Build Speed |
|------|---------|------|-------------|
| `Dockerfile` | **Standard**. Single-stage build. | Medium | Medium |
| `Dockerfile.base` | **Base Layer**. Heavy dependencies (Torch, OCR). | Large (~3GB) | Slow |
| `Dockerfile.app` | **App Layer**. Light application code. Requires Base. | Tiny (<200MB) | **Fast** |
| `Dockerfile.offline` | **Air-Gapped**. Builds from local wheels. | Medium | Fast |
| `Dockerfile.standalone` | **All-in-One**. Includes models inside image. | Huge (~10GB) | Slow |

## 🚀 Scenarios

### 1. Standard Development (Recommended)
Uses `docker-compose.yml`.
- Good for simple local testing.
- Downloads models to host `./models` folder.
```bash
cd ..
docker-compose -f docker/docker-compose.yml up --build
```

### 2. Optimized / CI/CD (Layered)
Uses `Dockerfile.base` + `Dockerfile.app`.
- Best for frequent code changes.
- Rebuilds app in seconds.
```bash
# 1. Build Base (Once per month)
docker build -t docling-ocr-base:latest -f docker/Dockerfile.base .

# 2. Build App (Every commit)
docker build -t docling-ocr:latest -f docker/Dockerfile.app .

# 3. Run
docker-compose -f docker/docker-compose.layered.yml up -d
```

### 3. GPU Acceleration ⚡
Uses `Dockerfile.base` (GPU mode) + `docker-compose.gpu.yml`.
- Requires NVIDIA GPU & Container Toolkit.
```bash
# 1. Build GPU Base
docker build -t docling-ocr-base:latest --build-arg TORCH_DEVICE=gpu -f docker/Dockerfile.base .

# 2. Build App
docker build -t docling-ocr:latest -f docker/Dockerfile.app .

# 3. Run with GPU config
docker-compose -f docker/docker-compose.gpu.yml up -d
```

### 4. Offline / Air-Gapped 🔒
Uses `Dockerfile.offline`.
- No internet required for build.
- Requires pre-downloaded wheels in `offline_packages/`.
```bash
# 1. Download wheels (on internet-connected machine)
python scripts/download_offline_wheels.py

# 2. Build Offline Image
docker build -t docling-ocr:offline -f docker/Dockerfile.offline .
```

