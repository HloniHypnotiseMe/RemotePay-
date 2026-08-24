from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class SettlementLine:
    transaction_id: str
    gross_minor: int
    processor_fee_minor: int
    remotepay_fee_minor: int
    adjustments_minor: int = 0

    @property
    def merchant_net_minor(self) -> int:
        return (
            self.gross_minor
            - self.processor_fee_minor
            - self.remotepay_fee_minor
            + self.adjustments_minor
        )


@dataclass(frozen=True)
class SettlementSummary:
    transaction_count: int
    gross_minor: int
    processor_fees_minor: int
    remotepay_fees_minor: int
    adjustments_minor: int
    merchant_net_minor: int


class SettlementReconciliation:
    """Deterministic settlement arithmetic for a closed settlement batch."""

    def summarize(self, lines: Iterable[SettlementLine]) -> SettlementSummary:
        rows = list(lines)
        if any(v < 0 for row in rows for v in (
            row.gross_minor,
            row.processor_fee_minor,
            row.remotepay_fee_minor,
        )):
            raise ValueError("gross and fee amounts must be non-negative")

        return SettlementSummary(
            transaction_count=len(rows),
            gross_minor=sum(r.gross_minor for r in rows),
            processor_fees_minor=sum(r.processor_fee_minor for r in rows),
            remotepay_fees_minor=sum(r.remotepay_fee_minor for r in rows),
            adjustments_minor=sum(r.adjustments_minor for r in rows),
            merchant_net_minor=sum(r.merchant_net_minor for r in rows),
        )
