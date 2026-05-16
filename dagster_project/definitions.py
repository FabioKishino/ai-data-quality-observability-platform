"""Dagster definitions for the local observability platform."""

from __future__ import annotations

from dagster import Definitions, MetadataValue, asset

from observability_platform.bronze_pipeline import run_bronze_pipeline
from observability_platform.quality_engine import quality_run_as_dict, run_quality_checks


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



@asset(group_name="quality", compute_kind="python")
def data_quality_check_results(context) -> dict[str, object]:
    """Run SQL-backed quality checks and persist quality observability tables."""

    result = run_quality_checks()
    summary = quality_run_as_dict(result)
    context.add_output_metadata(
        {
            "status": summary["status"],
            "total_checks": summary["total_checks"],
            "failed_checks": summary["failed_checks"],
            "critical_failures": summary["critical_failures"],
        }
    )
    return summary


defs = Definitions(assets=[bronze_saas_source_tables, data_quality_check_results])
