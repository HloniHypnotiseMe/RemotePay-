import pytest

from services.transaction_state_machine import (
    InvalidTransition,
    TransactionState,
    TransactionStateMachine,
)


def test_happy_path_to_settlement():
    machine = TransactionStateMachine()
    machine.transition(TransactionState.PENDING)
    machine.transition(TransactionState.PAID)
    machine.transition(TransactionState.SETTLED)
    assert machine.state is TransactionState.SETTLED


def test_invalid_transition_is_rejected():
    machine = TransactionStateMachine()
    with pytest.raises(InvalidTransition):
        machine.transition(TransactionState.PAID)


def test_failed_transaction_is_terminal():
    machine = TransactionStateMachine(TransactionState.FAILED)
    with pytest.raises(InvalidTransition):
        machine.transition(TransactionState.PAID)
