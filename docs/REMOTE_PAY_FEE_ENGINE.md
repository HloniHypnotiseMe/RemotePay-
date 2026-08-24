# RemotePay Fee Engine

**Status:** v1 — implementation foundation

## Purpose

RemotePay Fintech Services calculates its transaction fee centrally. Product code must not implement its own RemotePay pricing arithmetic.

The engine accepts a server-selected `FeeRule` and returns gross amount, fee, and net settlement in integer minor currency units.

## Rule

`fee = round(gross × percentage_bps / 10,000) + fixed_minor`, then apply optional minimum/maximum bounds.

Example:

- Gross: `10_000` minor units (R100.00)
- Rate: `250` basis points (2.50%)
- Fixed: `30` minor units (R0.30)
- Fee: `280` minor units (R2.80)
- Net settlement: `9_720` minor units (R97.20)

## Important commercial boundary

This implementation intentionally does **not** choose the production RemotePay price. The actual merchant/brand pricing schedule must be approved and stored in the server-side pricing/configuration layer in the commercial-pricing phase.

This prevents another thumbsucked price from becoming embedded in production code.

## Safety

- No floating-point money arithmetic.
- Fee cannot exceed gross payment.
- Minimum and maximum fee bounds are supported.
- Pricing is supplied by server-side configuration.
- The engine calculates values only; it does not move, settle, or refund funds.
