from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class PricingProfile:
    profile_id: str
    name: str
    percentage_bps: int
    fixed_minor: int
    minimum_minor: int | None = None
    maximum_minor: int | None = None
    active: bool = True


class PricingProfileRegistry:
    """Server-side RemotePay commercial pricing configuration.

    A profile describes what RemotePay charges a merchant/brand. It is
    intentionally separate from provider costs and from the fee arithmetic
    engine.
    """

    def __init__(self) -> None:
        self._profiles: Dict[str, PricingProfile] = {}

    def register(self, profile: PricingProfile) -> PricingProfile:
        if profile.percentage_bps < 0 or profile.fixed_minor < 0:
            raise ValueError("pricing values must be non-negative")
        if profile.minimum_minor is not None and profile.minimum_minor < 0:
            raise ValueError("minimum_minor must be non-negative")
        if profile.maximum_minor is not None and profile.maximum_minor < 0:
            raise ValueError("maximum_minor must be non-negative")
        if (
            profile.minimum_minor is not None
            and profile.maximum_minor is not None
            and profile.minimum_minor > profile.maximum_minor
        ):
            raise ValueError("minimum_minor cannot exceed maximum_minor")

        self._profiles[profile.profile_id] = profile
        return profile

    def get_active(self, profile_id: str) -> PricingProfile:
        profile = self._profiles.get(profile_id)
        if profile is None or not profile.active:
            raise KeyError("active pricing profile not found")
        return profile
