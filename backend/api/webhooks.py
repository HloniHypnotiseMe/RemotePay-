from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException

from services.economic_events import EconomicEventStore, normalize_provider_event

router = APIRouter()
economic_events = EconomicEventStore()


@router.post("/webhooks/provider", status_code=202)
async def provider_webhook(
    payload: Dict[str, Any],
    x_remotepay_event_id: str = Header(...),
):
    """Accept provider callbacks only at the RemotePay boundary.

    Signature verification must be performed by the configured provider adapter
    before this handler is exposed to production traffic. The event ID is the
    idempotency key for downstream economic-event processing.
    """
    if not x_remotepay_event_id.strip():
        raise HTTPException(status_code=400, detail="event ID is required")

    try:
        event = normalize_provider_event(payload, x_remotepay_event_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    stored = economic_events.record(event)
    return {
        "accepted": True,
        "duplicate": stored is not event,
        "event_id": stored.event_id,
        "event_type": stored.event_type,
        "status": stored.status,
        "payment_id": stored.payment_id,
        "transaction_id": stored.transaction_id,
    }
