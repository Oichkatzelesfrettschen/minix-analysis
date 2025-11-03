# Makefile for Visual Testing Playground
# 
# Provides convenience targets for building, testing, and maintaining the project
#

.PHONY: help install clean test lint format tags docker-build docker-test all

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m

##@ General

help: ## Display this help message
	@echo "$(CYAN)Visual Testing Playground - Make Targets$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage: make $(GREEN)<target>$(NC)\n"} \
		/^[a-zA-Z_-]+:.*?##/ { printf "  $(CYAN)%-15s$(NC) %s\n", $$1, $$2 } \
		/^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

all: install tags lint test ## Install, generate tags, lint, and test

##@ Setup

install: ## Install dependencies
	@echo "$(GREEN)Installing dependencies...$(NC)"
	npm install

clean: ## Clean build artifacts and caches
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf node_modules
	rm -rf gemini-report
	rm -rf .gemini-report
	rm -rf coverage
	rm -f tags tags.*
	@echo "$(GREEN)Clean complete$(NC)"

##@ Development

tags: ## Generate ctags file for code navigation
	@echo "$(GREEN)Generating tags...$(NC)"
	npm run tags

tags-incremental: ## Update tags incrementally (faster)
	@echo "$(GREEN)Updating tags incrementally...$(NC)"
	npm run tags:incremental

tags-verbose: ## Generate tags with verbose output
	@echo "$(GREEN)Generating tags (verbose)...$(NC)"
	npm run tags:verbose

##@ Code Quality

lint: ## Run ESLint
	@echo "$(GREEN)Running linter...$(NC)"
	npm run lint

lint-fix: ## Run ESLint with auto-fix
	@echo "$(GREEN)Running linter with auto-fix...$(NC)"
	npm run lint:fix

format: ## Format code with Prettier
	@echo "$(GREEN)Formatting code...$(NC)"
	npm run format

format-check: ## Check code formatting
	@echo "$(GREEN)Checking code format...$(NC)"
	npm run format:check

##@ Testing

test: ## Run visual regression tests
	@echo "$(GREEN)Running tests...$(NC)"
	npm test

test-update: ## Update reference screenshots
	@echo "$(YELLOW)Updating reference screenshots...$(NC)"
	npm run test:update

test-report: ## Generate HTML test report
	@echo "$(GREEN)Generating test report...$(NC)"
	npm run test:report

test-gui: ## Open Gemini GUI
	@echo "$(GREEN)Opening Gemini GUI...$(NC)"
	npm run test:gui

##@ Docker

docker-build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	npm run docker:build

docker-test: ## Run tests in Docker
	@echo "$(GREEN)Running tests in Docker...$(NC)"
	npm run docker:test

docker-update: ## Update screenshots in Docker
	@echo "$(YELLOW)Updating screenshots in Docker...$(NC)"
	npm run docker:update

##@ Git Hooks

install-hooks: ## Install git hooks for auto-tag updates
	@echo "$(GREEN)Installing git hooks...$(NC)"
	@if [ -f scripts/hooks/post-commit ]; then \
		cp scripts/hooks/post-commit .git/hooks/post-commit; \
		chmod +x .git/hooks/post-commit; \
		echo "$(GREEN)✓ Post-commit hook installed$(NC)"; \
	else \
		echo "$(YELLOW)! Hook file not found$(NC)"; \
	fi

##@ CI/CD Simulation

ci: lint test ## Simulate CI pipeline (lint + test)
	@echo "$(GREEN)CI pipeline complete$(NC)"

pre-commit: lint-fix format tags-incremental ## Run pre-commit checks
	@echo "$(GREEN)Pre-commit checks complete$(NC)"

##@ Information

info: ## Display project information
	@echo "$(CYAN)Project Information$(NC)"
	@echo "  Name: Visual Testing Playground"
	@echo "  Node: $$(node --version 2>/dev/null || echo 'Not installed')"
	@echo "  npm: $$(npm --version 2>/dev/null || echo 'Not installed')"
	@echo "  Ctags: $$(ctags --version 2>/dev/null | head -1 || echo 'Not installed')"
	@echo "  Docker: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@if [ -f tags ]; then \
		echo "  Tags: $$(wc -l < tags) entries"; \
	else \
		echo "  Tags: Not generated"; \
	fi

status: ## Show project status
	@echo "$(CYAN)Project Status$(NC)"
	@echo ""
	@echo "$(YELLOW)Dependencies:$(NC)"
	@if [ -d node_modules ]; then \
		echo "  ✓ Installed"; \
	else \
		echo "  ✗ Not installed (run: make install)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Tags:$(NC)"
	@if [ -f tags ]; then \
		echo "  ✓ Generated ($$(wc -l < tags) tags)"; \
	else \
		echo "  ✗ Not generated (run: make tags)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Git Hooks:$(NC)"
	@if [ -f .git/hooks/post-commit ]; then \
		echo "  ✓ Installed"; \
	else \
		echo "  ✗ Not installed (run: make install-hooks)"; \
	fi

##@ Documentation

docs: ## Display documentation links
	@echo "$(CYAN)Documentation$(NC)"
	@echo "  - README.md - Main documentation"
	@echo "  - docs/CTAGS.md - Ctags integration guide"
	@echo "  - docs/EDITOR_CTAGS.md - Editor setup"
	@echo "  - docs/CTAGS_QUICKREF.md - Quick reference"
	@echo "  - docs/ARCHITECTURE.md - Architecture overview"
	@echo "  - docs/GETTING_STARTED.md - Getting started guide"

##@ Advanced

rebuild: clean install tags ## Full rebuild (clean + install + tags)
	@echo "$(GREEN)Rebuild complete$(NC)"

dev-setup: install tags install-hooks ## Complete development setup
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo ""
	@echo "$(CYAN)Next steps:$(NC)"
	@echo "  1. Review docs/CTAGS.md for editor setup"
	@echo "  2. Run 'make test' to run tests"
	@echo "  3. Run 'make help' to see all targets"
