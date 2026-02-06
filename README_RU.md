# Docling OCR API

<div align="center">

![Docling Logo](https://docling-project.github.io/docling/assets/docling_processing.png)

**API для конвертации документов с помощью ИИ на базе Docling**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Docling](https://img.shields.io/badge/Docling-2.0+-orange.svg)](https://docling-project.github.io/docling/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## 🚀 Возможности

- **Поддержка двойного пайплайна (одновременно)**
  - **Стандартный пайплайн (`std`)**: Специализированные ИИ-модели для анализа структуры, извлечения таблиц и OCR
  - **VLM пайплайн (`vlm`)**: Vision-Language модели для полного понимания документа
  - **Не требуется переключение конфигурации** - выберите пайплайн на каждый запрос через параметр `?pipeline=`
  
- **Расширенные возможности OCR**
  - Поддержка EasyOCR (многоязычный, ускорение на GPU)
  - Интеграция Tesseract
  - RapidOCR с моделями PaddleOCR PP-OCRv4 (рекомендуется по точности)
  - Автоматическое определение сканированных и цифровых PDF (режимы auto/always/never)

- **Интеллектуальная обработка документов**
  - Анализ структуры с RT-DETR
  - Распознавание структуры таблиц с TableFormer
  - Классификация изображений
  - Обнаружение кода и формул
  
- **Совместимость с MiD-OCR API**
  - Прямая замена для MiD-OCR
  - Те же API endpoints и форматы ответов
  - Простой путь миграции

- **Функции для RAG**
  - Разбиение документов для векторных баз данных
  - Извлечение метаданных
  - Экспорт структурированных данных таблиц
  - Доступ к семантической структуре (DoclingDocument)
  - Множество форматов вывода (Markdown, HTML, JSON, DocTags)

- **Production функции**
  - Поддержка архивов (ZIP, RAR, 7Z)
  - Развертывание Docker (Layered, CPU/GPU, Offline)
  - Поддержка on-premise/air-gapped окружений
  - RESTful API с документацией OpenAPI
  - Современный веб-интерфейс
  - **Локализация интерфейса (русский/английский)**

## 📋 Поддерживаемые форматы

| Категория | Форматы |
|----------|---------|
| **Документы** | PDF, DOCX, DOC, TXT |
| **Таблицы** | XLSX, XLS |
| **Презентации** | PPTX, PPT |
| **Веб** | HTML, HTM, XML |
| **Изображения** | JPG, JPEG, PNG, GIF, BMP, TIFF |
| **Электронные книги** | EPUB |
| **Архивы** | ZIP, RAR, 7Z |

## 🔧 Быстрый старт

### Docker (Рекомендуется)

Используется **стратегия многослойной сборки** для более быстрой сборки и меньших образов.

```bash
# 1. Клонировать репозиторий
git clone <repository-url>
cd docling-ocr

# 2. Создать файл окружения
cp env.example .env

# 3. Собрать и запустить (Linux/Mac)
./build_layered.sh

# 3. Собрать и запустить (Windows)
build_layered.bat

# 4. Доступ к сервису
# Веб-интерфейс: http://localhost:8002
# API Документация: http://localhost:8002/docs
```

Для поддержки GPU или офлайн-развертывания см. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md).

### Локальная установка

```bash
# Linux/Mac
./install.sh

# Windows
install.bat
```

## ⚙️ Конфигурация

Отредактируйте файл `.env` для настройки:

