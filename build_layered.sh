#!/bin/bash

# Docling OCR Layered Build System (Linux)
set -e

echo "========================================"
echo "Docling OCR Layered Build System"
echo "========================================"

# 1. Проверяем, существует ли базовый образ
if [[ "$(docker images -q docling-ocr-base:latest 2> /dev/null)" == "" ]]; then
    echo "[INFO] Base image not found. Building base image..."
    echo "This may take a few minutes..."
    
    # Сборка базового образа
    docker build -t docling-ocr-base:latest -f docker/Dockerfile.base .
    
    echo "[SUCCESS] Base image built successfully."
else
    echo "[INFO] Base image found. Skipping base build."
fi

# 2. Сборка образа приложения (всегда)
echo ""
echo "[INFO] Building application image..."
docker build -t docling-ocr:latest -f docker/Dockerfile.app .

echo "[SUCCESS] App image built successfully."

# 3. Запуск
echo ""
echo "[INFO] Starting services..."
docker-compose -f docker/docker-compose.layered.yml up -d

echo ""
echo "[DONE] Application is running on http://localhost:8002"

