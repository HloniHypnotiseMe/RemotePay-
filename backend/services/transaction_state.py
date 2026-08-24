from dataclasses import dataclass
from enum import Enum


class TransactionState(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    SETTLED = "settled"


_ALLOWED: dict[TransactionState, set[TransactionState]] = {
    TransactionState.CREATED: {TransactionState.PENDING, TransactionState.CANCELLED, TransactionState.EXPIRED},
    TransactionState.PENDING: {TransactionState.PAID, TransactionState.FAILED, TransactionState.CANCELLED, TransactionState.EXPIRED},
    TransactionState.PAID: {TransactionState.REFUNDED, TransactionState.SETTLED},
    TransactionState.SETTLED: {TransactionState.REFUNDED},
    TransactionState.FAILED: set(),
    TransactionState.CANCELLED: set(),
    TransactionState.EXPIRED: set(),
    TransactionState.REFUNDED: set(),
}


@dataclass(frozen=True)
class Transition:
    transaction_id: str
    from_state: TransactionState
    to_state: TransactionState
    reason: str


class TransactionStateMachine:
    def transition(self, transaction_id: str, current: TransactionState, target: TransactionState, reason: str) -> Transition:
        if not transaction_id.strip():
            raise ValueError("transaction_id is required")
        if not reason.strip():
            raise ValueError("transition reason is required")
        if target not in _ALLOWED[current]:
            raise ValueError(f"invalid transaction transition: {current.value} -> {target.value}")
        return Transition(transaction_id, current, target, reason.strip())
