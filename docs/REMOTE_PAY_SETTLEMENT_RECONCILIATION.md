# RemotePay Settlement & Reconciliation

**Status:** foundation

Every settlement batch must explain the complete money movement:

`Gross customer payments - processor costs - RemotePay fees +/- adjustments = merchant net`

## Settlement line

Each transaction contributes:

- transaction ID
- gross amount
- processor fee
- RemotePay commercial fee
- adjustments
- merchant net

All monetary values are integer minor currency units.

## Reconciliation

A settlement batch produces deterministic totals for transaction count, gross, processor fees, RemotePay fees, adjustments, and merchant net.

The arithmetic is intentionally separate from provider-specific settlement files. Provider adapters will normalize external settlement records into `SettlementLine` values.

## Production requirements still outstanding

Before live settlement:

1. Persist settlement batches and lines.
2. Store provider settlement IDs and timestamps.
3. Match provider transactions against RemotePay transaction IDs.
4. Record unmatched, duplicate, and short/over-settled items.
5. Make settlement batches immutable after close, with adjustment events for corrections.
6. Persist the RemotePay pricing-profile version used for every fee.
7. Generate merchant statements and an audit trail.
