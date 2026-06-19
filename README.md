# Open Markets Specification

Open Markets is a specification workspace for decentralized marketplaces on Nostr.

This repository currently preserves the existing e-commerce marketplace protocol exactly while reorganizing it into clearer navigation paths for future work. The refactor is a transposition, not a recomposition: existing event kinds, tag shapes, payload structures, examples, and normative requirements remain unchanged.

## Current Spec

- [SPEC.md](SPEC.md) is the contiguous compatibility snapshot of the current specification.
- [docs/compatibility.md](docs/compatibility.md) lists the invariants this repository must preserve.
- [docs/architecture.md](docs/architecture.md) maps the current spec into the four organizational pillars.
- [lanes/ecommerce.md](lanes/ecommerce.md) preserves the current e-commerce lane as the first fully expressed market lane.

## Pillars

The repo is organized around four broad homes for current and future Open Markets work:

- [Items](pillars/items.md): listings, collections, drafts, reviews, metadata, discovery, categorization, and pricing.
- [Orders](pillars/orders.md): buyer/seller intent, order creation, communication, status, cancellation, and receipts.
- [Payments](pillars/payments.md): merchant preferences, payment requests, payment proofs, invoices, receipts, and future payment rails.
- [Delivery](pillars/delivery.md): shipping options, pickup, shipping updates, digital delivery, services, rides, lodging, and fulfillment.

Only the current e-commerce material is normative today. Future market lanes can be added without changing current behavior.

## Normative Status

- Normative: [SPEC.md](SPEC.md) and copied current-spec sections in the pillar and lane files.
- Explanatory: docs under [docs/](docs/) unless explicitly marked otherwise.
- Historical: [docs/history.md](docs/history.md).
- Experimental/proposal: [proposals/](proposals/).

When there is any ambiguity, [SPEC.md](SPEC.md) controls for current compatibility.

## Prior Work

This repository builds on and preserves links to the current Nostr commerce design space:

- [Gamma Markets market-spec](https://github.com/GammaMarkets/market-spec)
- [NIP-99 classified listings](https://github.com/nostr-protocol/nips/blob/master/99.md)
- [NIP-15 marketplace](https://github.com/nostr-protocol/nips/blob/master/15.md)
- [nostr-commerce-skill](https://github.com/welliv/nostr-commerce-skill)
- [Colabonate NIP-115 draft](https://github.com/Colabonate/nips/blob/colabonate-freedom-protocol/115.md)
- [nostr-protocol/nips PR 2323](https://github.com/nostr-protocol/nips/pull/2323)
- [Pontmore PIP-00 agent definition](https://github.com/pontmore/protocol/blob/main/PIP-00-agent-definition.md)
- [Switchboard escrow architecture](https://github.com/samuelralak/switchboard/blob/master/docs/escrow-architecture.md)

## Contributing

Read [AGENTS.md](AGENTS.md) before making structural or semantic changes. Structural PRs should preserve implementation-sensitive text and keep semantic changes in separate, explicit proposals.
