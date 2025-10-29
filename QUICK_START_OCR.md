# ⚡ Быстрый Старт - OCR Toggle

## 🎯 Что Сделано

✅ **OCR включен** для полноценного функционала (сканы + цифровые документы)  
✅ **UI переключатель** добавлен (вкл/выкл OCR одним кликом)  
✅ **API endpoint** создан для программного управления  
✅ **Автозагрузка моделей** EasyOCR при первом использовании  

## 🚀 Как Использовать Прямо Сейчас

### 1. Откройте Web UI

```
http://localhost:8002
```

### 2. Найдите Переключатель OCR

В строке статуса (вверху страницы):
```
Mode: Standard | OCR: Enabled | Models: Loaded ✓
[🎚️ Enable OCR for Scans] ← ЭТОТ ПЕРЕКЛЮЧАТЕЛЬ
```

### 3. Используйте

**Для цифровых PDF** (быстрее):
- Выключите переключатель (станет серым)
- Загрузите PDF
- Конвертация 1-3 сек

**Для сканов** (распознавание текста):
- Включите переключатель (станет зеленым)
- Загрузите скан/фото
- Первый раз: подождите загрузку моделей (2-3 мин)
- Последующие: конвертация 5-15 сек

## 💻 Через API

### PowerShell

```powershell
# Включить OCR
Invoke-RestMethod -Uri "http://localhost:8002/ocr/docling/pipeline/ocr/toggle" `
  -Method Post -Body '{"enabled": true}' -ContentType "application/json"

# Отключить OCR
Invoke-RestMethod -Uri "http://localhost:8002/ocr/docling/pipeline/ocr/toggle" `
  -Method Post -Body '{"enabled": false}' -ContentType "application/json"

# Проверить статус
Invoke-RestMethod -Uri "http://localhost:8002/ocr/docling/pipeline"
```

### Bash/cURL

```bash
# Включить OCR
curl -X POST "http://localhost:8002/ocr/docling/pipeline/ocr/toggle" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Отключить OCR
curl -X POST "http://localhost:8002/ocr/docling/pipeline/ocr/toggle" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Проверить статус
curl "http://localhost:8002/ocr/docling/pipeline"
```

## 📊 Когда Включать/Выключать

| Тип документа | OCR | Время | Причина |
|---------------|-----|-------|---------|
| PDF из Word | ❌ OFF | 1-3 сек | Текст уже есть |
| DOCX, XLSX | ❌ OFF | 1-2 сек | Не требуется |
| Скан PDF | ✅ ON | 5-15 сек | Нужно распознать |
| Фото документа | ✅ ON | 3-8 сек | Нужно распознать |
| JPG с текстом | ✅ ON | 3-8 сек | Нужно распознать |

## 🎓 Важно Знать

### При Первом Использовании OCR

**Что произойдет**:
1. EasyOCR загрузит модели (~500MB)
2. Загрузка займет 2-3 минуты
3. Модели сохранятся в `~/.EasyOCR/`
4. Дальше будет быстро

**Где хранятся**:
- Windows: `C:\Users\user\.EasyOCR\model\`
- Linux: `~/.EasyOCR/model/`

### Перезапуск Сервиса

После переключения рекомендуется перезапустить для полного эффекта:

```powershell
# Остановить
Stop-Process -Name python -Force

# Запустить
cd docling-ocr
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## 📚 Дополнительно

### Полная Документация

- `OCR_SETUP.md` - Подробная настройка OCR
- `FINAL_STATUS.md` - Полный статус проекта
- `OCR_FEATURE_ADDED.md` - Описание функции
- `TROUBLESHOOTING.md` - Решение проблем

### Тестирование

```bash
# Проверить health
curl http://localhost:8002/ocr/docling/health

# Проверить pipeline
curl http://localhost:8002/ocr/docling/pipeline

# Live тесты
cd docling-ocr
python test_live_api.py
```

### Настройка OCR

В файле `.env`:
```bash
DOCLING_OCR_ENABLED=true          # Включить/выключить
DOCLING_OCR_ENGINE=easyocr        # easyocr, tesseract, rapidocr
DOCLING_OCR_LANGUAGES=en,ru       # Языки
DOCLING_OCR_GPU=false             # GPU acceleration
```

## 🆘 Помощь

### Проблемы с OCR?

См. `TROUBLESHOOTING.md` раздел "OCR Model Missing Error"

### Хотите другой OCR движок?

См. `OCR_SETUP.md` раздел "OCR Engines"

### Нужна помощь?

1. Проверьте логи сервиса
2. Запустите `python scripts/verify_installation.py`
3. См. документацию

---

## ✅ Итого

**Все работает и готово к использованию!**

- ✅ Сервис запущен: http://localhost:8002
- ✅ OCR включен по умолчанию
- ✅ Переключатель в UI работает
- ✅ API endpoint работает
- ✅ Модели загрузятся автоматически

**Просто откройте браузер и начните использовать!** 🚀

