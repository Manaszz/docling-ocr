#!/bin/bash

# Docling OCR: Restarting in GPU Mode (Linux)
set -e

# Переходим в корневую директорию проекта
cd "$(dirname "$0")"

echo "========================================"
echo "Docling OCR: Restarting in GPU Mode"
echo "========================================"

# 1. Проверяем наличие базового образа (НЕ пересобираем если он есть)
echo ""
echo "[INFO] Checking for base image..."
if [[ "$(docker images -q docling-ocr-base:latest 2> /dev/null)" == "" ]]; then
    echo "[INFO] Base image not found. Building GPU Base Image (Large download ~2-3GB)..."
    echo "This might take a while..."
    docker build -t docling-ocr-base:latest --build-arg TORCH_DEVICE=gpu -f docker/Dockerfile.base .
    
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to build GPU base image."
        exit 1
    fi
    echo "[SUCCESS] Base image built successfully."
else
    echo "[INFO] Base image found. Skipping base build (as requested)."
fi

# 2. Сборка App Image (Быстро)
echo ""
echo "[INFO] Building Application Image..."
docker build -t docling-ocr:latest -f docker/Dockerfile.app .

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to build app image."
    exit 1
fi

# 3. Запуск с конфигом GPU
echo ""
echo "[INFO] Starting with GPU support..."

# Останавливаем старые контейнеры
docker-compose --env-file .env -f docker/docker-compose.layered.yml down 2>/dev/null || true
docker-compose --env-file .env -f docker/docker-compose.gpu.yml down 2>/dev/null || true

# Запускаем новый, явно указывая файл .env
docker-compose --env-file .env -f docker/docker-compose.gpu.yml up -d

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to start containers."
    exit 1
fi

echo ""
echo "[SUCCESS] Docling is running on GPU!"
echo "Check logs to confirm: docker-compose -f docker/docker-compose.gpu.yml logs -f"