```bash
# Локализация
DEFAULT_LANGUAGE=ru  # ru (русский) или en (английский)

# Конфигурация OCR (Стандартный пайплайн)
DOCLING_OCR_ENABLED=true
DOCLING_OCR_ENGINE=easyocr  # easyocr, tesseract, rapidocr
DOCLING_OCR_LANGUAGES=en,ru
DOCLING_OCR_GPU=false

# Конфигурация RapidOCR (если DOCLING_OCR_ENGINE=rapidocr)
# RapidOCR использует модели PaddleOCR PP-OCRv4 в формате ONNX
DOCLING_RAPIDOCR_BACKEND=onnxruntime  # onnxruntime (CPU) или torch (GPU)
DOCLING_RAPIDOCR_MODELS_PATH=/root/.cache/rapidocr/models
DOCLING_RAPIDOCR_TEXT_SCORE=0.5  # Порог уверенности (0.0-1.0)

# Конфигурация VLM (VLM пайплайн)
DOCLING_VLM_ENABLED=true  # Включить VLM пайплайн
DOCLING_VLM_API_URL=https://openrouter.ai/api/v1/chat/completions
DOCLING_VLM_API_KEY=your-openrouter-api-key-here
DOCLING_VLM_MODEL=qwen/qwen3-vl-235b-a22b-instruct
DOCLING_VLM_PROMPT=Convert this page to docling.

# Обработка таблиц
DOCLING_TABLE_MODE=accurate  # fast или accurate
```

**Примечание:** Оба пайплайна могут использоваться одновременно. Выберите пайплайн на каждый запрос используя `?pipeline=std` или `?pipeline=vlm`.

См. `env.example` для всех опций.

## 📖 API Документация

### Базовый URL

```
/ocr/docling
```

### 1. Проверка здоровья

```http
GET /ocr/docling/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "version": "1.2.0",
  "default_pipeline": "std",
  "default_language": "ru",
  "supported_languages": ["ru", "en"],
  "docling_version": "2.0.0",
  "pipelines": {
    "std": {"available": true, "loaded": true},
    "vlm": {"available": true, "loaded": false, "enabled": false, "model": null}
  },
  "ocr_enabled": true,
  "ocr_engine": "easyocr",
  "vlm_enabled": false,
  "models_loaded": true
}
```

### 2. Загрузка файла

```bash
# Конвертировать файл используя стандартный пайплайн (по умолчанию)
curl -X POST "http://localhost:8002/ocr/docling/upload" \
  -F "file=@document.pdf"

# Конвертировать файл используя VLM пайплайн
curl -X POST "http://localhost:8002/ocr/docling/upload?pipeline=vlm" \
  -F "file=@document.pdf"

# Стандартный пайплайн с определенным режимом OCR
curl -X POST "http://localhost:8002/ocr/docling/upload?pipeline=std&ocr_mode=always" \
  -F "file=@document.pdf"
```

Полная документация API доступна по адресу: http://localhost:8002/docs

## 🌐 Локализация

Интерфейс поддерживает русский и английский языки. Язык устанавливается через конфигурацию:

```bash
# В .env файле
DEFAULT_LANGUAGE=ru  # Русский (по умолчанию)
# или
DEFAULT_LANGUAGE=en  # Английский
```

Все элементы интерфейса автоматически переводятся в соответствии с выбранным языком.

## 📚 Документация

- [Руководство по установке](INSTALLATION.md)
- [Руководство по развертыванию](DOCKER_DEPLOYMENT.md)
- [On-Premise развертывание](ON_PREMISE_DEPLOYMENT.md)
- [PaddleOCR Setup](PADDLEOCR_SETUP.md) - RapidOCR и PaddleOCR-VL
- [Справочник API](http://localhost:8002/docs) (когда сервис запущен)

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 🙏 Благодарности

- [Docling](https://docling-project.github.io/docling/) - Основная обработка документов
- [FastAPI](https://fastapi.tiangolo.com/) - Веб-фреймворк
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) - OCR движок
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - PP-OCRv4 и PaddleOCR-VL модели
- [RapidOCR](https://github.com/RapidAI/RapidOCR) - OCR обертка для PaddleOCR
- [MiD-OCR](https://github.com/Manaszz/MiD-OCR) - Вдохновение для дизайна API

---

**Создано с ❤️ используя Docling**

