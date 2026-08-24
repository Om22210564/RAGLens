.PHONY: format lint type-check test test-unit test-integration test-security migration-check

format:
	uv run ruff format app tests

lint:
	uv run ruff check app tests

type-check:
	uv run mypy app

test:
	uv run pytest

test-unit:
	uv run pytest -m unit

test-integration:
	uv run pytest -m integration

test-security:
	uv run pytest -m security

migration-check:
	uv run alembic check
