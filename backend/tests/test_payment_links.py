from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_payment_link_creation_and_idempotency():
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

    second = client.post("/api/v1/payment-links", json=payload)
    assert second.status_code == 201
    assert second.json() == first_body


def test_missing_payment_link_returns_404():
    response = client.get("/api/v1/payment-links/pay_missing")
    assert response.status_code == 404
