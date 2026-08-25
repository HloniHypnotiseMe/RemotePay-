from dataclasses import dataclass

import httpx

from core.config import settings


@dataclass(frozen=True)
class ProviderCheckout:
    provider: str
    provider_payment_id: str
    checkout_url: str
    raw: dict


class SimplyBluProvider:
    """Current underlying processor adapter; merchant-facing callers stay on RemotePay."""

    name = "simplyblu"

    def __init__(self) -> None:
        self.base_url = settings.SIMPLYBLU_API_URL.rstrip("/")
        self.public_key = settings.SIMPLYBLU_PUBLIC_KEY
        self.private_key = settings.SIMPLYBLU_PRIVATE_KEY

    def _require_credentials(self) -> None:
        if not self.public_key or not self.private_key:
            raise RuntimeError("SimplyBlu provider credentials are not configured")

    def create_payment(
        self,
        *,
        amount_minor: int,
        currency: str,
        reference: str,
        description: str,
        return_url: str | None = None,
    ) -> ProviderCheckout:
        self._require_credentials()

        payload = {
            "amount": amount_minor,
            "currency": currency.upper(),
            "description": description,
            "reference": reference,
        }
        if return_url:
            payload["redirectUrl"] = return_url

        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                f"{self.base_url}/payment",
                json=payload,
                auth=(self.public_key, self.private_key),
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            data = response.json()

        checkout_url = (
            data.get("redirectUrl")
            or data.get("paymentUrl")
            or data.get("checkoutUrl")
            or data.get("url")
        )
        if not checkout_url:
            raise RuntimeError("SimplyBlu response did not contain a checkout URL")

        provider_payment_id = str(
            data.get("id")
            or data.get("paymentId")
            or data.get("payment_id")
            or reference
        )
        return ProviderCheckout(self.name, provider_payment_id, checkout_url, data)
