# Open Markets Specification Refactor Plan

Status: planning document for a structural reorganization PR.

This plan describes how to make the repository easier to navigate, easier to contribute to, and easier to extend while preserving full backward compatibility with the current specification. The refactor is a transposition, not a recomposition.

## 1. Current Repo Audit

Current structure:

```text
/
  README.md
  LICENSE
```

Current state:

- The current root `README.md` is byte-identical to `GammaMarkets/market-spec` `spec.md`.
- The repo has no separate compatibility, history, contribution, examples, or proposal workspace documents.
- The existing specification is framed primarily as a full-featured e-commerce framework.
- The current e-commerce lane is the only fully expressed lane and must remain clear.

Current implementation-sensitive surface:

- Event kinds: `30402`, `30405`, `30406`, `14`, `16`, `17`, `31555`, `31989`, `31990`, kind `0`, and kind `10019` references.
- Tags and fields include `d`, `title`, `price`, `type`, `visibility`, `stock`, `summary`, `spec`, `image`, `weight`, `dim`, `location`, `g`, `t`, `a`, `shipping_option`, `p`, `subject`, `order`, `amount`, `item`, `shipping`, `address`, `email`, `phone`, `payment`, `expiration`, `status`, `tracking`, `carrier`, `eta`, `rating`, and `payment_preference`.
- Required/optional language, status values, payment preference values, and JSON examples are implementation-sensitive.

Known gaps to note but not fix in this PR:

- Relative NIP links such as `17.md`, `51.md`, `89.md`, and `10.md` are inherited from the current text.
- Some notes are numbered inconsistently.
- Minor grammar and typo issues exist.
- History includes an `expires` commit note while current text uses `expiration`.
- There is no current distinction between normative, explanatory, historical, and experimental material.

## 2. Prior Art Summary

Reference these exactly. Do not absorb or rewrite their specs.

