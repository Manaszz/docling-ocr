@echo off
echo ========================================
echo Docling OCR Layered Build System
echo ========================================

REM 1. Проверяем, существует ли базовый образ
docker image inspect docling-ocr-base:latest >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Base image not found. Building base image...
    echo This may take a few minutes...
    
    REM Сборка базового образа из папки docker/
    docker build -t docling-ocr-base:latest -f docker/Dockerfile.base .
    
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to build base image.
        pause
        exit /b 1
    )
    echo [SUCCESS] Base image built successfully.
) else (
    echo [INFO] Base image found. Skipping base build.
)

REM 2. Сборка образа приложения (всегда)
echo.
echo [INFO] Building application image...
docker build -t docling-ocr:latest -f docker/Dockerfile.app .

if %errorlevel% neq 0 (
    echo [ERROR] Failed to build app image.
    pause
    exit /b 1
)

echo [SUCCESS] App image built successfully.

REM 3. Запуск
echo.
echo [INFO] Starting services...
docker-compose -f docker/docker-compose.layered.yml up -d

echo.
echo [DONE] Application is running on http://localhost:8002
pause

