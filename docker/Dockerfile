# Lightweight Dockerfile (Optimized for Size & Air-Gapped)
# Build: docker-compose build
# Or: docker build -t docling-ocr:latest .

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Build arguments for custom PyPI index (Air-gapped support)
ARG PIP_INDEX_URL
ARG PIP_TRUSTED_HOST
ARG PIP_EXTRA_INDEX_URL

# Install build dependencies
# git: for git dependencies
# build-essential: for compiling C extensions
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# CRITICAL OPTIMIZATION: Install PyTorch (CPU or GPU based on ARG)
# Default to CPU-only for size. Override for GPU support.
ARG TORCH_DEVICE=cpu
RUN if [ "$TORCH_DEVICE" = "cpu" ]; then \
        pip install --no-cache-dir torch torchvision torchaudio --index-url ${PIP_INDEX_URL:-https://download.pytorch.org/whl/cpu}; \
    else \
        # For GPU, use standard PyPI or provided index
        pip install --no-cache-dir torch torchvision torchaudio; \
    fi

# Install remaining dependencies
# --user installs to /root/.local which we can easily copy
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime (Slim)
FROM python:3.11-slim

WORKDIR /app

# Install strictly necessary runtime libraries
# libgl1/libglib2.0-0: Required for OpenCV
# poppler-utils: Required for PDF processing
# curl: For healthchecks
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    poppler-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Configure path to use installed packages
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages:$PYTHONPATH

# Copy application code
COPY app /app/app
COPY env.example /app/env.example
COPY scripts /app/scripts

# Create working directories
RUN mkdir -p /app/temp /app/models /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default to CPU mode. Override in docker-compose for GPU.
ENV DOCLING_OCR_GPU=false

# Expose port
EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8002/ocr/docling/health || exit 1

# Run application
CMD ["/bin/sh", "-c", "/root/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8002 --workers ${WORKERS:-4}"]
