# Makefile for AgentKnowledgeMCP
.PHONY: help dev test build clean deploy install

# Default target
help:
	@echo "Available commands:"
	@echo "  dev      - Start development server"
	@echo "  test     - Run all tests"
	@echo "  build    - Build package for distribution"
	@echo "  clean    - Clean build artifacts"
	@echo "  deploy   - Deploy to PyPI"
	@echo "  install  - Install in development mode"

# Development server
dev:
	@echo "🚀 Starting development server..."
	python src/server.py

# Run tests
test:
	@echo "🧪 Running tests..."
	python tests/test_validation.py
	python tests/test_strict_validation.py
	python tests/demo_config_management.py

# Build package
build:
	@echo "📦 Building package..."
	python -m build

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Deploy to PyPI
deploy: build
	@echo "🚀 Deploying to PyPI..."
	python -m twine upload dist/* --repository pypi

# Install in development mode
install:
	@echo "📥 Installing in development mode..."
	pip install -e .
