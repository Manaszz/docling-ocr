.PHONY: help install clean run stop restart logs test build deploy

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

build: bump-version ## Build Docker image (auto-increments version)
	docker-compose build

up: ## Start Docker containers
	docker-compose up -d

down: ## Stop Docker containers
	docker-compose down

logs: ## View Docker logs
	docker-compose logs -f

restart: ## Restart Docker containers
	docker-compose restart

ps: ## Show container status
	docker-compose ps

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
