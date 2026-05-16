# Stage 3: Data Quality Engine

## Goal

Run dataset-level quality checks against the DuckDB models produced by dbt and persist each check run for later observability dashboards.

## Quality Tables

The engine writes these tables into `data/warehouse/observability.duckdb`:

- `quality_check_runs`
- `quality_check_results`
- `dataset_health_status`

## Check Coverage

The Stage 3 rule set validates:

- row availability for critical models
- customer ID uniqueness and completeness
- subscription status validity
- non-negative MRR, payment, and revenue values
- payment-to-customer relationships
- product usage availability and positive event counts

## Run Locally

```bash
make setup-quality PYTHON=/opt/homebrew/bin/python3.12
make run-pipeline
make dbt-build
make quality-check
```

For demo logs with a JSON summary:

```bash
.venv/bin/python -m observability_platform.quality --write-summary
```

## Acceptance Criteria

- Quality checks run against dbt-built DuckDB models.
- Results are persisted in the warehouse.
- Dataset health is summarized as `healthy`, `warning`, or `critical`.
- The CLI exits non-zero when critical checks fail.
- CI runs pipeline, dbt build, and quality checks in sequence.


## Implementation Note

This stage uses a lightweight SQL-backed quality engine instead of introducing a framework wrapper. That keeps the project local-first, transparent, and easy to inspect. A Great Expectations integration can still be added later if framework-specific validation becomes useful.
