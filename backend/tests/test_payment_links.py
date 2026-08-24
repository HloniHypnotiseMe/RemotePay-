from datetime import datetime, timezone

from fastapi.testclient import TestClient

import api.payment_links as payment_links
from main import app, settings
from models.transaction_ledger import TransactionLedgerEntry


class FakeLedger:
    def __init__(self):
        self.entries = {}
        self.idempotency = {}

    async def get_by_idempotency_key(self, key):
        return self.idempotency.get(key)

    async def get_by_payment_id(self, payment_id):
        return self.entries.get(payment_id)

    async def create(self, entry):
        self.entries[entry.payment_id] = entry
        self.idempotency[entry.idempotency_key] = entry
        return entry


settings.REMOTEPAY_API_KEYS_JSON = '{"test-key":"merchant_test"}'
payment_links.ledger = FakeLedger()
client = TestClient(app)
HEADERS = {"Authorization": "Bearer test-key"}


def payload():
    return {
        "merchant_id": "merchant_test",
        "brand_id": "ubernie",
        "source_system": "ubernie",
        "description": "Ubernie Customer 1 Test",
        "amount_minor": 100,
        "currency": "ZAR",
        "return_url": "https://ubernie.co.za/payment/success",
        "cancel_url": "https://ubernie.co.za/packages",
        "idempotency_key": "ubernie-test-payment-1",
    }


def test_payment_link_creation_and_idempotency():
    first = client.post("/api/v1/payment-links", json=payload(), headers=HEADERS)
    assert first.status_code == 201
    first_body = first.json()
    assert first_body["payment_url"].endswith(f"/pay/{first_body['payment_id']}")

    second = client.post("/api/v1/payment-links", json=payload(), headers=HEADERS)
    assert second.status_code == 201
    assert second.json() == first_body


def test_payment_link_rejects_wrong_merchant():
    data = payload()
    data["merchant_id"] = "another_merchant"
    response = client.post("/api/v1/payment-links", json=data, headers=HEADERS)
    assert response.status_code == 403


def test_payment_link_requires_authentication():
    response = client.post("/api/v1/payment-links", json=payload())
    assert response.status_code == 401


def test_missing_payment_link_returns_404():
    response = client.get("/api/v1/payment-links/pay_missing", headers=HEADERS)
    assert response.status_code == 404
