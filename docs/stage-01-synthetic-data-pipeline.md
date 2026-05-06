# Stage 1: Synthetic SaaS Data Pipeline

## Goal

Create a deterministic source-data pipeline that simulates a B2B SaaS business and writes related source tables into the local bronze layer as Parquet files.

## Generated Tables

- `customers`
- `subscriptions`
- `invoices`
- `payments`
- `product_events`

## Run Locally

```bash
make setup-pipeline PYTHON=/opt/homebrew/bin/python3.12
make run-pipeline
```

For reproducible demos:

```bash
.venv/bin/python -m observability_platform.pipeline --run-date 2026-05-06 --seed 42 --customers 120 --days 90
```

## Outputs

The pipeline writes partitioned Parquet files under:

```text
data/bronze/<table_name>/run_date=<YYYY-MM-DD>/<table_name>.parquet
```

It also writes the latest run metadata to:

```text
data/bronze/_metadata/latest_run.json
```

Generated data is intentionally ignored by Git.

## Acceptance Criteria

- The generator is deterministic for the same seed and run date.
- The five source tables are generated with stable relationships.
- Bronze Parquet files are written locally.
- Dagster exposes the bronze source asset.
- Tests validate generation, relationships, and file output.
