"""SQL-backed data quality engine for local DuckDB models."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from uuid import uuid4

import duckdb

from observability_platform.settings import ProjectPaths, get_project_paths


class CheckSeverity(StrEnum):
    """Supported quality check severities."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class CheckStatus(StrEnum):
    """Normalized quality check status."""

    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True)
class QualityCheck:
    """A single SQL quality rule evaluated against DuckDB."""

    check_name: str
    dataset_name: str
    severity: CheckSeverity
    description: str
    metric_sql: str
    failure_condition: str


@dataclass(frozen=True)
class QualityCheckResult:
    """Result of a single quality rule evaluation."""

    check_name: str
    dataset_name: str
    severity: CheckSeverity
    status: CheckStatus
    observed_value: float
    description: str
    failure_condition: str


@dataclass(frozen=True)
class QualityRunResult:
    """Summary of a quality engine run."""

    run_id: str
    started_at: datetime
    completed_at: datetime
    status: CheckStatus
    results: list[QualityCheckResult]

    @property
    def failed_checks(self) -> list[QualityCheckResult]:
        return [result for result in self.results if result.status == CheckStatus.FAILED]

    @property
    def critical_failures(self) -> list[QualityCheckResult]:
        return [
            result
            for result in self.failed_checks
            if result.severity == CheckSeverity.CRITICAL
        ]


class CriticalQualityFailure(RuntimeError):
    """Raised when critical quality checks fail."""

    def __init__(self, result: QualityRunResult) -> None:
        failed_names = ", ".join(check.check_name for check in result.critical_failures)
        super().__init__(f"Critical data quality checks failed: {failed_names}")
        self.result = result


def build_default_quality_checks() -> list[QualityCheck]:
    """Return the Stage 3 quality rule set."""

    return [
        QualityCheck(
            check_name="dim_customers_has_rows",
            dataset_name="dim_customers",
            severity=CheckSeverity.CRITICAL,
            description="Customer dimension must not be empty.",
            metric_sql="select count(*) from dim_customers",
            failure_condition="observed_value <= 0",
        ),
        QualityCheck(
            check_name="dim_customers_unique_customer_id",
            dataset_name="dim_customers",
            severity=CheckSeverity.CRITICAL,
            description="Customer IDs must be unique in the customer dimension.",
            metric_sql="""
                select count(*)
                from (
                    select customer_id
                    from dim_customers
                    group by customer_id
                    having count(*) > 1
                )
            """,
            failure_condition="observed_value > 0",
        ),
        QualityCheck(
            check_name="dim_customers_customer_id_complete",
            dataset_name="dim_customers",
            severity=CheckSeverity.CRITICAL,
            description="Customer IDs must be complete in the customer dimension.",
            metric_sql="select count(*) from dim_customers where customer_id is null",
            failure_condition="observed_value > 0",
        ),
        QualityCheck(
            check_name="dim_subscriptions_mrr_non_negative",
            dataset_name="dim_subscriptions",
            severity=CheckSeverity.CRITICAL,
            description="Subscription MRR must never be negative.",
            metric_sql="select count(*) from dim_subscriptions where mrr < 0",
            failure_condition="observed_value > 0",
        ),
        QualityCheck(
            check_name="dim_subscriptions_valid_status",
            dataset_name="dim_subscriptions",
            severity=CheckSeverity.CRITICAL,
            description="Subscription status must stay within known values.",
            metric_sql="""
                select count(*)
                from dim_subscriptions
                where subscription_status not in ('active', 'canceled')
            """,
            failure_condition="observed_value > 0",
        ),
        QualityCheck(
            check_name="fact_payments_amount_non_negative",
            dataset_name="fact_payments",
            severity=CheckSeverity.CRITICAL,
            description="Payment amounts must never be negative.",
            metric_sql="select count(*) from fact_payments where amount_paid < 0",
            failure_condition="observed_value > 0",
        ),
        QualityCheck(
            check_name="fact_payments_customer_relationship",
            dataset_name="fact_payments",
            severity=CheckSeverity.CRITICAL,
            description="Payments must reference known customers.",
            metric_sql="""
                select count(*)
                from fact_payments
                left join dim_customers using (customer_id)
                where dim_customers.customer_id is null
            """,
            failure_condition="observed_value > 0",
        ),
        QualityCheck(
            check_name="fact_product_usage_has_rows",
            dataset_name="fact_product_usage",
            severity=CheckSeverity.WARNING,
            description="Product usage events should be present for observability demos.",
            metric_sql="select count(*) from fact_product_usage",
            failure_condition="observed_value <= 0",
        ),
        QualityCheck(
            check_name="fact_product_usage_event_count_positive",
            dataset_name="fact_product_usage",
            severity=CheckSeverity.WARNING,
            description="Product usage event counts should be positive.",
            metric_sql="select count(*) from fact_product_usage where event_count is null or event_count <= 0",
            failure_condition="observed_value > 0",
        ),
        QualityCheck(
            check_name="mart_revenue_health_has_rows",
            dataset_name="mart_revenue_health",
            severity=CheckSeverity.CRITICAL,
            description="Revenue health mart must not be empty.",
            metric_sql="select count(*) from mart_revenue_health",
            failure_condition="observed_value <= 0",
        ),
        QualityCheck(
            check_name="mart_revenue_health_non_negative_revenue",
            dataset_name="mart_revenue_health",
            severity=CheckSeverity.CRITICAL,
            description="Revenue health totals must never be negative.",
            metric_sql="""
                select count(*)
                from mart_revenue_health
                where total_amount_invoiced < 0 or total_amount_paid < 0 or total_mrr < 0
            """,
            failure_condition="observed_value > 0",
        ),
    ]


