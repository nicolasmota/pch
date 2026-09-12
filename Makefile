# Personal Context Hub
# Usage: make [target]
# Override: make serve PORT=9000 DATA_DIR=/tmp/pch

UV       ?= uv
NPM      ?= npm
PORT     ?= 8765
HOST     ?= 127.0.0.1
DATA_DIR ?= $(HOME)/.pch
FRONTEND ?= frontend

.DEFAULT_GOAL := help

.PHONY: help install sync frontend lint format test test-forbidden test-perf \
        test-all serve desktop openapi demo-agent bridge clean release smoke \
        check-secrets

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nTargets:\n"} \
		/^[a-zA-Z0-9_.-]+:.*##/ { printf "  %-18s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@printf "\nVariables: UV PORT HOST DATA_DIR\n\n"

install: sync frontend ## Install Python workspace and build the UI

sync: ## Install Python 3.14 workspace with uv
	$(UV) sync --all-packages

frontend: ## Install JS deps and build UI into pcl-server static/
	cd $(FRONTEND) && $(NPM) ci && $(NPM) run build

check-secrets: ## Fail if git-tracked paths match the secrets deny-list
	$(UV) run python scripts/check_secrets.py

lint: ## Lint Python with Ruff and frontend with ESLint
	$(UV) run ruff check packages apps
	cd $(FRONTEND) && $(NPM) run lint

format: ## Format Python with Ruff and frontend with Prettier
	$(UV) run ruff format packages apps
	cd $(FRONTEND) && $(NPM) run format

test: ## Run the default pytest suite
	$(UV) run pytest

test-forbidden: ## Run forbidden-context isolation tests (SC-003)
	$(UV) run pytest -m forbidden_context

test-perf: ## Run search/scale performance tests (SC-009)
	$(UV) run pytest -m perf

test-all: test test-forbidden ## Default suite plus forbidden-context

serve: ## Headless API with auto-reload (Python + UI watch)
	@trap 'kill 0' EXIT INT TERM; \
	(cd $(FRONTEND) && $(NPM) run build:watch) & \
	$(UV) run pcl-server --headless --reload --host $(HOST) --port $(PORT) --data-dir $(DATA_DIR)

desktop: ## Hub with auto-reload (Python + UI watch)
	@trap 'kill 0' EXIT INT TERM; \
	(cd $(FRONTEND) && $(NPM) run build:watch) & \
	$(UV) run hub-desktop --dev --reload --port $(PORT) --data-dir $(DATA_DIR)

openapi: ## Dump OpenAPI 3.1 JSON to specs/.../contracts/openapi.json
	$(UV) run python -c "from pathlib import Path; from pcl_core.service import Hub; from pcl_server.rest.app import create_app; import json, tempfile; \
hub = Hub(Path(tempfile.mkdtemp()), plain=True); \
Path('specs/001-personal-context-hub/contracts/openapi.json').write_text(json.dumps(create_app(hub).openapi(), indent=2))"

demo-agent: ## Pair the reference agent (CODE= from Hub pairing link)
	@test -n "$(CODE)" || (echo "usage: make demo-agent CODE=<pairing-code>"; exit 1)
	$(UV) run pcl-sdk demo-agent --pair $(CODE) --base http://$(HOST):$(PORT)

bridge: ## Run the MCP stdio bridge (TOKEN= from a connection recipe)
	@test -n "$(TOKEN)" || (echo "usage: make bridge TOKEN=<connection-token>"; exit 1)
	PCH_TOKEN=$(TOKEN) PCH_BASE=http://$(HOST):$(PORT) $(UV) run pcl-sdk mcp-bridge

release: frontend ## Build wheels, gate them, and publish
	$(UV) build --all-packages
	$(UV) run python scripts/check_release.py
	$(UV) publish

smoke: ## Headless packaged smoke (health, SPA, 001/004 HTTP)
	$(UV) run pch smoke

clean: ## Remove caches, build artifacts, and the local venv
	rm -rf .venv .pytest_cache .mypy_cache .ruff_cache
	rm -rf $(FRONTEND)/node_modules $(FRONTEND)/dist
	rm -rf packages/pcl-server/src/pcl_server/static/assets
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	find . -type d -name '*.egg-info' -prune -exec rm -rf {} +
