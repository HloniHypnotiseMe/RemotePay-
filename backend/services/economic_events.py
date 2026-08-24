from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


ALLOWED_STATUSES = {"created", "pending", "paid", "failed", "cancelled", "expired", "refunded"}


@dataclass(frozen=True)
class EconomicEvent:
    event_id: str
    event_type: str
    payment_id: str
    transaction_id: str
    merchant_id: str
    brand_id: str
    source_system: str
    status: str
    amount_minor: int
    currency: str
    occurred_at: str
    provider_reference: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)


def normalize_provider_event(payload: Dict[str, Any], event_id: str) -> EconomicEvent:
    """Normalize provider callback data at the RemotePay boundary."""
    status = str(payload.get("status", "")).lower()
    if status not in ALLOWED_STATUSES:
        raise ValueError("unsupported payment status")

    required = (
        "payment_id",
        "transaction_id",
        "merchant_id",
        "brand_id",
        "source_system",
        "amount_minor",
        "currency",
    )
    missing = [key for key in required if payload.get(key) in (None, "")]
    if missing:
        raise ValueError(f"missing required event fields: {', '.join(missing)}")

    return EconomicEvent(
        event_id=event_id,
        event_type=f"payment.{status}",
        payment_id=str(payload["payment_id"]),
        transaction_id=str(payload["transaction_id"]),
        merchant_id=str(payload["merchant_id"]),
        brand_id=str(payload["brand_id"]),
        source_system=str(payload["source_system"]),
        status=status,
        amount_minor=int(payload["amount_minor"]),
        currency=str(payload["currency"]).upper(),
        occurred_at=str(payload.get("occurred_at") or datetime.now(timezone.utc).isoformat()),
        provider_reference=payload.get("provider_reference"),
        metadata=dict(payload.get("metadata") or {}),
    )


class EconomicEventStore:
    """Idempotent event boundary; persistence can be backed by the ledger later."""

    def __init__(self) -> None:
        self._events: Dict[str, EconomicEvent] = {}

    def record(self, event: EconomicEvent) -> EconomicEvent:
        existing = self._events.get(event.event_id)
        if existing is not None:
            return existing
        self._events[event.event_id] = event
        return event
