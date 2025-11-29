.PHONY: install format lint test run

install:
	uv sync

format:
	uv run ruff check --fix
	uv run ruff format

lint:
	uv run ruff check .
	uv run mypy github_crawler

test:
	uv run pytest --cov=github_crawler --cov-report=term-missing --cov-fail-under=90
