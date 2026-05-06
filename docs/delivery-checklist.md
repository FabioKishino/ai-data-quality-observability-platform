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
