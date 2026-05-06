# AI-Powered Data Quality & Observability Platform

A local-first data engineering portfolio project that simulates a modern data platform, runs data quality checks, records incidents, exposes observability metrics, and later uses local AI to explain failures with evidence.

## Current Stage

Stage 0: project foundation.

This stage establishes the repository structure, Python packaging, CI baseline, Git workflow, and documentation skeleton. It intentionally does not implement ingestion, dbt models, observability tables, or AI features yet.

## Target Architecture

- **Orchestration:** Dagster assets for pipeline execution and lineage.
- **Storage:** Parquet files plus DuckDB for local analytical storage.
- **Transformation:** dbt Core with DuckDB adapter.
- **Data Quality:** Great Expectations for validation suites and quality runs.
- **Dashboard:** Streamlit for local observability views.
- **AI:** Ollama and Chroma for local incident analysis in a later stage.
- **CI/CD:** GitHub Actions for linting and tests.

## Repository Layout

```text
.
├── .github/workflows/      # CI workflows
├── dagster_project/        # Dagster definitions and orchestration assets
├── data/                   # Local data lake folders, ignored except .gitkeep files
├── dbt/                    # dbt project files in later stages
├── docs/                   # Technical documentation
├── src/                    # Python package code
└── tests/                  # Automated tests
```

## Local Setup

```bash
# Use any Python version >= 3.11.
# On this macOS environment, Python 3.12 is available at /opt/homebrew/bin/python3.12.
make setup PYTHON=/opt/homebrew/bin/python3.12
source .venv/bin/activate
```

## Validation Commands

```bash
make lint
make test
```

Later stages will add optional dependency groups for pipeline, transformation, quality, dashboard, and AI features. The foundation stage installs only development tooling by default.

## Git Workflow

Use one branch per delivery stage:

```bash
git checkout -b feature/00-project-foundation
```

Each stage should be reviewed against its acceptance criteria before moving to the next one.

## Roadmap

1. Project foundation.
2. Synthetic SaaS data pipeline.
3. dbt transformation layer.
4. Data quality engine.
5. Incident simulation.
6. Observability dashboard.
7. AI incident analyst.
8. CI/CD hardening and portfolio documentation.
