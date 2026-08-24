# RemotePay Production Verification Gate

**Status:** foundation verification suite added; live production approval remains separate.

## Verified architecture contracts

- Merchant/brand identity boundary exists.
- Commercial pricing profiles are server-side and versionable.
- Provider integrations are isolated behind an adapter boundary.
- Transaction lifecycle rejects invalid state transitions.
- Settlement arithmetic reconciles gross, processor fees, RemotePay fees and adjustments into merchant net.
- A combined foundation test exercises pricing → provider → lifecycle → settlement.

## Required before live-money launch

The foundation suite is not a claim that the production payment gateway is ready for unrestricted live traffic. The final launch gate must additionally verify:

1. Real provider sandbox payment creation.
2. Real provider webhook signature verification.
3. Idempotent webhook/event handling.
4. Persistent transaction and economic-event ledger.
5. Persistent settlement batches and provider reconciliation.
6. Merchant pricing-profile assignment and effective-version capture.
7. Refund/chargeback/dispute handling.
8. Authentication, authorization, rate limits and audit logging.
9. Secret management and environment separation.
10. End-to-end staging transaction using the actual merchant-facing API.
11. Operational monitoring, alerts and failure recovery.
12. Regulatory, banking, acquiring and contractual approvals applicable to the operating model.

## Launch principle

Do not interpret passing deterministic unit/foundation tests as authorization to move real money. Production launch occurs only when the operational, provider, security, financial-control and regulatory gates above have evidence attached.
