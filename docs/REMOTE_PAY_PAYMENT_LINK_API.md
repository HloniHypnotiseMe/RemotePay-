# RemotePay Payment-Link API

**Status:** v1 API boundary

## Create

`POST /api/v1/payment-links`

The request follows the canonical payment contract and requires merchant, brand, source-system, description, amount in minor currency units, currency, and an idempotency key.

Example:

```json
{
  "merchant_id": "merchant_123",
  "brand_id": "ubernie",
  "source_system": "ubernie",
  "description": "Ubernie Customer 1 Test",
  "amount_minor": 100,
  "currency": "ZAR",
  "idempotency_key": "customer-1-test-001"
}
```

Response:

```json
{
  "payment_id": "pay_...",
  "transaction_id": "txn_...",
  "status": "pending",
  "payment_url": "/pay/pay_...",
  "currency": "ZAR",
  "amount_minor": 100,
  "merchant_id": "merchant_123",
  "brand_id": "ubernie"
}
```

Repeated requests with the same idempotency key return the same payment identity rather than creating a duplicate payment link.

## Retrieve

`GET /api/v1/payment-links/{payment_id}`

## Boundary status

This API establishes the RemotePay-facing payment-link contract. It does not yet settle funds or replace the existing provider flow. Persistent transaction-ledger wiring, provider routing, authenticated webhooks, and production payment-link generation remain subsequent implementation work.
