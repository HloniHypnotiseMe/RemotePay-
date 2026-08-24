import pytest

from services.transaction_state import TransactionState, TransactionStateMachine


def test_valid_payment_lifecycle_transition():
    machine = TransactionStateMachine()
    transition = machine.transition("txn_1", TransactionState.PENDING, TransactionState.PAID, "provider confirmed payment")
    assert transition.to_state is TransactionState.PAID


def test_invalid_transition_is_rejected():
    machine = TransactionStateMachine()
    with pytest.raises(ValueError):
        machine.transition("txn_1", TransactionState.FAILED, TransactionState.PAID, "late provider callback")


def test_reason_is_required():
    machine = TransactionStateMachine()
    with pytest.raises(ValueError):
        machine.transition("txn_1", TransactionState.PAID, TransactionState.SETTLED, "")
