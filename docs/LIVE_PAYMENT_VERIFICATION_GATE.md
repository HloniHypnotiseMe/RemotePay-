# RemotePay — Live Payment Verification Gate

## Purpose

This is the final external-account gate for the current C6 Group / Ubernie / RemotePay sprint. No production payment behavior is declared verified until a real SimplyBLU payment is observed end-to-end.

## Already implemented

- C6 and Ubernie remain merchant-facing brands; RemotePay is the payment boundary.
- RemotePay creates the hosted checkout through the SimplyBLU provider adapter.
- Payment links are persisted in the canonical RemotePay transaction ledger.
- Idempotency is enforced on the RemotePay payment-link boundary.
- Provider webhook events are normalized and reconciled into the canonical ledger.
- Unknown provider transactions are rejected instead of silently creating ledger records.

## External verification required

1. Configure the SimplyBLU production/sandbox webhook callback to the deployed RemotePay provider webhook endpoint.
2. Confirm the exact SimplyBLU webhook authentication/signature mechanism available to the merchant account. Do not assume a header or secret that has not been supplied by SimplyBLU.
3. Confirm that the deployed RemotePay environment has its SimplyBLU credentials and database configured through environment/secret storage.
4. Generate an R1 test payment for a C6/Ubernie-originated transaction.
5. Confirm the customer receives the expected SimplyBLU payment communication (email/SMS/link) where enabled by the merchant configuration.
6. Complete the R1 payment.
7. Capture the provider callback/status event and verify RemotePay changes the canonical ledger from `pending` to `paid` with the correct payment ID, transaction ID, brand ID and provider reference.
8. Verify duplicate provider events do not create duplicate economic effects.

## Current stop condition

The repository cannot prove the live SimplyBLU merchant-account webhook configuration or customer notification behavior. Those are external-account facts and must be verified with a real test.

## Success criteria

`C6/Ubernie -> RemotePay -> SimplyBLU hosted checkout -> customer notification -> payment -> provider callback -> RemotePay ledger PAID -> originating brand attribution`.

Only after all steps pass should the payment path be marked production-verified.
