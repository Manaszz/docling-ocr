# Release Notes v1.1.0

## 🎉 Новые возможности

### Internationalization (i18n) Support
- ✅ Добавлена поддержка многоязычного интерфейса (Русский и Английский)
- ✅ Переключение языка через URL параметр (`?lang=ru` или `?lang=en`) или селектор в UI
- ✅ Система переводов на основе JSON файлов с кэшированием
- ✅ Настройка языка по умолчанию через переменную окружения `DEFAULT_LANGUAGE`
- ✅ Обновлен health endpoint для возврата информации о поддерживаемых языках

### Advanced Chunking Modes
- ✅ Добавлены три режима chunking для RAG приложений:
  - **Mode 0 (Simple)**: Простой чанкинг по символам с фиксированным размером
  - **Mode 1 (Hierarchical)**: Семантический чанкинг на основе структуры документа
  - **Mode 2 (Hybrid)**: Гибридный чанкинг (иерархический + токенизация)
- ✅ Добавлены параметры для тонкой настройки:
  - `max_tokens` - максимальное количество токенов на чанк (для mode=2)
  - `merge_list_items` - объединение элементов списка в один чанк (для mode=1)
  - `merge_peers` - объединение одноуровневых чанков в одной секции (для mode=2)
- ✅ Улучшена обработка позиций (start_char, end_char) для всех режимов
- ✅ Поддержка HuggingFace tokenizer для hybrid режима

## 📝 Изменения

### Backend
- Добавлен модуль `app/utils/i18n.py` для управления переводами
- Обновлен `app/main.py` для поддержки параметра `lang` в URL
- Обновлен `app/api/v1/endpoints/health.py` для возврата информации о языках
- Обновлена схема `HealthResponse` с полями `default_language` и `supported_languages`
- Добавлена конфигурация `default_language` в `app/core/config.py`
- Улучшен `app/services/converter.py` с поддержкой трех режимов chunking
- Обновлен endpoint `/chunk` с новыми параметрами для режимов chunking
- Добавлены конфигурационные параметры для chunking в `app/core/config.py`:
  - `chunking_mode` (0=simple, 1=hierarchical, 2=hybrid)
  - `chunking_max_tokens` (для mode=2)
  - `chunking_merge_list_items` (для mode=1)
  - `chunking_merge_peers` (для mode=2)

### Frontend
- Добавлен селектор языка в заголовке UI
- Обновлены JavaScript и CSS для поддержки локализации
- Добавлены файлы переводов: `app/locales/ru.json` и `app/locales/en.json`
- Обновлен HTML шаблон для динамической загрузки переводов

### Документация
- Обновлен README.md с информацией о локализации
- Обновлены Memory Bank файлы (activeContext.md, progress.md)
- Добавлен README_RU.md (русская версия README)

## 🔧 Технические детали

### Файлы переводов
- `app/locales/ru.json` - Русские переводы
- `app/locales/en.json` - Английские переводы

### Конфигурация
```bash
# Localization
DEFAULT_LANGUAGE=ru  # ru (Russian) or en (English)

# Chunking Configuration
CHUNKING_MODE=0  # 0=simple, 1=hierarchical, 2=hybrid
CHUNKING_MAX_TOKENS=512  # For mode=2
CHUNKING_MERGE_LIST_ITEMS=true  # For mode=1
CHUNKING_MERGE_PEERS=true  # For mode=2
```

### API изменения
Health endpoint теперь возвращает:
```json
{
  "default_language": "ru",
  "supported_languages": ["ru", "en"],
  ...
}
```

Chunk endpoint теперь поддерживает три режима:
```bash
# Simple chunking (mode=0)
POST /ocr/docling/chunk?chunking_mode=0&chunk_size=1000&chunk_overlap=200

# Hierarchical chunking (mode=1)
POST /ocr/docling/chunk?chunking_mode=1&merge_list_items=true

# Hybrid chunking (mode=2)
POST /ocr/docling/chunk?chunking_mode=2&max_tokens=512&merge_peers=true
```

## 🐛 Исправления
- Исправлена обработка ошибок в системе переводов
- Улучшена валидация языковых параметров

## 📦 Обновления зависимостей
- Нет изменений в зависимостях

## 🚀 Миграция

Для обновления с v1.0.4 до v1.1.0:
1. Обновите код из репозитория
2. Убедитесь, что файлы переводов присутствуют в `app/locales/`
3. При необходимости настройте `DEFAULT_LANGUAGE` в `.env`
4. Пересоберите Docker образ (если используете Docker)

## 📚 Документация
- См. README.md для полной документации
- См. README_RU.md для русской версии

---

**Полный список изменений**: [GitHub Compare](https://github.com/Manaszz/docling-ocr/compare/v1.0.4...v1.1.0)
