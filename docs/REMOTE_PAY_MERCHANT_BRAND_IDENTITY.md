# RemotePay Merchant & Brand Identity Model

**Status:** v1 — approved for ecosystem implementation

## Purpose

RemotePay Fintech Services is the payment business of record. Every payment must be attributable to a merchant, the commercial brand presented to the customer, and the source system that initiated the payment.

## Identity hierarchy

```text
RemotePay Fintech Services
        |
        +-- Merchant Account
              |
              +-- Brand
                    |
                    +-- Source System / Channel
                          |
                          +-- Payment
```

### Merchant

The legal/commercial party whose funds are processed and settled through RemotePay. A merchant has a stable `merchant_id` and its own onboarding, status, settlement, and fee configuration.

Examples include C6 Group, Ubernie, and external client businesses where each is onboarded as a distinct merchant relationship.

### Brand

The customer-facing commercial identity operating under a merchant relationship. A brand has a stable `brand_id`, display name, status, and optional parent/merchant relationship.

A brand is **not** automatically treated as a separate legal entity. Legal ownership and corporate relationships remain explicit business data rather than assumptions in payment code.

### Source system

The application/channel that originated the payment request, represented by a stable `source_system` identifier such as `ubernie`, `c6-group`, `online-shop`, or `api`.

Source system is operational metadata; it does not determine legal ownership.

## Canonical identifiers

- `merchant_id` — immutable RemotePay merchant identifier.
- `brand_id` — immutable RemotePay brand identifier.
- `source_system` — controlled identifier for the originating application/channel.
- `customer_reference` — merchant-scoped customer reference; avoid exposing unnecessary PII in payment records.
- `payment_id` — immutable RemotePay payment identifier.
- `transaction_id` — immutable RemotePay transaction identifier.

IDs must not be derived from display names, domains, email addresses, or mutable business attributes.

## Required relationships

Every payment must resolve to:

1. one active merchant;
2. one active brand belonging to that merchant;
3. one recognized source system;
4. one payment/transaction identity.

The payment contract may carry `brand_id` and `source_system`, but RemotePay must validate their relationship to the merchant server-side.

## Internal ecosystem rule

C6 Group and Ubernie may use RemotePay as merchants/brands. RemotePay remains the independent payment business/provider boundary. The current processor is an implementation detail behind RemotePay and must not be used as the merchant identity.

## External merchant rule

External clients receive their own merchant identity and may configure one or more brands/channels under that merchant. Their payment traffic remains attributable to the merchant while RemotePay calculates the applicable fees and settlement amounts.

## Minimum merchant record

```json
{
  "merchant_id": "mrc_123",
  "legal_name": "Example Business (Pty) Ltd",
  "display_name": "Example Business",
  "status": "active",
  "default_currency": "ZAR",
  "fee_plan_id": "plan_standard"
}
```

## Minimum brand record

```json
{
  "brand_id": "brd_ubernie",
  "merchant_id": "mrc_ubernie",
  "name": "Ubernie",
  "status": "active"
}
```

## Controls

- Merchant and brand identifiers are server-assigned and immutable.
- A disabled merchant or brand cannot create new payments.
- Brand ownership is validated on every payment creation request.
- Fee and settlement configuration belongs to the merchant relationship, not to a client-controlled payment request.
- Customer-facing labels may be customized, but must never change the underlying merchant/brand identity.
- Corporate ownership must not be inferred from brand names.

## Implementation status

This document establishes the canonical identity model. It does not claim the current RemotePay codebase already implements merchant/brand persistence or validation. Those are implementation work for the subsequent transaction/ledger phases.
