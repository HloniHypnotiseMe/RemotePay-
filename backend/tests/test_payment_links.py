from fastapi.testclient import TestClient

from main import app
from models.transaction_ledger import TransactionLedgerEntry
from services.simplyblu_provider import ProviderCheckout, SimplyBluProvider
import api.payment_links as payment_links_api


client = TestClient(app)


class FakeLedger:
    def __init__(self):
        self.entries = {}
        self.idempotency = {}

    async def ensure_indexes(self):
        return None

    async def create(self, entry):
        self.entries[entry.payment_id] = entry
        self.idempotency[entry.idempotency_key] = entry.payment_id
        return entry

    async def get_by_payment_id(self, payment_id):
        return self.entries.get(payment_id)

    async def get_by_idempotency_key(self, key):
        payment_id = self.idempotency.get(key)
        return self.entries.get(payment_id) if payment_id else None


def fake_checkout(self, *, amount_minor, currency, reference, description, return_url=None):
    return ProviderCheckout(
        provider="simplyblu",
        provider_payment_id="sb_test_1",
        checkout_url="https://sandbox.example.test/pay/sb_test_1",
        raw={"amount": amount_minor, "currency": currency},
    )


def test_payment_link_creation_and_idempotency(monkeypatch):
    fake_ledger = FakeLedger()
    monkeypatch.setattr(payment_links_api, "ledger", fake_ledger)
    monkeypatch.setattr(payment_links_api, "ledger_ready", False)
    monkeypatch.setattr(payment_links_api.settings, "DATABASE_URL", "mongodb://test")
    monkeypatch.setattr(SimplyBluProvider, "create_payment", fake_checkout)

    payload = {
        "merchant_id": "merchant_test",
        "brand_id": "ubernie",
        "source_system": "ubernie",
        "description": "Ubernie Customer 1 Test",
        "amount_minor": 100,
        "currency": "ZAR",
        "idempotency_key": "ubernie-test-payment-1",
    }

    first = client.post("/api/v1/payment-links", json=payload)
    assert first.status_code == 201
    first_body = first.json()
    assert first_body["payment_url"].startswith("https://")

    second = client.post("/api/v1/payment-links", json=payload)
    assert second.status_code == 201
    assert second.json() == first_body


def test_missing_payment_link_returns_404(monkeypatch):
    fake_ledger = FakeLedger()
    monkeypatch.setattr(payment_links_api, "ledger", fake_ledger)
    monkeypatch.setattr(payment_links_api, "ledger_ready", False)
    monkeypatch.setattr(payment_links_api.settings, "DATABASE_URL", "mongodb://test")

    response = client.get("/api/v1/payment-links/pay_missing")
    assert response.status_code == 404
