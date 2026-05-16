# Delivery Checklist

Use this checklist at the end of each stage before moving forward.

## Stage 0: Project Foundation

- [ ] Repository structure exists.
- [ ] Python package config exists.
- [ ] README explains the project and roadmap.
- [ ] CI workflow exists.
- [ ] Basic tests exist.
- [ ] `make lint` passes.
- [ ] `make test` passes.
- [ ] Git status only includes intentional files.

## Stage 1: Synthetic SaaS Data Pipeline

- [ ] Generator is deterministic for a fixed seed and run date.
- [ ] Bronze Parquet files are created for all five source tables.
- [ ] Table relationships are stable and tested.
- [ ] Dagster definitions expose the bronze pipeline asset.
- [ ] `make setup-pipeline` works with Python >= 3.11.
- [ ] `make lint` passes.
- [ ] `make test` passes.
- [ ] `make run-pipeline` writes local output under `data/bronze/`.


## Stage 2: dbt Transformation Layer

- [ ] dbt project is configured for DuckDB.
- [ ] Staging models read all five bronze source tables.
- [ ] Intermediate models capture revenue and subscription lifecycle logic.
- [ ] Mart models support customer, subscription, payment, product usage, and revenue-health analysis.
- [ ] dbt tests validate uniqueness, non-null constraints, relationships, and accepted values.
- [ ] `make setup-transform` works with Python >= 3.11.
- [ ] `make run-pipeline` passes.
- [ ] `make dbt-build` passes.
- [ ] `make lint` and `make test` pass.


## Stage 3: Data Quality Engine

- [ ] Quality checks run against DuckDB models after `dbt-build`.
- [ ] `quality_check_runs` is persisted in the warehouse.
- [ ] `quality_check_results` is persisted in the warehouse.
- [ ] `dataset_health_status` summarizes model health.
- [ ] Critical check failures return a non-zero CLI exit code.
- [ ] `make setup-quality` works with Python >= 3.11.
- [ ] `make quality-check` passes after pipeline and dbt build.
- [ ] `make lint` and `make test` pass.
