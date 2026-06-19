# Terminology

Status: explanatory reader aid.

This page helps readers navigate the repository. It does not redefine protocol behavior. If a definition here conflicts with [../SPEC.md](../SPEC.md), [../SPEC.md](../SPEC.md) controls.

## Pillars

- Items: what is being offered, listed, updated, discovered, categorized, priced, reviewed, or collected.
- Orders: buyer/seller intent and communication around order creation, status, cancellation, and order-linked messages.
- Payments: payment preferences, payment requests, invoices, proofs, receipts, payment services, and future payment rails.
- Delivery: shipping, pickup, physical delivery, digital delivery, ride or service fulfillment, lodging fulfillment, milestones, and completion signals.

## Lanes

A lane is a market-specific flow that uses the shared pillars.

The current fully expressed lane is e-commerce. Future lanes might include ride-sharing, room-sharing, restaurant delivery, real estate listings, job postings, service marketplaces, digital goods, and other open-market flows. Those future lanes are not normative until explicitly specified.

## Status Labels

- Normative: current protocol requirements and future accepted requirements.
- Explanatory: guidance for readers and implementers that does not change requirements.
- Historical: prior work, acknowledgments, and source lineage.
- Experimental: proposals, design space, and integration notes.

## Current Coordination Point

[NIP-99](https://github.com/nostr-protocol/nips/blob/master/99.md) is the current coordination point for listing primitives in the Open Markets design space. Open Markets organizes interoperable flows above that base primitive while preserving current e-commerce compatibility.
