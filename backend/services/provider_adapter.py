from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class ProviderPayment:
    provider: str
    provider_payment_id: str
    checkout_url: str
    status: str
    raw: dict[str, Any]


class PaymentProvider(Protocol):
    name: str

    def create_payment(self, *, amount_minor: int, currency: str, reference: str, metadata: dict[str, Any]) -> ProviderPayment:
        ...

    def get_payment(self, provider_payment_id: str) -> ProviderPayment:
        ...

    def refund_payment(self, provider_payment_id: str, amount_minor: int | None = None) -> ProviderPayment:
        ...


class ProviderRegistry:
    """Maps RemotePay provider names to isolated provider adapters."""

    def __init__(self) -> None:
        self._providers: dict[str, PaymentProvider] = {}

    def register(self, provider: PaymentProvider) -> None:
        if not provider.name.strip():
            raise ValueError("provider name is required")
        self._providers[provider.name] = provider

    def get(self, name: str) -> PaymentProvider:
        provider = self._providers.get(name)
        if provider is None:
            raise KeyError(f"payment provider not registered: {name}")
        return provider
