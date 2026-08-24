# RemotePay Provider Architecture

**Status:** foundation

RemotePay owns the merchant-facing contract. Payment processors are isolated behind provider adapters.

## Boundary

`RemotePay API → provider registry → provider adapter → processor`

Provider adapters expose only the capabilities RemotePay needs:

- create payment
- retrieve payment
- refund payment

The adapter normalizes provider-specific IDs, checkout URLs, statuses and raw response metadata into the RemotePay provider contract.

## Why this matters

C6 Group, Ubernie and external merchants integrate with RemotePay once. They do not integrate directly with the underlying processor.

That means the current processor can be replaced, supplemented, or eventually bypassed by a native RemotePay processing rail without changing merchant-facing integrations.

## Production rules

- Never expose provider credentials to merchants or brands.
- Keep provider-specific payloads inside adapters.
- Persist provider IDs alongside RemotePay transaction IDs.
- Normalize provider webhook events before they enter the RemotePay economic-event pipeline.
- Do not treat the adapter boundary as evidence that RemotePay itself is a licensed/acquiring/payment-processing rail; regulatory and banking requirements remain separate production gates.
