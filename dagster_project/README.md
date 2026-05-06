# Dagster Project

Stage 1 exposes a bronze asset that generates deterministic SaaS source tables as local Parquet files.

Run Dagster locally after installing pipeline dependencies:

```bash
make setup-pipeline PYTHON=/opt/homebrew/bin/python3.12
.venv/bin/dagster dev -m dagster_project.definitions
```

The Dagster UI should show the `bronze_saas_source_tables` asset in the `bronze` group.
