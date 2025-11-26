#!/bin/bash

# Docling OCR: Restarting in GPU Mode (Linux)
set -e

echo "========================================"
echo "Docling OCR: Restarting in GPU Mode"
echo "========================================"

# 1. Сборка Base Image с поддержкой GPU (Тяжелая операция!)
echo ""
echo "[INFO] Building GPU Base Image (Large download ~2-3GB)..."
echo "This might take a while..."
docker build -t docling-ocr-base:latest --build-arg TORCH_DEVICE=gpu -f docker/Dockerfile.base .

# 2. Сборка App Image (Быстро)
echo ""
echo "[INFO] Building Application Image..."
docker build -t docling-ocr:latest -f docker/Dockerfile.app .

# 3. Запуск с конфигом GPU
echo ""
echo "[INFO] Starting with GPU support..."

# Останавливаем старые контейнеры
docker-compose --env-file .env -f docker/docker-compose.layered.yml down 2>/dev/null || true
docker-compose --env-file .env -f docker/docker-compose.gpu.yml down 2>/dev/null || true

# Запускаем новый, явно указывая файл .env
docker-compose --env-file .env -f docker/docker-compose.gpu.yml up -d

echo ""
echo "[SUCCESS] Docling is running on GPU!"
echo "Check logs to confirm: docker-compose -f docker/docker-compose.gpu.yml logs -f"
