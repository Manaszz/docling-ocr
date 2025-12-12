# Легкий образ приложения (App Code Only)
# Этот образ собирается ЧАСТО (при любом изменении кода)
# Он наследуется от docling-ocr-base, поэтому сборка занимает секунды
#
# Build: docker build -t docling-ocr:latest -f Dockerfile.app .

# ВАЖНО: Здесь мы используем имя образа, который собрали через Dockerfile.base
# В продакшене это может быть: FROM my-registry.com/docling-base:v1
FROM docling-ocr-base:latest

WORKDIR /app

# Копируем только код приложения
# Так как слои с библиотеками уже есть в базовом образе, этот шаг очень быстрый
COPY app /app/app
COPY env.example /app/env.example
COPY scripts /app/scripts

# Настройка переменных окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# Отключаем GPU по умолчанию (для CPU версии). Переопределяется в docker-compose
ENV DOCLING_OCR_GPU=false

# УДАЛЕНО: DOCLING_ARTIFACTS_PATH
# Позволяем Docling использовать стандартный путь кэша (~/.cache/docling/models)
# Это решает проблему "Missing safe tensors file" при правильном монтировании

# Порт
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/ocr/docling/health || exit 1

# Делаем скрипт запуска исполняемым и исправляем окончания строк (Windows fix)
RUN sed -i 's/\r$//' /app/scripts/start.sh && \
    chmod +x /app/scripts/start.sh

# Запуск через скрипт (который создает симлинки для моделей)
CMD ["/app/scripts/start.sh"]
