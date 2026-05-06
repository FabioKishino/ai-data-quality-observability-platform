"""Bronze-layer writer for synthetic SaaS source data."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from observability_platform.settings import ProjectPaths, get_project_paths
from observability_platform.synthetic_saas import SyntheticSaaSConfig, generate_saas_tables


@dataclass(frozen=True)
class BronzePipelineResult:
    """Summary of a bronze pipeline run."""

    run_date: date
    mode: str
    output_root: Path
    table_paths: dict[str, Path]
    row_counts: dict[str, int]

    @property
    def total_rows(self) -> int:
        return sum(self.row_counts.values())


def run_bronze_pipeline(
    *,
    paths: ProjectPaths | None = None,
    run_date: date | None = None,
    seed: int = 42,
    customer_count: int = 120,
    days: int = 90,
    mode: str = "normal",
) -> BronzePipelineResult:
    """Generate deterministic source data and write it to bronze Parquet partitions."""

    if mode != "normal":
        msg = f"Unsupported bronze pipeline mode for Stage 1: {mode}"
        raise ValueError(msg)

    paths = paths or get_project_paths()
    effective_run_date = run_date or datetime.now(UTC).date()
    config = SyntheticSaaSConfig(
        seed=seed,
        customer_count=customer_count,
        days=days,
        run_date=effective_run_date,
    )
    tables = generate_saas_tables(config)

    output_root = paths.data_root / "bronze"
    table_paths: dict[str, Path] = {}
    row_counts: dict[str, int] = {}

    for table_name, dataframe in tables.items():
        table_dir = output_root / table_name / f"run_date={effective_run_date.isoformat()}"
        table_dir.mkdir(parents=True, exist_ok=True)
        table_path = table_dir / f"{table_name}.parquet"
        dataframe.to_parquet(table_path, index=False)
        table_paths[table_name] = table_path
        row_counts[table_name] = int(len(dataframe))

    metadata_dir = output_root / "_metadata"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_dir / "latest_run.json"
    metadata_path.write_text(
        json.dumps(
            {
                "run_date": effective_run_date.isoformat(),
                "mode": mode,
                "seed": seed,
                "customer_count": customer_count,
                "days": days,
                "generated_at": datetime.now(UTC).isoformat(),
                "row_counts": row_counts,
                "table_paths": {name: str(path) for name, path in table_paths.items()},
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    return BronzePipelineResult(
        run_date=effective_run_date,
        mode=mode,
        output_root=output_root,
        table_paths=table_paths,
        row_counts=row_counts,
    )
