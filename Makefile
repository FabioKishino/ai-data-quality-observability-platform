.PHONY: setup lint test run-pipeline run-dashboard run-incident-demo

PYTHON ?= python3
VENV ?= .venv

setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && python -m pip install --upgrade pip
	. $(VENV)/bin/activate && pip install -e '.[dev]'

lint:
	$(VENV)/bin/ruff check src tests

test:
	$(VENV)/bin/pytest

run-pipeline:
	@echo "Pipeline implementation starts in Stage 1."

run-dashboard:
	@echo "Dashboard implementation starts in Stage 5."

run-incident-demo:
	@echo "Incident simulation starts in Stage 4."
