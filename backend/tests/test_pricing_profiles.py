import pytest

from services.pricing_profiles import PricingProfile, PricingProfileRegistry


def test_register_and_get_active_profile():
    registry = PricingProfileRegistry()
    profile = PricingProfile(
        profile_id="standard-v1",
        name="Standard",
        percentage_bps=250,
        fixed_minor=30,
    )

    assert registry.register(profile) == profile
    assert registry.get_active("standard-v1") == profile


def test_inactive_profile_is_not_selectable():
    registry = PricingProfileRegistry()
    registry.register(
        PricingProfile(
            profile_id="retired",
            name="Retired",
            percentage_bps=250,
            fixed_minor=30,
            active=False,
        )
    )

    with pytest.raises(KeyError):
        registry.get_active("retired")


def test_invalid_bounds_are_rejected():
    with pytest.raises(ValueError):
        PricingProfileRegistry().register(
            PricingProfile(
                profile_id="bad",
                name="Bad",
                percentage_bps=250,
                fixed_minor=30,
                minimum_minor=100,
                maximum_minor=50,
            )
        )
