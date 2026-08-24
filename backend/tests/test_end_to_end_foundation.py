from services.pricing_profiles import PricingProfile, PricingProfileRegistry
from services.provider_adapter import ProviderPayment, ProviderRegistry
from services.settlement import SettlementLine, SettlementReconciliation
from services.transaction_state_machine import TransactionState, TransactionStateMachine


class FakeProvider:
    name = "fake"

    def create_payment(self, **kwargs):
        return ProviderPayment("fake", "provider_1", "https://example.test/pay", "pending", kwargs)

    def get_payment(self, provider_payment_id):
        return ProviderPayment("fake", provider_payment_id, "https://example.test/pay", "paid", {})

    def refund_payment(self, provider_payment_id, amount_minor=None):
        return ProviderPayment("fake", provider_payment_id, "", "refunded", {})


def test_remote_pay_foundation_end_to_end_contracts():
    pricing = PricingProfileRegistry()
    pricing.register(PricingProfile("ecosystem-v1", "Ecosystem", 250, 30))
    profile = pricing.get_active("ecosystem-v1")

    providers = ProviderRegistry()
    providers.register(FakeProvider())
    payment = providers.get("fake").create_payment(
        amount_minor=10000,
        currency="ZAR",
        reference="uber_customer_1",
        metadata={"brand": "Ubernie", "pricing_profile": profile.profile_id},
    )

    lifecycle = TransactionStateMachine()
    lifecycle.transition(TransactionState.PENDING)
    lifecycle.transition(TransactionState.PAID)
    lifecycle.transition(TransactionState.SETTLED)

    summary = SettlementReconciliation().summarize([
        SettlementLine(payment.provider_payment_id, 10000, 150, 280)
    ])

    assert payment.provider == "fake"
    assert payment.status == "pending"
    assert lifecycle.state is TransactionState.SETTLED
    assert summary.gross_minor == 10000
    assert summary.processor_fees_minor == 150
    assert summary.remotepay_fees_minor == 280
    assert summary.merchant_net_minor == 9570
