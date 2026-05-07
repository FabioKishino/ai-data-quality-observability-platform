# Stage 2: dbt Transformation Layer

## Goal

Transform deterministic bronze SaaS source files into typed staging views, intermediate models, and analytics-ready marts using dbt Core with DuckDB.

## Model Layers

- `staging`: typed views over bronze Parquet files.
- `intermediate`: reusable revenue and subscription lifecycle models.
- `marts`: customer, subscription, payment, product usage, and revenue-health models.

## Run Locally

```bash
make setup-transform PYTHON=/opt/homebrew/bin/python3.12
make run-pipeline
make dbt-build
```

## Outputs

- DuckDB database: `data/warehouse/observability.duckdb`
- dbt artifacts: `dbt/target/`, ignored by Git
- Analytics marts in the DuckDB `main` schema

## Acceptance Criteria

- Bronze pipeline produces source Parquet files.
- dbt builds staging, intermediate, and mart models.
- dbt tests validate uniqueness, non-null constraints, accepted values, and relationships.
- CI runs the bronze pipeline before `dbt build`.
