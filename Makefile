.PHONY: help install clean run stop restart logs test build deploy build-gpu build-gpu-base up-gpu down-gpu logs-gpu restart-gpu ps-gpu

# Variables
PYTHON=python3
PIP=pip
VENV=venv
PORT=8002

help: ## Show this help message
	@echo "Docling OCR - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and set up environment
	@echo "Installing Docling OCR..."
	$(PYTHON) -m venv $(VENV)
	./$(VENV)/bin/pip install --upgrade pip
	./$(VENV)/bin/pip install -r requirements.txt
	@mkdir -p temp models logs
	@if [ ! -f .env ]; then cp env.example .env; echo "Created .env file"; fi
	@echo "Installation complete!"

download-models: ## Download Docling models
	@echo "Downloading models..."
	./$(VENV)/bin/python scripts/download_models.py -o ./models

verify: ## Verify installation
	./$(VENV)/bin/python scripts/verify_installation.py

run: ## Run the service locally
	./$(VENV)/bin/uvicorn app.main:app --host 0.0.0.0 --port $(PORT)

run-dev: ## Run with hot reload (development)
	./$(VENV)/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port $(PORT)

# Docker commands
bump-version: ## Increment patch version
	@$(PYTHON) scripts/bump_version.py

build: bump-version ## Build lightweight image (uses host models)
	@echo "Building lightweight image (models from host)..."
	docker-compose build

build-standalone: bump-version ## Build standalone image (models embedded)
	@echo "Building standalone image (models embedded - takes ~10-15 min)..."
	docker-compose -f docker-compose.standalone.yml build

build-fast: ## Build without cache (force rebuild all)
	docker-compose build --no-cache

build-quick: ## Quick rebuild (uses cache)
	docker-compose build

build-gpu: ## Build app image for GPU (requires base image)
	@echo "Building application image for GPU..."
	docker build -t docling-ocr:latest -f docker/Dockerfile.app .

build-gpu-base: ## Build GPU base image (heavy operation, ~2-3GB download)
	@echo "Building GPU base image (this may take a while)..."
	docker build -t docling-ocr-base:latest --build-arg TORCH_DEVICE=gpu -f docker/Dockerfile.base .

up: ## Start Docker containers (lightweight mode)
	docker-compose up -d

up-standalone: ## Start standalone container
	docker-compose -f docker-compose.standalone.yml up -d

up-gpu: ## Start Docker containers with GPU support
	docker-compose --env-file .env -f docker/docker-compose.gpu.yml up -d

down: ## Stop Docker containers
	docker-compose down

down-standalone: ## Stop standalone container
	docker-compose -f docker-compose.standalone.yml down

down-gpu: ## Stop GPU containers
	docker-compose --env-file .env -f docker/docker-compose.gpu.yml down

logs: ## View Docker logs
	docker-compose logs -f

logs-gpu: ## View GPU container logs
	docker-compose -f docker/docker-compose.gpu.yml logs -f

restart: ## Restart Docker containers
	docker-compose restart

restart-gpu: down-gpu build-gpu up-gpu ## Rebuild and restart GPU containers
	@echo "GPU containers restarted successfully!"

ps: ## Show container status
	docker-compose ps

ps-gpu: ## Show GPU container status
	docker-compose -f docker/docker-compose.gpu.yml ps

# Testing
test: ## Run tests
	./$(VENV)/bin/pytest tests/ -v

test-cov: ## Run tests with coverage
	./$(VENV)/bin/pytest tests/ --cov=app --cov-report=html --cov-report=term

# Offline deployment
prepare-offline: ## Prepare offline deployment package
	@echo "Preparing offline package..."
	chmod +x scripts/prepare_offline.sh
	./scripts/prepare_offline.sh

# Cleanup
clean: ## Clean up temporary files
	@echo "Cleaning up..."
	rm -rf temp/* logs/* __pycache__ .pytest_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

clean-all: clean ## Clean everything including venv and models
	@echo "Deep cleaning..."
	rm -rf $(VENV) models/* offline-deploy
	@echo "Clean complete!"

clean-docker: ## Clean Docker cache and dangling images
	@echo "Cleaning Docker cache..."
	docker system prune -f
	docker builder prune -f

# Health check
health: ## Check service health
	@curl -s http://localhost:$(PORT)/ocr/docling/health | python -m json.tool || echo "Service not running"

# Version management
version: ## Show version information
	@echo "Docling OCR Version Information:"
	@grep "__version__" app/__init__.py
	@echo ""
	@./$(VENV)/bin/python -c "import docling; print(f'Docling: {docling.__version__}')" || echo "Docling not installed"

# Quick test
quick-test: ## Quick API test
	@echo "Testing upload endpoint..."
	@echo "Hello Docling" > /tmp/test_docling.txt
	@curl -X POST "http://localhost:$(PORT)/ocr/docling/upload" -F "file=@/tmp/test_docling.txt" | python -m json.tool
	@rm /tmp/test_docling.txt

.DEFAULT_GOAL := help
