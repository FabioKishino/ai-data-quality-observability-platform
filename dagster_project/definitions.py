"""Dagster definitions for the local observability platform."""

from __future__ import annotations

from dagster import Definitions, MetadataValue, asset

from observability_platform.bronze_pipeline import run_bronze_pipeline


@asset(group_name="bronze", compute_kind="python")
def bronze_saas_source_tables(context) -> dict[str, int]:
    """Generate synthetic SaaS source tables in the bronze layer."""

    result = run_bronze_pipeline()
    context.add_output_metadata(
        {
            "run_date": result.run_date.isoformat(),
            "mode": result.mode,
            "total_rows": result.total_rows,
            "output_root": MetadataValue.path(str(result.output_root)),
        }
    )
    return result.row_counts


defs = Definitions(assets=[bronze_saas_source_tables])
