from fastapi.testclient import TestClient

from main import app
import api.webhooks as webhooks_api
from models.transaction_ledger import TransactionLedgerEntry


client = TestClient(app)


class FakeLedger:
    def __init__(self):
        self.entries = {
            "pay_test": TransactionLedgerEntry(
                payment_id="pay_test",
                transaction_id="txn_test",
                merchant_id="merchant_test",
                brand_id="ubernie",
                source_system="ubernie",
                description="test payment",
                amount_minor=100,
                currency="ZAR",
                status="pending",
                provider_reference="sb_test",
                idempotency_key="idem_test",
            )
        }

    async def ensure_indexes(self):
        return None

    async def apply_provider_event(self, event):
        entry = self.entries.get(event.payment_id)
        if entry is None or entry.transaction_id != event.transaction_id:
            return None
        return entry.model_copy(update={"status": event.status, "provider_reference": event.provider_reference})


def test_provider_webhook_reconciles_payment(monkeypatch):
    fake_ledger = FakeLedger()
    monkeypatch.setattr(webhooks_api, "ledger", fake_ledger)

    payload = {
        "payment_id": "pay_test",
        "transaction_id": "txn_test",
        "merchant_id": "merchant_test",
        "brand_id": "ubernie",
        "source_system": "ubernie",
        "status": "paid",
        "amount_minor": 100,
        "currency": "ZAR",
        "provider_reference": "sb_paid_1",
    }

    response = client.post(
        "/api/v1/webhooks/provider",
        headers={"x-remotepay-event-id": "evt_test_1"},
        json=payload,
    )

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "paid"
    assert body["payment_id"] == "pay_test"
    assert body["brand_id"] == "ubernie"


def test_provider_webhook_rejects_unknown_transaction(monkeypatch):
    fake_ledger = FakeLedger()
    monkeypatch.setattr(webhooks_api, "ledger", fake_ledger)

    payload = {
        "payment_id": "pay_missing",
        "transaction_id": "txn_missing",
        "merchant_id": "merchant_test",
        "brand_id": "c6group",
        "source_system": "c6group",
        "status": "paid",
        "amount_minor": 100,
        "currency": "ZAR",
    }

    response = client.post(
        "/api/v1/webhooks/provider",
        headers={"x-remotepay-event-id": "evt_test_2"},
        json=payload,
    )

    assert response.status_code == 409
