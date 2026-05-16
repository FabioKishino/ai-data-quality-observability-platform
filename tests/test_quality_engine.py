from pathlib import Path

import duckdb
import pytest

from observability_platform.quality_engine import (
    CheckSeverity,
    CheckStatus,
    CriticalQualityFailure,
    QualityCheck,
    run_quality_checks,
)
from observability_platform.settings import get_project_paths

REQUIRED_MODEL_TABLES = [
    "dim_customers",
    "dim_subscriptions",
    "fact_payments",
    "fact_product_usage",
    "mart_revenue_health",
]


def test_quality_engine_persists_successful_results(tmp_path: Path) -> None:
    paths = get_project_paths(tmp_path)
    _create_minimal_quality_tables(paths.warehouse_path)

    result = run_quality_checks(paths=paths)

    assert result.status == CheckStatus.PASSED
    assert len(result.results) == 11
    assert result.critical_failures == []

    with duckdb.connect(str(paths.warehouse_path)) as connection:
        run_count = connection.execute("select count(*) from quality_check_runs").fetchone()[0]
        result_count = connection.execute(
            "select count(*) from quality_check_results"
        ).fetchone()[0]
        health_rows = connection.execute(
            "select dataset_name, health_status from dataset_health_status order by dataset_name"
        ).fetchall()

    assert run_count == 1
    assert result_count == 11
    assert health_rows == [(table, "healthy") for table in REQUIRED_MODEL_TABLES]


def test_quality_engine_fails_on_critical_check(tmp_path: Path) -> None:
    paths = get_project_paths(tmp_path)
    _create_minimal_quality_tables(paths.warehouse_path)
    check = QualityCheck(
        check_name="forced_failure",
        dataset_name="dim_customers",
        severity=CheckSeverity.CRITICAL,
        description="Forced failure for tests.",
        metric_sql="select 1",
        failure_condition="observed_value > 0",
    )

    with pytest.raises(CriticalQualityFailure) as exc_info:
        run_quality_checks(paths=paths, checks=[check])

    assert exc_info.value.result.status == CheckStatus.FAILED
    assert exc_info.value.result.critical_failures[0].check_name == "forced_failure"

    with duckdb.connect(str(paths.warehouse_path)) as connection:
        health_status = connection.execute(
            "select health_status from dataset_health_status where dataset_name = 'dim_customers'"
        ).fetchone()[0]

    assert health_status == "critical"


def _create_minimal_quality_tables(warehouse_path: Path) -> None:
    warehouse_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(warehouse_path)) as connection:
        connection.execute(
            """
            create table dim_customers as
            select
                'cus_00001' as customer_id,
                'Company 00001' as company_name,
                'US' as country,
                'startup' as segment,
                date '2026-05-01' as signup_date,
                'organic' as acquisition_channel,
                'active' as account_status,
                1 as invoice_count,
                1 as payment_count,
                100.00 as total_amount_invoiced,
                100.00 as total_amount_paid,
                1 as product_event_rows,
                5 as product_event_count,
                timestamp '2026-05-02 00:00:00' as latest_product_event_at
            """
        )
        connection.execute(
            """
            create table dim_subscriptions as
            select
                'sub_00001' as subscription_id,
                'cus_00001' as customer_id,
                'startup' as segment,
                'US' as country,
                'starter' as plan_tier,
                'monthly' as billing_period,
                date '2026-05-01' as started_at,
                null::date as canceled_at,
                49.00 as mrr,
                'active' as subscription_status,
                1 as is_active,
                0 as is_churned,
                10 as subscription_age_days
            """
        )
        connection.execute(
            """
            create table fact_payments as
            select
                'pay_00001_01' as payment_id,
                'inv_00001_01' as invoice_id,
                'sub_00001' as subscription_id,
                'cus_00001' as customer_id,
                date '2026-05-03' as payment_date,
                date '2026-05-01' as invoice_date,
                date '2026-05-15' as due_date,
                49.00 as amount_paid,
                'card' as payment_method,
                'succeeded' as payment_status,
                2 as payment_delay_days
            """
        )
        connection.execute(
            """
            create table fact_product_usage as
            select
                'evt_00001_001' as event_id,
                'cus_00001' as customer_id,
                date '2026-05-02' as event_date,
                timestamp '2026-05-02 00:00:00' as event_timestamp,
                'login' as event_name,
                5 as event_count,
                'web' as source
            """
        )
        connection.execute(
            """
            create table mart_revenue_health as
            select
                'startup' as segment,
                'US' as country,
                1 as customer_count,
                1 as subscription_count,
                49.00 as total_mrr,
                1 as active_subscriptions,
                0 as churned_subscriptions,
                100.00 as total_amount_invoiced,
                100.00 as total_amount_paid,
                1 as payment_count,
                2.0 as avg_payment_delay_days
            """
        )
