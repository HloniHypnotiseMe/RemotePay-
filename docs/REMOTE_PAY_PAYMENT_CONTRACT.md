# RemotePay Canonical Payment Contract

**Status:** v1 — approved for ecosystem implementation

## Purpose

RemotePay Fintech Services is the payment business of record for the C6 ecosystem and external merchants. C6 Group, Ubernie, future brands, and external merchants integrate with the RemotePay contract rather than implementing provider-specific payment logic.

The current underlying processing rail may change over time. Provider details must therefore remain an implementation detail of RemotePay, not the merchant-facing identity of the payment system.

## Canonical payment request

```json
{
  "merchant_id": "merchant_123",
  "brand_id": "ubernie",
  "source_system": "ubernie",
  "customer_reference": "customer_1",
  "product_id": "product_123",
  "offer_id": "offer_123",
  "description": "Ubernie Customer 1 Test",
  "amount_minor": 100,
  "currency": "ZAR",
  "return_url": "https://example.com/payment/success",
  "cancel_url": "https://example.com/payment/cancel",
  "idempotency_key": "unique-request-123",
  "metadata": {}
}
```

## Canonical payment response

```json
{
  "payment_id": "pay_123",
  "transaction_id": "txn_123",
  "status": "pending",
  "payment_url": "https://...",
  "currency": "ZAR",
  "amount_minor": 100,
  "merchant_id": "merchant_123",
  "brand_id": "ubernie"
}
```

## Canonical lifecycle

`created → pending → paid | failed | cancelled | expired → refunded (where applicable)`

Provider callbacks must be normalized into these RemotePay statuses before being emitted to consuming systems.

## Economic-event fields

A settled/paid transaction must retain, at minimum:

- `payment_id`
- `transaction_id`
- `merchant_id`
- `brand_id`
- `source_system`
- `customer_reference`
- `product_id`
- `offer_id`
- `amount_minor`
- `currency`
- `fee_minor` (when calculated)
- `net_settlement_minor` (when calculated)
- `provider_reference` (internal/provider-facing)
- `status`
- `created_at`
- `paid_at` (when applicable)
- `settled_at` (when applicable)
- `idempotency_key`
- `metadata`

## Rules

1. **RemotePay is the payment provider identity exposed to ecosystem consumers.**
2. Provider/acquirer integrations are behind the RemotePay boundary.
3. No C6 product should directly implement provider-specific payment logic.
4. `idempotency_key` is mandatory for payment creation.
5. Amounts are represented in minor currency units to avoid floating-point money errors.
6. Currency is explicit and defaults to ZAR only at the API boundary.
7. Merchant/brand/source identity must survive the complete payment lifecycle.
8. Webhooks must be authenticated, idempotent, and normalized before downstream delivery.
9. Fees and settlement amounts are recorded separately from gross payment amount.
10. This contract does not authorize live payment or settlement by itself; provider configuration and applicable production controls remain separate.

## Current implementation gap

The existing RemotePay repository has a payment endpoint with an in-memory transaction store and provider-specific payment creation. It currently models `amount`, `currency`, `customer_id`, return/cancel URLs, item data, transaction ID, and pending status, but does not yet implement this full canonical contract. The existing implementation also calls a PayFast service directly. This document therefore defines the target boundary for the next implementation phases; it does not claim those capabilities are already production-complete.
