from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dbt_project_files_exist() -> None:
    expected_files = [
        "dbt/dbt_project.yml",
        "dbt/profiles.yml",
        "dbt/models/staging/stg_customers.sql",
        "dbt/models/intermediate/int_customer_revenue.sql",
        "dbt/models/marts/mart_revenue_health.sql",
        "dbt/models/schema.yml",
    ]

    missing = [path for path in expected_files if not (ROOT / path).is_file()]

    assert missing == []
