.PHONY: install test lint typecheck check ci

install: ## Install dependencies
	@uv sync

test: ## Run tests with coverage
	@uv run pytest

lint: ## Run ruff lint
	@uv run ruff check .

typecheck: ## Run pyrefly typecheck
	@uv run pyrefly check

check: ## Run lint, typecheck, and tests (with coverage) via tox
	@uv run tox

ci: ## Commit on a branch, open a PR, merge it, then switch back to main and pull
	@echo "Staging everything"
	@git add .
	@echo "Running pre-commit"
	@uvx prek run --all-files
	@echo "Creating branch: $(BRANCH)"
	@git checkout -b "$(BRANCH)"
	@echo "Committing with message: $(MSG)"
	@git commit -m "$(MSG)"
	@echo "Pushing branch to origin"
	@git push -u origin "$(BRANCH)"
	@echo "Opening PR"
	@gh pr create --fill --head "$(BRANCH)"
	@echo "Merging PR"
	@gh pr merge "$(BRANCH)" --merge --delete-branch
	@echo "Switching back to main"
	@git checkout main
	@echo "Pulling latest"
	@git pull origin main
	@echo "Done"