| Reference | Role | Contribution | Reorganized location |
| --- | --- | --- | --- |
| [Gamma Markets market-spec](https://github.com/GammaMarkets/market-spec) | Normative ancestor/current source | Provides the current e-commerce marketplace spec text preserved in this repository. | `docs/history.md`, `docs/compatibility.md`, `SPEC.md` |
| [NIP-99 classified listings](https://github.com/nostr-protocol/nips/blob/master/99.md) | Current upstream coordination point | Provides the current base listing primitive for Nostr commerce coordination. | `README.md`, `docs/architecture.md`, `pillars/items.md` |
| [NIP-15 marketplace](https://github.com/nostr-protocol/nips/blob/master/15.md) | Historical | Important earlier marketplace work in the Nostr commerce design space. | `docs/history.md` |
| [nostr-commerce-skill](https://github.com/welliv/nostr-commerce-skill) | Informational / agent-friendly reference | Shows scenario-oriented commerce modeling useful for docs and agent workflows. | `docs/architecture.md`, `examples/README.md`, `AGENTS.md` |
| [Colabonate NIP-115 draft](https://github.com/Colabonate/nips/blob/colabonate-freedom-protocol/115.md) | Experimental proposal | Active checkout, escrow, and dispute design work. | `proposals/escrow.md` |
| [nostr-protocol/nips PR 2323](https://github.com/nostr-protocol/nips/pull/2323) | Active RFC context | Discussion context for on-graph checkout, escrow, and disputes. | `proposals/escrow.md` |
| [Pontmore PIP-00 agent definition](https://github.com/pontmore/protocol/blob/main/PIP-00-agent-definition.md) | Experimental / informational | Agent definition work that may inform future agent discovery or service coordination. | `proposals/escrow.md`, future proposals |
| [Switchboard escrow architecture](https://github.com/samuelralak/switchboard/blob/master/docs/escrow-architecture.md) | Implementation / informational | Escrow architecture reference for future integration notes. | `proposals/escrow.md` |

The repo should acknowledge contributors including Gamma Markets, NIP-15 authors, Shopstr, Plebeian, Conduit, Colabonate, Switchboard, and related Nostr commerce builders without presenting this refactor as replacing their work.

## 3. Proposed Information Architecture

Use a small file-based structure:

```text
/
  README.md
  SPEC.md
  AGENTS.md
  docs/
    refactor-plan.md
    history.md
    compatibility.md
    terminology.md
    architecture.md
  pillars/
    items.md
    orders.md
    payments.md
    delivery.md
  lanes/
    ecommerce.md
  examples/
    README.md
  proposals/
    escrow.md
```

Purpose:

- `README.md`: map, compatibility promise, status legend, and exact external links.
- `SPEC.md`: byte-identical current spec snapshot.
- `AGENTS.md`: contributor and agent guardrails.
- `docs/`: explanatory, historical, compatibility, and planning docs.
- `pillars/`: broad homes for current material and future extensions.
- `lanes/`: market-specific lanes, with e-commerce as the first fully expressed lane.
- `examples/`: future runnable or copyable examples without changing the spec.
- `proposals/`: experimental references and proposal workspaces.

## 4. Migration / Transposition Strategy

Every moved/copied section must preserve meaning. Current text can be copied unchanged into split views while `SPEC.md` preserves the original contiguous document.

| Current section | Proposed location | Strategy |
| --- | --- | --- |
| `Protocol Requirements` | `lanes/ecommerce.md` | Copy unchanged. |
| `Core Protocol Components` | `docs/architecture.md` | Copy unchanged and add non-normative pillar navigation. |
| `Merchant Preferences` | `pillars/payments.md` and `docs/architecture.md` | Copy unchanged. |
| `Product Listing` | `pillars/items.md` | Copy unchanged. |
| `Product Collection` | `pillars/items.md` | Copy unchanged. |
| `Drafts` | `pillars/items.md` | Copy unchanged. |
| `Shipping Option` | `pillars/delivery.md` | Copy unchanged. |
| `Order Communication Flow and Payment Processing` intro | `pillars/orders.md` | Copy unchanged for context. |
| `Order Creation` | `pillars/orders.md` | Copy unchanged. |
| `Payment Request` | `pillars/payments.md` | Copy unchanged. |
| `Order Status Updates` | `pillars/orders.md` | Copy unchanged. |
| `Shipping Updates` | `pillars/delivery.md` | Copy unchanged. |
| `General Communication` | `pillars/orders.md` | Copy unchanged. |
| `Payment Receipt` | `pillars/payments.md` | Copy unchanged. |
| `Product Reviews` | `pillars/items.md` | Copy unchanged. |
| `Implementation Guidelines` payment material | `pillars/payments.md` | Copy unchanged. |

Safe now:

- Move/copy text unchanged.
- Add navigation and cross-links.
- Add source links, compatibility notes, history, and proposal workspaces.
- Label sections as normative, explanatory, historical, or experimental.

Defer:

- New event kinds.
- Escrow semantics.
- Payment tag redesign.
- Order receipt redesign.
- NIP-99 recomposition.
- Generic market abstractions that change current e-commerce behavior.
- Any wording change that alters MUST, SHOULD, or MAY meaning.

## 5. Backward Compatibility Strategy

The PR should preserve:

- event kind numbers
- tag names
- tag ordering in examples
- field names
- JSON shapes
- required and optional semantics
- payment preference values
- order `type` values
- order and shipping `status` values
- payment proof shapes
- current examples
- upstream links
- NIP-99 expectations
- current e-commerce flow wording

Validation checks:

- `SPEC.md` must match the pre-refactor `README.md`.
- Inventory kind numbers before and after.
- Inventory tag names before and after.
- Inventory normative keywords before and after.
- Review all copied code fences against `SPEC.md`.
- Confirm escrow remains proposal-only.

## 6. Normative vs Non-Normative Strategy

Normative:

- `SPEC.md`
- copied current spec sections in `pillars/` and `lanes/`

Explanatory:

- `docs/architecture.md` navigation text
- `docs/terminology.md`
- `examples/README.md`

Historical:

- `docs/history.md`

Experimental:

- `proposals/escrow.md`
- future proposal documents

Future proposals may become normative only through explicit PRs that identify compatibility impact and migration requirements.

## 7. Specific PR Implementation Plan

Commit 1: repo map and agent guidance.

- Add `docs/refactor-plan.md`.
- Add `AGENTS.md`.
- Compatibility note: planning and guardrails only.

Commit 2: compatibility snapshot.

- Add `SPEC.md` as a byte-identical copy of the current `README.md`.
- Compatibility note: current spec remains available in one file.

Commit 3: history and compatibility docs.

- Add `docs/history.md`, `docs/compatibility.md`, `docs/terminology.md`, and `docs/architecture.md`.
- Compatibility note: explanatory only.

Commit 4: pillar and lane transposition.

- Add `pillars/items.md`, `pillars/orders.md`, `pillars/payments.md`, `pillars/delivery.md`, and `lanes/ecommerce.md`.
- Compatibility note: copied current spec text, no semantic changes.

Commit 5: examples and proposal workspace.

- Add `examples/README.md` and `proposals/escrow.md`.
- Compatibility note: examples are future workspace; escrow remains optional and experimental.

Commit 6: root README cleanup.

- Replace root README with navigation, compatibility, status legend, and exact references.
- Compatibility note: root README points to `SPEC.md` instead of redefining protocol.

## 8. Open Questions

These are explicitly out of scope for the structural refactor:

- Whether new kinds are needed for checkout, payment status, escrow, disputes, or delivery milestones.
- Whether current NIP-99 structures are sufficient for non-e-commerce lanes.
- Whether order receipt shape should remain private, public, hybrid, or revealable only during disputes.
- How payment status events should be represented, if at all.
- How escrow/arbitration services should be discovered.
- How privacy-preserving dispute disclosure should work.
- How fiat and external payments should be referenced.
- How much lane-specific material belongs in the base spec.
- How outside contributors should upstream their proposals.

## 9. Risks

- Accidentally changing spec meaning during reorganization.
- Breaking apps that already implement the current spec.
- Overcomplicating the repo.
- Prematurely standardizing escrow.
- Alienating prior contributors.
- Making e-commerce harder to implement while trying to generalize.
- Inventing new events unnecessarily.
- Creating too many folders.
- Making the spec hostile to implementers or agents.
- Misrepresenting external specs through paraphrase.

## 10. Acceptance Criteria

The refactor is successful when:

- Existing apps remain compatible.
- Current implementation-sensitive details are preserved.
- NIP-99 remains the base listing primitive.
- Current NIP-99 standards are referenced exactly.
- E-commerce still works clearly.
- Non-e-commerce market flows have obvious future homes.
- Payments are organized in a payment-agnostic way without changing current payment behavior.
- Escrow has a place without being prematurely finalized.
- Delivery is broad enough for physical goods, digital goods, services, rides, lodging, and fulfillment.
- History is acknowledged respectfully.
- External proposals are linked exactly and given room to develop.
- The repo is easier for humans and agents to navigate.
- Implementers can tell which parts are normative, explanatory, historical, and experimental.
- The PR is a transposition, not a recomposition.
