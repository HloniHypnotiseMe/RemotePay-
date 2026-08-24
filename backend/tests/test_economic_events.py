import pytest

from services.economic_events import EconomicEventStore, normalize_provider_event


def payload():
    return {
        "payment_id": "pay_123",
        "transaction_id": "txn_123",
        "merchant_id": "merchant_123",
        "brand_id": "ubernie",
        "source_system": "ubernie",
        "status": "paid",
        "amount_minor": 100,
        "currency": "zar",
        "provider_reference": "provider_123",
    }


def test_provider_event_is_normalized():
    event = normalize_provider_event(payload(), "evt_123")
    assert event.event_type == "payment.paid"
    assert event.currency == "ZAR"
    assert event.amount_minor == 100


def test_event_store_is_idempotent():
    store = EconomicEventStore()
    first = normalize_provider_event(payload(), "evt_123")
    second = normalize_provider_event(payload(), "evt_123")

    assert store.record(first) is first
    assert store.record(second) is first


def test_unknown_status_is_rejected():
    data = payload()
    data["status"] = "mystery"
    with pytest.raises(ValueError):
        normalize_provider_event(data, "evt_bad")
