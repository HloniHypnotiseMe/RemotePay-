# RemotePay Transaction Ledger

**Status:** v1 — implemented as the canonical persistence boundary

## Purpose

The transaction ledger is RemotePay Fintech Services' canonical record of payment economic events. It is independent of the underlying processor and preserves the identity, money, lifecycle, and settlement attributes defined by the RemotePay payment contract.

## Canonical record

Each ledger entry contains:

- `payment_id`
- `transaction_id`
- `merchant_id`
- `brand_id`
- `source_system`
- `customer_reference`
- `product_id`
- `offer_id`
- `description`
- `amount_minor`
- `currency`
- `fee_minor`
- `net_settlement_minor`
- `status`
- `provider_reference`
- `provider_metadata`
- `idempotency_key`
- `metadata`
- `created_at`
- `paid_at`
- `settled_at`
- `updated_at`

## Persistence guarantees

The Mongo-backed ledger service creates unique indexes for `payment_id`, `transaction_id`, and `idempotency_key`. It also indexes merchant, brand, and status/time access patterns.

The ledger service provides canonical lookup by payment ID, transaction ID, and idempotency key.

## Money rule

Amounts are integer minor units. For ZAR, `100` means R1.00. Floating-point monetary values are not stored in the canonical ledger.

## Provider boundary

Provider-specific information is retained only as provider reference/metadata. Provider status must be normalized to the RemotePay lifecycle before downstream consumers use it.

## Implementation boundary

This phase establishes the canonical model and persistence service. Payment creation, fee calculation, webhook normalization, settlement, and consumer integrations remain subsequent phases and must write through this ledger rather than maintaining independent transaction stores.
