@echo off
echo ========================================
echo Docling OCR: Restarting in GPU Mode
echo ========================================

REM Переходим в корневую директорию проекта (на случай если скрипт запущен из другой папки)
cd /d "%~dp0"

REM 1. Проверяем наличие базового образа (НЕ пересобираем если он есть)
echo.
echo [INFO] Checking for base image...
docker image inspect docling-ocr-base:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Base image not found. Building GPU Base Image (Large download ~2-3GB)...
    echo This might take a while...
    docker build -t docling-ocr-base:latest --build-arg TORCH_DEVICE=gpu -f docker/Dockerfile.base .
    
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to build GPU base image.
        pause
        exit /b 1
    )
    echo [SUCCESS] Base image built successfully.
) else (
    echo [INFO] Base image found. Skipping base build (as requested).
)

REM 2. Сборка App Image (Быстро)
echo.
echo [INFO] Building Application Image...
docker build -t docling-ocr:latest -f docker/Dockerfile.app .

if %errorlevel% neq 0 (
    echo [ERROR] Failed to build app image.
    pause
    exit /b 1
)

REM 3. Запуск с конфигом GPU
echo.
echo [INFO] Starting with GPU support...
REM Останавливаем старые контейнеры
docker-compose --env-file .env -f docker/docker-compose.layered.yml down 2>nul
docker-compose --env-file .env -f docker/docker-compose.gpu.yml down 2>nul

REM Запускаем новый, явно указывая файл .env из корня
docker-compose --env-file .env -f docker/docker-compose.gpu.yml up -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start containers.
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Docling is running on GPU!
echo Check logs to confirm: docker-compose -f docker/docker-compose.gpu.yml logs -f
pause
