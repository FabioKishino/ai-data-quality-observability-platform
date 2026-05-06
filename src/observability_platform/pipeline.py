"""Command-line entrypoint for local pipeline execution."""

from __future__ import annotations

import argparse
from datetime import date

from observability_platform.bronze_pipeline import run_bronze_pipeline
from observability_platform.settings import get_project_paths


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the local data observability platform pipeline."
    )
    parser.add_argument(
        "--mode",
        default="normal",
        choices=["normal"],
        help="Pipeline mode to run.",
    )
    parser.add_argument(
        "--run-date",
        type=_parse_date,
        default=None,
        help="Run date in YYYY-MM-DD format.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Deterministic generator seed.")
    parser.add_argument("--customers", type=int, default=120, help="Number of synthetic customers.")
    parser.add_argument("--days", type=int, default=90, help="Synthetic history window in days.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_bronze_pipeline(
        paths=get_project_paths(),
        run_date=args.run_date,
        seed=args.seed,
        customer_count=args.customers,
        days=args.days,
        mode=args.mode,
    )

    print(f"Bronze pipeline completed for run_date={result.run_date.isoformat()}")
    for table_name, row_count in sorted(result.row_counts.items()):
        print(f"- {table_name}: {row_count} rows -> {result.table_paths[table_name]}")


if __name__ == "__main__":
    main()
