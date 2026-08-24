from services.provider_adapter import ProviderPayment, ProviderRegistry


class FakeProvider:
    name = "fake"

    def create_payment(self, **kwargs):
        return ProviderPayment("fake", "pay_1", "https://example.test/pay_1", "pending", kwargs)

    def get_payment(self, provider_payment_id):
        return ProviderPayment("fake", provider_payment_id, "https://example.test/pay", "paid", {})

    def refund_payment(self, provider_payment_id, amount_minor=None):
        return ProviderPayment("fake", provider_payment_id, "", "refunded", {})


def test_provider_registry_isolates_provider_choice():
    registry = ProviderRegistry()
    provider = FakeProvider()
    registry.register(provider)

    assert registry.get("fake") is provider
