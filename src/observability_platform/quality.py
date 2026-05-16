"""Command-line entrypoint for data quality checks."""

from __future__ import annotations

import argparse

from observability_platform.quality_engine import (
    CriticalQualityFailure,
    quality_run_as_dict,
    run_quality_checks,
    write_quality_summary,
)
from observability_platform.settings import get_project_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run data quality checks against DuckDB models.")
    parser.add_argument(
        "--no-fail-on-critical",
        action="store_true",
        help="Persist results but return success even when critical checks fail.",
    )
    parser.add_argument(
        "--write-summary",
        action="store_true",
        help="Write the latest quality run summary to data/quality/latest_run.json.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    paths = get_project_paths()
    try:
        result = run_quality_checks(
            paths=paths,
            fail_on_critical=not args.no_fail_on_critical,
        )
    except CriticalQualityFailure as exc:
        result = exc.result
        _print_summary(result)
        if args.write_summary:
            write_quality_summary(result, paths.data_root / "quality" / "latest_run.json")
        raise SystemExit(1) from exc

    _print_summary(result)
    if args.write_summary:
        write_quality_summary(result, paths.data_root / "quality" / "latest_run.json")


def _print_summary(result) -> None:
    summary = quality_run_as_dict(result)
    print(
        "Quality checks completed: "
        f"status={summary['status']} total={summary['total_checks']} "
        f"failed={summary['failed_checks']} critical={summary['critical_failures']}"
    )
    for check in summary["results"]:
        print(
            "- "
            f"{check['dataset_name']}.{check['check_name']}: "
            f"{check['status']} ({check['severity']}, observed={check['observed_value']})"
        )


if __name__ == "__main__":
    main()
