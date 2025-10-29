# Troubleshooting Guide - Docling OCR

## Common Issues and Solutions

### 1. OCR Model Missing Error ✅ РЕШЕНО

**Ошибка**:
```
Missing D:\codding\ai\_RAG\markitdown\docling-ocr\models\EasyOcr\craft_mlt_25k.pth
and downloads disabled
```

**Причина**: EasyOCR пытается загрузить свои модели при инициализации, но автоматическая загрузка отключена.

#### Решение A: Отключить OCR (Для цифровых PDF) ✅ ПРИМЕНЕНО

Если вы работаете в основном с цифровыми PDF (не сканами), OCR не нужен:

```bash
# В файле .env установите:
DOCLING_OCR_ENABLED=false
```

**Перезапустите сервис**:
```bash
# Остановить
Stop-Process -Name python -Force

# Запустить
cd docling-ocr
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

**Проверка**:
```bash
curl http://localhost:8002/ocr/docling/health
# ocr_enabled должно быть false
```

#### Решение B: Установить модели EasyOCR (Для OCR)

Если вам нужен OCR для сканированных документов:

**Шаг 1: Загрузить модели EasyOCR вручную**

```bash
cd docling-ocr
.\venv\Scripts\python.exe -c "import easyocr; reader = easyocr.Reader(['en', 'ru'])"
```

Это загрузит модели в домашнюю директорию пользователя (`~/.EasyOCR/`).

**Шаг 2: Скопировать модели (опционально)**

```bash
# Создать директорию
mkdir models\EasyOcr

# Скопировать модели из ~/.EasyOCR/model/ в models\EasyOcr\
```

**Шаг 3: Включить OCR**

```bash
# В файле .env:
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr
DOCLING_OCR_LANGUAGES=en,ru
```

**Шаг 4: Перезапустить сервис**

#### Решение C: Использовать альтернативный OCR движок

Вместо EasyOCR можно использовать Tesseract (без дополнительных моделей):

**Установка Tesseract**:

**Windows**:
```bash
# Скачать и установить с https://github.com/UB-Mannheim/tesseract/wiki
# Или через chocolatey:
choco install tesseract
```

**Linux**:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-rus
```

**Конфигурация**:
```bash
# В .env:
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=tesseract
```

### 2. PDF Conversion Now Working ✅

После применения решения A, цифровые PDF конвертируются без проблем:

**Тест**:
```bash
# Проверить статус
curl http://localhost:8002/ocr/docling/health

# Должно показать:
# ocr_enabled: false
# status: healthy
```

### 3. When to Use OCR?

**OCR НЕ НУЖЕН для**:
- ✅ Цифровых PDF (созданных из Word, экспорта и т.д.)
- ✅ PDF с embedded text layers
- ✅ DOCX, XLSX, PPTX файлов
- ✅ HTML, MD файлов

**OCR НУЖЕН для**:
- ⚠️ Сканированных документов (photos of documents)
- ⚠️ PDF из сканера без text layer
- ⚠️ Изображений с текстом (JPG, PNG документов)

### 4. Service Not Starting

**Ошибка**: Port already in use

**Решение**:
```bash
# Найти процесс на порту 8002
Get-Process -Id (Get-NetTCPConnection -LocalPort 8002).OwningProcess

# Остановить
Stop-Process -Id <PID> -Force

# Или изменить порт в .env
PORT=8003
```

### 5. Models Not Loading

**Ошибка**: `models_loaded: false`

**Решение**:
```bash
# Проверить путь к моделям
ls models/

# Должны быть:
# - ds4sd--docling-layout-heron/
# - ds4sd--docling-models/
# - ds4sd--DocumentFigureClassifier/
# - ds4sd--CodeFormulaV2/

# Если моделей нет, загрузить:
.\venv\Scripts\python.exe scripts\download_models.py -o .\models
```

### 6. Import Errors

**Ошибка**: `ModuleNotFoundError: No module named 'docling'`

**Решение**:
```bash
# Активировать виртуальное окружение
.\venv\Scripts\activate

# Переустановить зависимости
pip install -r requirements.txt
```

### 7. Memory Issues

**Ошибка**: Out of memory

**Решение**:
```bash
# В .env установить fast mode для таблиц:
DOCLING_TABLE_MODE=fast

# Или отключить некоторые функции:
ENABLE_TABLE_EXTRACTION=false
ENABLE_METADATA_EXTRACTION=false
```

### 8. Slow Conversion

**Проблема**: Конвертация занимает много времени

**Решение**:
```bash
# 1. Использовать fast mode для таблиц
DOCLING_TABLE_MODE=fast

# 2. Отключить OCR если не нужен
DOCLING_OCR_ENABLED=false

# 3. Включить GPU (если доступен)
DOCLING_OCR_GPU=true
```

## Performance Tuning

### Для Production

```bash
# В .env:
WORKERS=8  # Увеличить количество workers
DOCLING_TABLE_MODE=fast  # Быстрый режим
DOCLING_OCR_ENABLED=false  # Отключить если не нужен
MAX_UPLOAD_SIZE=52428800  # Уменьшить лимит (50MB)
```

### Для Development

```bash
WORKERS=1  # Меньше workers для debugging
LOG_LEVEL=debug  # Больше логов
DOCLING_TABLE_MODE=accurate  # Качество важнее скорости
```

## Testing After Fix

После применения любого решения, протестируйте:

```bash
# 1. Проверить здоровье
curl http://localhost:8002/ocr/docling/health

# 2. Проверить форматы
curl http://localhost:8002/ocr/docling/formats

# 3. Тест с простым файлом
echo "# Test" > test.md
curl -X POST "http://localhost:8002/ocr/docling/upload" -F "file=@test.md"
```

## Current Status

✅ **OCR отключен** - Работает для цифровых PDF  
✅ **Сервис запущен** - http://localhost:8002  
✅ **Все остальные функции** - Работают нормально  

## Need More Help?

1. Проверьте логи: `docker logs docling-ocr` (для Docker)
2. Запустите verification: `python scripts/verify_installation.py`
3. Проверьте тесты: `pytest tests/ -v`

## Quick Fix Script

Создайте `fix_ocr.bat`:

```batch
@echo off
cd /d %~dp0
echo Fixing OCR configuration...

REM Отключить OCR
powershell -Command "(Get-Content .env) -replace 'DOCLING_OCR_ENABLED=true', 'DOCLING_OCR_ENABLED=false' | Set-Content .env"

REM Перезапустить сервис
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul
start "" .\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8002

echo.
echo Fixed! Service restarting...
echo Check: http://localhost:8002/ocr/docling/health
pause
```

Запустите: `fix_ocr.bat`

---

**Текущее решение применено**: OCR отключен, сервис работает для цифровых PDF ✅

