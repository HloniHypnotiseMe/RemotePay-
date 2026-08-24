# RemotePay Transaction Lifecycle

**Status:** foundation

RemotePay transactions use a deterministic state machine:

`created → pending → paid → settled`

Alternative terminal paths include:

- `pending → failed`
- `pending → cancelled`
- `pending → expired`
- `paid → refunded`

## Rules

- A transaction cannot jump directly from `created` to `paid`.
- Failed, cancelled, expired, refunded and settled states are terminal in this foundation.
- A refund is a separate economic event and must not rewrite the historical payment event.
- Settlement closes the payment lifecycle; corrections must be represented as adjustment/refund events.

## Production integration

The state machine is deliberately pure. Production persistence must store every accepted transition with transaction ID, previous state, next state, source event, provider reference, actor/system identity and timestamp.

Provider webhooks must be normalized before attempting a transition. Duplicate events must be idempotent and must not create duplicate state transitions.
