"""Deterministic synthetic SaaS data generation for the bronze pipeline."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pandas as pd


@dataclass(frozen=True)
class SyntheticSaaSConfig:
    """Controls the shape of the deterministic SaaS dataset."""

    seed: int = 42
    customer_count: int = 120
    days: int = 90
    run_date: date | None = None


def _run_date(config: SyntheticSaaSConfig) -> date:
    return config.run_date or datetime.now(UTC).date()


def _choice(rng: random.Random, values: list[str]) -> str:
    return values[rng.randrange(0, len(values))]


def _frame(rows: list[dict[str, object]], sort_column: str) -> pd.DataFrame:
    return pd.DataFrame(rows).sort_values(sort_column).reset_index(drop=True)


def generate_saas_tables(config: SyntheticSaaSConfig | None = None) -> dict[str, pd.DataFrame]:
    """Generate related SaaS source tables with stable IDs and timestamps."""

    config = config or SyntheticSaaSConfig()
    rng = random.Random(config.seed)
    run_date = _run_date(config)
    start_date = run_date - timedelta(days=config.days)

    countries = ["US", "GB", "CA", "DE", "FR", "BR", "AU", "NL"]
    segments = ["startup", "mid_market", "enterprise"]
    channels = ["organic", "paid_search", "partner", "outbound", "marketplace"]
    statuses = ["active", "active", "active", "trial", "churned"]
    plans = [
        ("starter", Decimal("49.00")),
        ("growth", Decimal("149.00")),
        ("business", Decimal("399.00")),
        ("enterprise", Decimal("999.00")),
    ]

    customers: list[dict[str, object]] = []
    subscriptions: list[dict[str, object]] = []
    invoices: list[dict[str, object]] = []
    payments: list[dict[str, object]] = []
    product_events: list[dict[str, object]] = []

    for customer_index in range(1, config.customer_count + 1):
        customer_id = f"cus_{customer_index:05d}"
        signup_date = start_date + timedelta(days=rng.randrange(0, config.days))
        account_status = _choice(rng, statuses)
        segment = _choice(rng, segments)
        country = _choice(rng, countries)

        customers.append(
            {
                "customer_id": customer_id,
                "company_name": f"Company {customer_index:05d}",
                "country": country,
                "segment": segment,
                "signup_date": signup_date.isoformat(),
                "acquisition_channel": _choice(rng, channels),
                "account_status": account_status,
            }
        )

        plan_name, base_mrr = _choice(rng, plans)
        started_at = signup_date + timedelta(days=rng.randrange(0, 10))
        churned = account_status == "churned"
        canceled_at = (
            started_at + timedelta(days=rng.randrange(20, config.days)) if churned else None
        )
        subscription_id = f"sub_{customer_index:05d}"
        billing_period = _choice(rng, ["monthly", "monthly", "annual"])
        random_multiplier = Decimal(str(rng.random() * 0.45)).quantize(Decimal("0.01"))
        mrr_multiplier = Decimal("0.85") + random_multiplier
        mrr = (base_mrr * mrr_multiplier).quantize(Decimal("0.01"))

        subscriptions.append(
            {
                "subscription_id": subscription_id,
                "customer_id": customer_id,
                "plan_tier": plan_name,
                "billing_period": billing_period,
                "started_at": started_at.isoformat(),
                "canceled_at": canceled_at.isoformat() if canceled_at else None,
                "mrr": float(mrr),
                "subscription_status": "canceled" if churned else "active",
            }
        )

        invoice_count = max(1, min(4, (run_date - started_at).days // 30 + 1))
        for invoice_number in range(1, invoice_count + 1):
            invoice_date = started_at + timedelta(days=30 * (invoice_number - 1))
            if invoice_date > run_date:
                continue

            invoice_id = f"inv_{customer_index:05d}_{invoice_number:02d}"
            due_date = invoice_date + timedelta(days=14)
            late_payment = rng.random() < 0.12
            paid = rng.random() > 0.08
            invoice_status = "paid" if paid else _choice(rng, ["open", "past_due"])
            amount_due = float(mrr)

            invoices.append(
                {
                    "invoice_id": invoice_id,
                    "subscription_id": subscription_id,
                    "customer_id": customer_id,
                    "invoice_date": invoice_date.isoformat(),
                    "due_date": due_date.isoformat(),
                    "amount_due": amount_due,
                    "currency": "USD",
                    "invoice_status": invoice_status,
                }
            )

            if paid:
                payment_delay_days = rng.randrange(0, 20 if late_payment else 8)
                payment_date = invoice_date + timedelta(days=payment_delay_days)
                payments.append(
                    {
                        "payment_id": f"pay_{customer_index:05d}_{invoice_number:02d}",
                        "invoice_id": invoice_id,
                        "customer_id": customer_id,
                        "payment_date": payment_date.isoformat(),
                        "amount_paid": amount_due,
                        "payment_method": _choice(rng, ["card", "ach", "wire", "paypal"]),
                        "payment_status": "succeeded",
                    }
                )

        active_days = max(1, (run_date - started_at).days)
        event_names = ["login", "report_created", "dashboard_viewed", "api_call"]
        event_names.append("export_completed")
        event_rows = rng.randrange(5, 16)
        for event_number in range(1, event_rows + 1):
            event_date = started_at + timedelta(days=rng.randrange(0, active_days + 1))
            event_timestamp = datetime.combine(
                event_date,
                datetime.min.time(),
                tzinfo=UTC,
            ) + timedelta(hours=rng.randrange(0, 24), minutes=rng.randrange(0, 60))
            product_events.append(
                {
                    "event_id": f"evt_{customer_index:05d}_{event_number:03d}",
                    "customer_id": customer_id,
                    "event_timestamp": event_timestamp.isoformat(),
                    "event_name": _choice(rng, event_names),
                    "event_count": rng.randrange(1, 25),
                    "source": _choice(rng, ["web", "api", "mobile"]),
                }
            )

    return {
        "customers": _frame(customers, "customer_id"),
        "subscriptions": _frame(subscriptions, "subscription_id"),
        "invoices": _frame(invoices, "invoice_id"),
        "payments": _frame(payments, "payment_id"),
        "product_events": _frame(product_events, "event_id"),
    }
