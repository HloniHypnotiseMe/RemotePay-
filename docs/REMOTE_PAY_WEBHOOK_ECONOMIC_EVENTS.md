# RemotePay Webhook → Economic Event Pipeline

**Status:** v1 — implementation foundation

Provider callbacks enter RemotePay through one normalized boundary. Downstream products must consume RemotePay events, not provider-specific webhook payloads.

## Flow

`Provider callback → RemotePay webhook boundary → normalization → idempotent event store → transaction ledger/economic consumers`

## Canonical event types

- `payment.created`
- `payment.pending`
- `payment.paid`
- `payment.failed`
- `payment.cancelled`
- `payment.expired`
- `payment.refunded`

## Required event identity

Every event carries `event_id`, `payment_id`, `transaction_id`, `merchant_id`, `brand_id`, and `source_system`.

The `event_id` is the downstream idempotency key. Re-delivery of the same provider event must not create a second economic event.

## Important production gap

The current implementation provides the normalization and idempotency boundary, but provider signature verification and persistent event storage must be wired through the provider adapter and transaction ledger before production webhook traffic is enabled.

No provider-specific callback format should leak into Ubernie, C6 Group, or external merchant applications.
