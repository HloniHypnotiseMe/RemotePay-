from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


@dataclass(frozen=True)
class FeeRule:
    """Server-side RemotePay transaction pricing rule."""

    percentage_bps: int = 0
    fixed_minor: int = 0
    minimum_minor: Optional[int] = None
    maximum_minor: Optional[int] = None

    def calculate(self, amount_minor: int) -> int:
        if amount_minor < 0:
            raise ValueError("amount_minor must be non-negative")

        percentage = (
            Decimal(amount_minor) * Decimal(self.percentage_bps) / Decimal(10_000)
        ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        fee = int(percentage) + self.fixed_minor

        if self.minimum_minor is not None:
            fee = max(fee, self.minimum_minor)
        if self.maximum_minor is not None:
            fee = min(fee, self.maximum_minor)

        return max(fee, 0)


@dataclass(frozen=True)
class FeeCalculation:
    gross_minor: int
    fee_minor: int
    net_settlement_minor: int


class RemotePayFeeEngine:
    """Calculate RemotePay fees without embedding pricing in product code.

    Pricing is supplied by the merchant/brand configuration layer. This engine
    performs only deterministic money arithmetic and does not persist or move
    funds.
    """

    def calculate(
        self,
        amount_minor: int,
        rule: FeeRule,
    ) -> FeeCalculation:
        if amount_minor < 0:
            raise ValueError("amount_minor must be non-negative")

        fee_minor = rule.calculate(amount_minor)
        if fee_minor > amount_minor:
            raise ValueError("calculated fee cannot exceed gross payment")

        return FeeCalculation(
            gross_minor=amount_minor,
            fee_minor=fee_minor,
            net_settlement_minor=amount_minor - fee_minor,
        )
