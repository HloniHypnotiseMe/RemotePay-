from services.settlement import SettlementLine, SettlementReconciliation


def test_settlement_reconciles_gross_costs_and_net():
    summary = SettlementReconciliation().summarize([
        SettlementLine("txn_1", 10000, 150, 280),
        SettlementLine("txn_2", 5000, 75, 155, adjustments_minor=100),
    ])

    assert summary.transaction_count == 2
    assert summary.gross_minor == 15000
    assert summary.processor_fees_minor == 225
    assert summary.remotepay_fees_minor == 435
    assert summary.adjustments_minor == 100
    assert summary.merchant_net_minor == 14440
