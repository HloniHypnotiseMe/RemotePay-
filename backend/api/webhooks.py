from typing import Any, Dict

from fastapi import APIRouter, Header, HTTPException

from services.economic_events import EconomicEventStore, normalize_provider_event
from services.transaction_ledger import TransactionLedger

router = APIRouter()
economic_events = EconomicEventStore()
ledger = None


async def _ledger():
    global ledger
    if ledger is None:
        ledger = TransactionLedger()
        await ledger.ensure_indexes()
    return ledger


@router.post("/webhooks/provider", status_code=202)
async def provider_webhook(
    payload: Dict[str, Any],
    x_remotepay_event_id: str = Header(...),
):
    """Accept provider callbacks only at the RemotePay boundary.

    The provider adapter must validate provider signatures before production
    traffic is routed here. The event ID is the idempotency key for economic
    event processing.
    """
    if not x_remotepay_event_id.strip():
        raise HTTPException(status_code=400, detail="event ID is required")

    try:
        event = normalize_provider_event(payload, x_remotepay_event_id)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    stored = economic_events.record(event)
    reconciled = await (await _ledger()).apply_provider_event(stored)

    if reconciled is None:
        raise HTTPException(
            status_code=409,
            detail="Provider event accepted but no matching RemotePay transaction exists",
        )

    return {
        "accepted": True,
        "duplicate": stored is not event,
        "event_id": stored.event_id,
        "event_type": stored.event_type,
        "status": reconciled.status,
        "payment_id": reconciled.payment_id,
        "transaction_id": reconciled.transaction_id,
        "brand_id": reconciled.brand_id,
        "merchant_id": reconciled.merchant_id,
    }
