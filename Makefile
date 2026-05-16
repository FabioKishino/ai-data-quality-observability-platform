.PHONY: setup setup-pipeline setup-transform setup-quality lint test run-pipeline dbt-build quality-check run-dashboard run-incident-demo

PYTHON ?= python3
VENV ?= .venv

setup:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && python -m pip install --upgrade pip
	. $(VENV)/bin/activate && pip install -e '.[dev]'

setup-pipeline:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && python -m pip install --upgrade pip
	. $(VENV)/bin/activate && pip install -e '.[dev,pipeline]'

setup-transform:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && python -m pip install --upgrade pip
	. $(VENV)/bin/activate && pip install -e '.[dev,pipeline,transform]'

setup-quality:
	$(PYTHON) -m venv $(VENV)
	. $(VENV)/bin/activate && python -m pip install --upgrade pip
	. $(VENV)/bin/activate && pip install -e '.[dev,pipeline,transform,quality]'

lint:
	$(VENV)/bin/ruff check src tests dagster_project

test:
	$(VENV)/bin/pytest

run-pipeline:
	$(VENV)/bin/python -m observability_platform.pipeline --mode normal

dbt-build:
	$(VENV)/bin/dbt build --project-dir dbt --profiles-dir dbt

quality-check:
	$(VENV)/bin/python -m observability_platform.quality --write-summary

run-dashboard:
	@echo "Dashboard implementation starts in Stage 5."

run-incident-demo:
	@echo "Incident simulation starts in Stage 4."
