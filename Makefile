# Makefile for Aseprite MCP - Simplified

.PHONY: help build test lint format clean

# Variables
IMAGE_NAME := aseprite-mcp
VERSION := 0.3.0

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Core MCP operations
build: ## Build Docker image
	docker build -t $(IMAGE_NAME):$(VERSION) -t $(IMAGE_NAME):latest .

run: ## Run MCP server
	docker-compose up -d

stop: ## Stop MCP server
	docker-compose down

# Development
install: ## Install core dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest tests/

lint: ## Run linting
	ruff check aseprite_mcp/

format: ## Format code
	black aseprite_mcp/

clean: ## Clean up Docker resources
	docker-compose down
	docker system prune -f

local-mcp: ## Run local MCP mode
	python -m aseprite_mcp
