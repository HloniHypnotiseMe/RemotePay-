from services.simplyblu_provider import SimplyBluProvider


def test_simplyblu_provider_normalizes_checkout_url(monkeypatch):
    provider = SimplyBluProvider()

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "id": "sb_123",
                "redirectUrl": "https://sandbox.example.test/pay/sb_123",
            }

    class FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr("services.simplyblu_provider.httpx.Client", lambda **kwargs: FakeClient())
    provider.public_key = "public"
    provider.private_key = "private"

    result = provider.create_payment(
        amount_minor=100,
        currency="ZAR",
        reference="txn_1",
        description="Test payment",
    )

    assert result.provider == "simplyblu"
    assert result.provider_payment_id == "sb_123"
    assert result.checkout_url == "https://sandbox.example.test/pay/sb_123"
