.PHONY: install test test-cov typecheck lint lint-all clean build all precommit

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ --cov=src/hermes_demand_orchestrator --cov-report=term-missing --cov-report=html

typecheck:
	python -m mypy src/hermes_demand_orchestrator/

lint:
	python -m flake8 src/hermes_demand_orchestrator/ tests/ --max-line-length=100 --count

lint-ruff:
	python -m ruff check src/ tests/

lint-ruff-fix:
	python -m ruff check --fix src/ tests/

lint-all: lint lint-ruff typecheck
	@echo "All linters passed."

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache __pycache__ */__pycache__/ .coverage htmlcov/ .mypy_cache/ .ruff_cache/ .pre-commit/

build:
	python -m build

precommit:
	pre-commit run --all-files

all: install lint-all test-cov build
	@echo "All checks passed."
