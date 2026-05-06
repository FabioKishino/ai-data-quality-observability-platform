from datetime import date

import pandas as pd

from observability_platform.bronze_pipeline import run_bronze_pipeline
from observability_platform.settings import get_project_paths


def test_bronze_pipeline_writes_expected_parquet_files(tmp_path) -> None:
    paths = get_project_paths(tmp_path)

    result = run_bronze_pipeline(
        paths=paths,
        run_date=date(2026, 5, 6),
        seed=13,
        customer_count=12,
        days=35,
    )

    assert result.run_date == date(2026, 5, 6)
    assert set(result.table_paths) == {
        "customers",
        "subscriptions",
        "invoices",
        "payments",
        "product_events",
    }
    assert result.row_counts["customers"] == 12
    assert result.total_rows > 12

    for table_name, table_path in result.table_paths.items():
        assert table_path.exists(), table_name
        dataframe = pd.read_parquet(table_path)
        assert len(dataframe) == result.row_counts[table_name]

    assert (paths.data_root / "bronze" / "_metadata" / "latest_run.json").exists()


def test_bronze_pipeline_rejects_non_stage_one_modes(tmp_path) -> None:
    paths = get_project_paths(tmp_path)

    try:
        run_bronze_pipeline(paths=paths, mode="incident_demo")
    except ValueError as exc:
        assert "Unsupported bronze pipeline mode" in str(exc)
    else:
        raise AssertionError("incident_demo mode should not be implemented until Stage 4")
