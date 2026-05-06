from datetime import date

from observability_platform.synthetic_saas import SyntheticSaaSConfig, generate_saas_tables

EXPECTED_TABLES = {"customers", "subscriptions", "invoices", "payments", "product_events"}


def test_generate_saas_tables_is_deterministic() -> None:
    config = SyntheticSaaSConfig(seed=7, customer_count=10, days=30, run_date=date(2026, 5, 6))

    first = generate_saas_tables(config)
    second = generate_saas_tables(config)

    assert set(first) == EXPECTED_TABLES
    for table_name in EXPECTED_TABLES:
        assert first[table_name].equals(second[table_name])


def test_generate_saas_tables_preserves_relationships() -> None:
    tables = generate_saas_tables(
        SyntheticSaaSConfig(seed=11, customer_count=25, days=45, run_date=date(2026, 5, 6))
    )

    customer_ids = set(tables["customers"]["customer_id"])
    subscription_customer_ids = set(tables["subscriptions"]["customer_id"])
    invoice_customer_ids = set(tables["invoices"]["customer_id"])
    payment_customer_ids = set(tables["payments"]["customer_id"])
    event_customer_ids = set(tables["product_events"]["customer_id"])

    assert len(tables["customers"]) == 25
    assert subscription_customer_ids <= customer_ids
    assert invoice_customer_ids <= customer_ids
    assert payment_customer_ids <= customer_ids
    assert event_customer_ids <= customer_ids

    invoice_subscription_ids = set(tables["invoices"]["subscription_id"])
    subscription_ids = set(tables["subscriptions"]["subscription_id"])
    payment_invoice_ids = set(tables["payments"]["invoice_id"])
    invoice_ids = set(tables["invoices"]["invoice_id"])

    assert invoice_subscription_ids <= subscription_ids
    assert payment_invoice_ids <= invoice_ids
