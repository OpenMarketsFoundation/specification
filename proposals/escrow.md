# Escrow, Arbitration, and Agent Proposals

Status: experimental reference workspace.

This page creates room for checkout, escrow, arbitration, dispute, and agent-related work without making any design canonical in the current Open Markets specification.

## Current Status

Escrow is not mandatory in the current Open Markets spec.

This repository does not currently decide:

- whether escrow should be merchant-run, third-party, federated, ecash-based, Lightning-based, on-chain, fiat-based, or hybrid
- whether escrow state should be public, private, encrypted, revealable, or projected from private receipts
- whether a marketplace should ever be a custodian of funds
- which arbiter discovery mechanism is preferred
- which payment proof tag shape should be canonical for escrow
- whether checkout state should extend current `kind:16` messages or use new public events

## Exact References

- [Colabonate NIP-115 draft](https://github.com/Colabonate/nips/blob/colabonate-freedom-protocol/115.md)
- [nostr-protocol/nips PR 2323](https://github.com/nostr-protocol/nips/pull/2323)
- [Pontmore PIP-00 agent definition](https://github.com/pontmore/protocol/blob/main/PIP-00-agent-definition.md)
- [Switchboard escrow architecture](https://github.com/samuelralak/switchboard/blob/master/docs/escrow-architecture.md)

## Open Design Direction

A possible future architecture may explore:

1. Merchant runs marketplace-standard escrow mint, register, or software.
2. Buyer receives a signed order receipt locally.
3. Merchant receives order details.
4. Marketplace may receive only a minimal hash, commitment, or verification ping.
5. If there is no dispute, marketplace never learns full transaction details.
6. If a dispute arises, either party reveals the receipt packet and supporting evidence to the marketplace or arbiter.

This is context only. It is not a current normative requirement.

## Contribution Guidance

Future escrow or arbitration proposals should:

- reference existing work exactly
- state whether they are compatible with current encrypted order messages
- state whether they require new event kinds
- state whether they require public checkout state
- state what information is revealed to marketplaces, arbiters, relays, and counterparties
- state how existing e-commerce implementations remain compatible
- avoid making escrow mandatory unless a future accepted spec explicitly does so
