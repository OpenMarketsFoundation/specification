# Repository Guidance

This repository contains implementation-sensitive protocol text. Treat the current specification as already implemented by real applications.

## Core Rule

Do not change the meaning of current specification material during structural refactors.

Preserve:

- event kind numbers
- tag names and tag ordering where shown in examples
- tag array shapes
- JSON payload shapes
- field names
- required/optional semantics
- status and type values
- examples
- MUST, SHOULD, and MAY language
- links to upstream specs and prior work

## Current Compatibility Snapshot

[SPEC.md](SPEC.md) is the contiguous current specification. It was copied from the pre-refactor root README and should remain available for implementers who need the old single-document shape.

If split docs disagree with [SPEC.md](SPEC.md), treat [SPEC.md](SPEC.md) as the compatibility source for the current protocol.

## Structural Refactors

Structural PRs may:

- move or copy text unchanged
- add navigation
- add compatibility notes
- add history and acknowledgments
- add clearly marked explanatory material
- add clearly marked proposal workspaces

Structural PRs must not:

- invent new Nostr kinds
- rename existing tags
- rewrite examples
- change payment, order, delivery, listing, review, or merchant-preference semantics
- make escrow mandatory
- make any marketplace a required custodian of funds
- collapse external proposals into this spec as if they are already canonical

## Normative Labels

Use explicit labels:

- Normative: current spec material or future accepted protocol requirements.
- Explanatory: reader guidance that does not redefine protocol behavior.
- Historical: prior work and acknowledgments.
- Experimental: active proposals, design space, or integration notes.

## Agent Notes

Before editing, inventory kind numbers, tag names, examples, and normative keywords in affected sections. After editing, compare them again. Prefer exact copies over paraphrases when transposing current spec text.
