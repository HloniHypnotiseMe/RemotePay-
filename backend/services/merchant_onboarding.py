from dataclasses import dataclass, field
from typing import Dict, List
from uuid import uuid4


@dataclass(frozen=True)
class BrandRegistration:
    brand_id: str
    merchant_id: str
    name: str
    source_systems: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class MerchantRegistration:
    merchant_id: str
    legal_name: str
    brands: List[BrandRegistration]


class MerchantOnboardingService:
    """Minimal server-side merchant/brand registry.

    This is the identity boundary for external businesses. It deliberately
    does not perform KYC/KYB approval or payment processing; those controls
    belong to the compliance and production onboarding layers.
    """

    def __init__(self) -> None:
        self._merchants: Dict[str, MerchantRegistration] = {}

    def register_merchant(self, legal_name: str) -> MerchantRegistration:
        if not legal_name.strip():
            raise ValueError("legal_name is required")

        merchant_id = f"mrc_{uuid4().hex[:16]}"
        registration = MerchantRegistration(
            merchant_id=merchant_id,
            legal_name=legal_name.strip(),
            brands=[],
        )
        self._merchants[merchant_id] = registration
        return registration

    def register_brand(
        self,
        merchant_id: str,
        name: str,
        source_systems: List[str] | None = None,
    ) -> BrandRegistration:
        merchant = self._merchants.get(merchant_id)
        if merchant is None:
            raise KeyError("merchant not found")
        if not name.strip():
            raise ValueError("brand name is required")

        brand = BrandRegistration(
            brand_id=f"brd_{uuid4().hex[:16]}",
            merchant_id=merchant_id,
            name=name.strip(),
            source_systems=list(source_systems or []),
        )
        self._merchants[merchant_id] = MerchantRegistration(
            merchant_id=merchant.merchant_id,
            legal_name=merchant.legal_name,
            brands=[*merchant.brands, brand],
        )
        return brand

    def get_merchant(self, merchant_id: str) -> MerchantRegistration:
        merchant = self._merchants.get(merchant_id)
        if merchant is None:
            raise KeyError("merchant not found")
        return merchant

    def validate_brand(self, merchant_id: str, brand_id: str) -> bool:
        merchant = self._merchants.get(merchant_id)
        return bool(merchant and any(b.brand_id == brand_id for b in merchant.brands))