def run_quality_checks(
    *,
    paths: ProjectPaths | None = None,
    checks: list[QualityCheck] | None = None,
    fail_on_critical: bool = True,
) -> QualityRunResult:
    """Run quality checks, persist observability tables, and return the run summary."""

    paths = paths or get_project_paths()
    checks = checks or build_default_quality_checks()
    started_at = datetime.now(UTC)
    run_id = str(uuid4())

    paths.warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(paths.warehouse_path)) as connection:
        _ensure_quality_tables(connection)
        results = [_evaluate_check(connection, check) for check in checks]
        completed_at = datetime.now(UTC)
        run_status = (
            CheckStatus.FAILED
            if any(result.status == CheckStatus.FAILED for result in results)
            else CheckStatus.PASSED
        )
        run_result = QualityRunResult(
            run_id=run_id,
            started_at=started_at,
            completed_at=completed_at,
            status=run_status,
            results=results,
        )
        _persist_run(connection, run_result)
        _refresh_dataset_health(connection, run_result)

    if fail_on_critical and run_result.critical_failures:
        raise CriticalQualityFailure(run_result)

    return run_result


def _ensure_quality_tables(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        create table if not exists quality_check_runs (
            run_id varchar primary key,
            started_at timestamp,
            completed_at timestamp,
            status varchar,
            total_checks integer,
            failed_checks integer,
            critical_failures integer
        )
        """
    )
    connection.execute(
        """
        create table if not exists quality_check_results (
            run_id varchar,
            check_name varchar,
            dataset_name varchar,
            severity varchar,
            status varchar,
            observed_value double,
            description varchar,
            failure_condition varchar,
            checked_at timestamp
        )
        """
    )
    connection.execute(
        """
        create table if not exists dataset_health_status (
            dataset_name varchar primary key,
            latest_run_id varchar,
            health_status varchar,
            failed_checks integer,
            critical_failures integer,
            warning_failures integer,
            updated_at timestamp
        )
        """
    )


def _evaluate_check(
    connection: duckdb.DuckDBPyConnection,
    check: QualityCheck,
) -> QualityCheckResult:
    observed_value = float(connection.execute(check.metric_sql).fetchone()[0] or 0)
    failed = _condition_failed(observed_value, check.failure_condition)
    return QualityCheckResult(
        check_name=check.check_name,
        dataset_name=check.dataset_name,
        severity=check.severity,
        status=CheckStatus.FAILED if failed else CheckStatus.PASSED,
        observed_value=observed_value,
        description=check.description,
        failure_condition=check.failure_condition,
    )


def _condition_failed(observed_value: float, failure_condition: str) -> bool:
    if failure_condition == "observed_value <= 0":
        return observed_value <= 0
    if failure_condition == "observed_value > 0":
        return observed_value > 0
    msg = f"Unsupported failure condition: {failure_condition}"
    raise ValueError(msg)


def _persist_run(connection: duckdb.DuckDBPyConnection, result: QualityRunResult) -> None:
    connection.execute(
        """
        insert into quality_check_runs values (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            result.run_id,
            result.started_at,
            result.completed_at,
            result.status.value,
            len(result.results),
            len(result.failed_checks),
            len(result.critical_failures),
        ],
    )
    rows = [
        (
            result.run_id,
            check.check_name,
            check.dataset_name,
            check.severity.value,
            check.status.value,
            check.observed_value,
            check.description,
            check.failure_condition,
            result.completed_at,
        )
        for check in result.results
    ]
    connection.executemany(
        """
        insert into quality_check_results values (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )


def _refresh_dataset_health(
    connection: duckdb.DuckDBPyConnection, result: QualityRunResult) -> None:
    datasets = sorted({check.dataset_name for check in result.results})
    for dataset_name in datasets:
        dataset_results = [check for check in result.results if check.dataset_name == dataset_name]
        failed_checks = [check for check in dataset_results if check.status == CheckStatus.FAILED]
        critical_failures = [
            check for check in failed_checks if check.severity == CheckSeverity.CRITICAL
        ]
        warning_failures = [
            check for check in failed_checks if check.severity == CheckSeverity.WARNING
        ]
        health_status = (
            "critical" if critical_failures else "warning" if warning_failures else "healthy"
        )
        connection.execute(
            """
            insert or replace into dataset_health_status values (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                dataset_name,
                result.run_id,
                health_status,
                len(failed_checks),
                len(critical_failures),
                len(warning_failures),
                result.completed_at,
            ],
        )


def quality_run_as_dict(result: QualityRunResult) -> dict[str, object]:
    """Serialize a quality run summary for logs and Dagster metadata."""

    return {
        "run_id": result.run_id,
        "status": result.status.value,
        "started_at": result.started_at.isoformat(),
        "completed_at": result.completed_at.isoformat(),
        "total_checks": len(result.results),
        "failed_checks": len(result.failed_checks),
        "critical_failures": len(result.critical_failures),
        "results": [
            {
                "check_name": check.check_name,
                "dataset_name": check.dataset_name,
                "severity": check.severity.value,
                "status": check.status.value,
                "observed_value": check.observed_value,
            }
            for check in result.results
        ],
    }


def write_quality_summary(result: QualityRunResult, output_path: Path) -> None:
    """Write a JSON summary for CLI and demo use."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(quality_run_as_dict(result), indent=2, sort_keys=True),
        encoding="utf-8",
    )
