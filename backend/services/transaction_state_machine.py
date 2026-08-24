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
    TransactionState.CREATED: {TransactionState.PENDING, TransactionState.CANCELLED},
    TransactionState.PENDING: {
        TransactionState.PAID,
        TransactionState.FAILED,
        TransactionState.CANCELLED,
        TransactionState.EXPIRED,
    },
    TransactionState.PAID: {TransactionState.REFUNDED, TransactionState.SETTLED},
    TransactionState.FAILED: set(),
    TransactionState.CANCELLED: set(),
    TransactionState.EXPIRED: set(),
    TransactionState.REFUNDED: set(),
    TransactionState.SETTLED: set(),
}


class InvalidTransition(ValueError):
    pass


class TransactionStateMachine:
    """Small deterministic lifecycle guard; persistence/audit lives above it."""

    def __init__(self, state: TransactionState = TransactionState.CREATED) -> None:
        self.state = state

    def transition(self, target: TransactionState) -> TransactionState:
        if target not in _ALLOWED[self.state]:
            raise InvalidTransition(f"cannot transition {self.state.value} -> {target.value}")
        self.state = target
        return self.state
