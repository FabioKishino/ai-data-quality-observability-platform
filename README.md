# AI-Powered Data Quality & Observability Platform

A local-first data engineering portfolio project that simulates a modern data platform, runs data quality checks, records incidents, exposes observability metrics, and later uses local AI to explain failures with evidence.

## Current Stage

Stage 2: dbt transformation layer.

This stage adds dbt Core transformations on top of the synthetic SaaS bronze pipeline. Quality checks, observability tables, dashboard, and AI features remain planned for later stages.

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
make setup-transform PYTHON=/opt/homebrew/bin/python3.12
source .venv/bin/activate
```

## Validation Commands

```bash
make lint
make test
make run-pipeline
make dbt-build
```

The Stage 2 setup installs development, pipeline, and dbt transformation dependencies. Later stages will add quality, dashboard, and AI dependency groups as those capabilities are implemented.

## Git Workflow

Use one branch per delivery stage:

```bash
git checkout -b feature/00-project-foundation
```

Each stage should be reviewed against its acceptance criteria before moving to the next one.

## Roadmap

1. Project foundation.
2. Synthetic SaaS data pipeline.
3. dbt transformation layer. Current stage.
4. Data quality engine.
5. Incident simulation.
6. Observability dashboard.
7. AI incident analyst.
8. CI/CD hardening and portfolio documentation.


## Stage 1 Pipeline Output

The bronze pipeline generates deterministic B2B SaaS source data for customers, subscriptions, invoices, payments, and product events. Outputs are written as partitioned Parquet files under `data/bronze/` and are ignored by Git.

See `docs/stage-01-synthetic-data-pipeline.md` for implementation details and acceptance criteria.


## Stage 2 dbt Output

The dbt layer reads bronze SaaS Parquet files, creates typed staging views, reusable intermediate models, and analytics marts in DuckDB.

See `docs/stage-02-dbt-transformation-layer.md` for implementation details and acceptance criteria.
