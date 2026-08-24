# RemotePay Commercial Pricing

**Status:** configuration foundation — no production rate approved here

RemotePay must separate its own commercial pricing from the cost charged by an underlying payment processor.

## Money flow

`Customer gross payment → processor cost → RemotePay commercial fee → merchant net settlement`

The processor cost is an infrastructure/provider concern. The RemotePay fee is a commercial product decision.

## Pricing profiles

A `PricingProfile` contains:

- profile ID
- human-readable name
- percentage fee in basis points
- fixed fee in currency minor units
- optional minimum fee
- optional maximum fee
- active/inactive status

The profile is selected server-side. Clients must not be allowed to choose arbitrary pricing values in a payment request.

## Commercial segmentation

The architecture supports separate profiles for:

- C6 Group ecosystem brands
- Ubernie
- other C6 subsidiaries/verticals
- external merchants
- negotiated enterprise accounts
- future volume tiers

No assumption is made here that every brand pays the same rate.

## Production rule

Do not ship a hard-coded rate as the final RemotePay commercial schedule. The approved pricing matrix must be loaded into the server-side configuration/database and versioned with an effective date before live merchant billing begins.

## Current state

The pricing registry and validation are implemented. The next integration must connect the selected profile to the fee engine and transaction ledger, while preserving the exact profile/version used for each transaction for auditability.
