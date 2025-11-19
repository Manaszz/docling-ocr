# Multi-stage build for Docling OCR API

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt


# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages:$PYTHONPATH

# Copy application code
COPY app /app/app
COPY env.example /app/env.example
COPY scripts /app/scripts

# Create necessary directories
RUN mkdir -p /app/temp /app/models /app/logs

# Download Docling models during build
RUN python3 /app/scripts/download_models.py -o /app/models

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user (commented out for compatibility with /root/.local)
# RUN useradd -m -u 1000 docling && \
#     chown -R docling:docling /app
# USER docling

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/ocr/docling/health || exit 1

# Run application with environment variable support
CMD ["/bin/sh", "-c", "/root/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers ${WORKERS:-4}"]
