# RemotePay External Merchant Onboarding

**Status:** foundation

RemotePay supports external businesses as first-class merchants. A merchant may have multiple brands and source systems (website, shop, invoice, app, etc.).

## Boundary

`Merchant → Brand → Source System → Payment`

RemotePay owns the payment identity and fee/transaction boundaries. The merchant remains responsible for its business, products, customers and fulfillment.

## Required onboarding identity

- `merchant_id`
- legal/business name
- one or more `brand_id`s
- approved source systems
- server-side pricing configuration
- payout/settlement configuration

## Production onboarding gates

The current service is an identity foundation only. Before a merchant can process live money, production onboarding must add:

1. KYB/KYC and beneficial-owner verification where required.
2. Terms and merchant agreement acceptance.
3. Settlement account verification.
4. Risk/compliance status.
5. Approved pricing profile.
6. Webhook/provider capability configuration.
7. API credentials scoped to the merchant.
8. Audit trail for onboarding decisions.

No merchant should bypass these controls by directly supplying a `merchant_id` or `brand_id` to the payment-link endpoint.

## Ecosystem use

The same model supports C6 Group, Ubernie, and future external clients without creating a separate payment implementation for each business.
