import pytest

from services.merchant_onboarding import MerchantOnboardingService


def test_register_merchant_and_brand():
    service = MerchantOnboardingService()
    merchant = service.register_merchant("Example Business (Pty) Ltd")
    brand = service.register_brand(merchant.merchant_id, "Example Brand", ["website"])

    assert brand.merchant_id == merchant.merchant_id
    assert service.validate_brand(merchant.merchant_id, brand.brand_id)


def test_brand_cannot_be_attached_to_unknown_merchant():
    service = MerchantOnboardingService()
    with pytest.raises(KeyError):
        service.register_brand("mrc_missing", "Example Brand")
