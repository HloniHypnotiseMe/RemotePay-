import pytest

from services.fee_engine import FeeRule, RemotePayFeeEngine


def test_percentage_plus_fixed_fee():
    result = RemotePayFeeEngine().calculate(
        10_000,
        FeeRule(percentage_bps=250, fixed_minor=30),
    )

    assert result.gross_minor == 10_000
    assert result.fee_minor == 280
    assert result.net_settlement_minor == 9_720


def test_rounds_percentage_to_minor_unit():
    result = RemotePayFeeEngine().calculate(
        101,
        FeeRule(percentage_bps=250),
    )

    assert result.fee_minor == 3
    assert result.net_settlement_minor == 98


def test_minimum_and_maximum_are_enforced():
    engine = RemotePayFeeEngine()

    assert engine.calculate(100, FeeRule(minimum_minor=50)).fee_minor == 50
    assert engine.calculate(10_000, FeeRule(maximum_minor=100)).fee_minor == 100


def test_fee_cannot_exceed_gross_payment():
    with pytest.raises(ValueError):
        RemotePayFeeEngine().calculate(100, FeeRule(fixed_minor=101))
