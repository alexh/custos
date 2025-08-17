.PHONY: install setup dev test clean help

help: ## Show available commands
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

install: ## Install dependencies with uv
	uv sync --group dev

setup: install ## Install dependencies and configure server
	@echo "🔑 Generating server configuration and tokens..."
	python setup_custos.py
	@echo "✅ Setup complete! Check output above for tokens."

dev: ## Run server locally (requires setup first)
	python custos_server.py

test: ## Start Docker, run tests, stop Docker
	@echo "🧪 Starting full test suite..."
	@echo "================================"
	@# Clean up any existing containers and volumes
	@docker-compose down -v 2>/dev/null || true
	@docker volume prune -f 2>/dev/null || true
	@echo "🚀 Starting Docker containers..."
	@docker-compose up -d
	@echo "⏳ Waiting for server to be ready..."
	@timeout=60; counter=0; \
	while [ $$counter -lt $$timeout ]; do \
		if curl -sf http://localhost:5555/health > /dev/null 2>&1; then \
			echo "✅ Server is ready!"; \
			break; \
		fi; \
		sleep 1; \
		counter=$$((counter + 1)); \
		if [ $$counter -eq $$timeout ]; then \
			echo "❌ Server failed to start within $$timeout seconds"; \
			docker-compose logs; \
			docker-compose down; \
			exit 1; \
		fi; \
	done
	@echo "🔑 Extracting tokens..."
	@TOKENS=$$(docker-compose exec -T custos cat /opt/custos/custos-tokens.txt 2>/dev/null || echo ""); \
	if [ -z "$$TOKENS" ]; then \
		echo "❌ Could not retrieve tokens from container"; \
		docker-compose logs; \
		docker-compose down; \
		exit 1; \
	fi; \
	PRIMARY_TOKEN=$$(echo "$$TOKENS" | grep "Primary Token" -A 1 | tail -1 | xargs); \
	EMERGENCY_TOKEN=$$(echo "$$TOKENS" | grep "Emergency Token" -A 1 | tail -1 | xargs); \
	if [ -z "$$PRIMARY_TOKEN" ] || [ -z "$$EMERGENCY_TOKEN" ]; then \
		echo "❌ Could not parse tokens"; \
		docker-compose down; \
		exit 1; \
	fi; \
	echo "🧪 Running tests..."; \
	CUSTOS_URL=http://localhost:5555 CUSTOS_PRIMARY_TOKEN=$$PRIMARY_TOKEN CUSTOS_EMERGENCY_TOKEN=$$EMERGENCY_TOKEN uv run python -m pytest tests/ -v; \
	TEST_RESULT=$$?; \
	echo "🧹 Cleaning up containers..."; \
	docker-compose down; \
	if [ $$TEST_RESULT -eq 0 ]; then \
		echo "✅ All tests passed!"; \
	else \
		echo "❌ Tests failed"; \
		exit 1; \
	fi

clean: ## Clean up containers and temp files
	docker-compose down -v || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true