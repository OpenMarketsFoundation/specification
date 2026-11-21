# Escrow, Dispute, and Public Checkout State

Status: experimental proposal. This page is not current normative Open Markets text.

This proposal fills the escrow, arbitration, dispute and checkout workspace with a concrete design: a **non-custodial, opt-in trust layer** that sits on top of the current NIP-99 listing and NIP-17 order communication, without changing either. It defines how a trade that needs more than reputation gets a hold, how a disagreement is escalated and resolved by a community arbitrator, what each party can see at each step, and how the outcome is settled and provable. Escrow is **never mandatory**: the ordinary path stays a direct buyer-to-seller payment, and the layer below only activates when both sides opt in. No marketplace or client ever becomes a custodian of funds. The proposal also introduces the **public settlement skeleton** — an addressable, publicly auditable checkout state that complements, and does not replace, the encrypted kind `16`/`17` order messages — because the current encrypted channel alone cannot give a third party (an arbitrator, an indexer, a reputation service) anything to verify. Kind allocation is deliberately **not** claimed in this proposal: the numbers are listed with their current claimants so that allocation can be agreed jointly.

## Public sources and kind allocation

- [NIP-01 addressable events, tags, filters, and replacement](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [NIP-17 encrypted private direct messages](https://github.com/nostr-protocol/nips/blob/master/17.md)
- [NIP-44 encrypted payloads](https://github.com/nostr-protocol/nips/blob/master/44.md)
- [NIP-57 lightning zaps](https://github.com/nostr-protocol/nips/blob/master/57.md)
- [NIP-99 classified listings](https://github.com/nostr-protocol/nips/blob/master/99.md)
- [NIP-115 draft — on-graph checkout layer for NIP-99 markets](https://github.com/Colabonate/nips/blob/colabonate-freedom-protocol/115.md)
- [nostr-protocol/nips PR 2323 — the same draft, as an RFC on the Nostr list](https://github.com/nostr-protocol/nips/pull/2323)
- [Colabonate Protocol Specification](https://github.com/Colabonate/Colabonate_Protocol)
- [Current Open Markets compatibility snapshot](../SPEC.md)
- [Nostr kind registry](https://github.com/nostr-protocol/registry-of-kinds/blob/master/schema.yaml)

**This proposal claims no new event kinds.** The trust layer needs two addressable records (a checkout state and a dispute record) plus a verdict record, but the numbers are deliberately left unallocated so they can be agreed jointly rather than taken unilaterally. The currently claimed numbers, as far as we can observe them, are:

| Number | Claimed by | Meaning today |
|---|---|---|
| `30402` | Open Markets | Product listing (normative) |
| `30405` | Open Markets | Product collection (normative) |
| `30406` | Open Markets | Shipping option (normative) |
| `14`, `16`, `17` | Open Markets | Regular communication, order processing, payment receipt (normative) |
| `31555` | Open Markets | Product review (normative) |
| `31989`, `31990` | Open Markets | Merchant application recommendation and handler |
| `1331` | bookings proposal | Private time-based booking rumor |
| `2047` | offer-code-commitments proposal | Opaque offer-code commitment |
| `30078` | commerce-settings proposal | Portable commerce settings document |
| `30409`, `30410`, `3841` | event-commerce proposal | Event market, occurrence assignment, agent identity |
| `30017`–`30027`, `30410`, `30411`, `30414`, `30415`, `30420`–`30423`, `31416`–`31424`, `31922`–`31925` | Colabonate Protocol Specification | Legacy and adopted kinds; see the note below |

Two collisions are worth naming explicitly, because they are the reason kind allocation has to be a joint decision rather than a unilateral one:

- **`30410`** is claimed by the event-commerce proposal as an occurrence-assignment record, and by the Colabonate specification as the dual-publishing target for the verification credential (`30021`). These are different meanings for the same number. Colabonate moved its credential and review events off `30405` and `30406` precisely because those two belong to Open Markets; the same reasoning now applies to `30410`.
- **`30409`** is claimed by the event-commerce proposal and appears in the Colabonate specification as the dual-publishing target of the dispute-opened event (`30020`).

We are not proposing to resolve either of these unilaterally. We are proposing that the workspace agree one allocation table, and offering ours as input.

## Scope and coordinates

```text
listing   = 30402:<merchant-pubkey>:<listing-d>
order     = 16 (NIP-17, encrypted, addressed to the merchant's listing key)
receipt   = 17 (NIP-17, encrypted, addressed to the buyer)

checkout  = <checkout-kind>:<buyer-pubkey>:<checkout-d>     // public settlement skeleton
dispute   = <dispute-kind>:<opening-pubkey>:<dispute-d>     // public, neutral claim
verdict   = <verdict-kind>:<arbitrator-pubkey>:<verdict-d>  // public, per-arbitrator
hold      = <hold-kind>:<escrow-provider-pubkey>:<hold-d>    // provider-run, non-custodial
```

A checkout state is written by the party that performed the step, and is addressed to the buyer so that both parties can index the same record. A dispute record is written by whichever party escalates it and is addressed to the order it belongs to. A verdict is written by one arbitrator and carries that arbitrator's identity; the set of verdicts is what resolves the dispute, not any single one of them.

## Answers to the open questions in this workspace

This section answers the questions listed in [the escrow workspace](https://github.com/OpenMarketsFoundation/specification/blob/codex/spec-refactor-transposition/proposals/escrow.md), each with the reasoning and the production experience behind it.

### Which escrow rail — merchant-run, third-party, federated, ecash-based, Lightning-based, on-chain, fiat-based, or hybrid?

**Neither the marketplace nor a third party, by default.** The default path is a direct buyer-to-seller payment in which no one holds funds at all. When a trade needs a hold, both parties opt in to an escrow that is **run by the merchant or by a provider the merchant names**, and it is **non-custodial with respect to the parties' keys**: the hold mechanism cannot spend the buyer's funds without the buyer's signature, and cannot release them to the seller without a preimage that only the seller can produce.

Concretely, three rails are viable and should be allowed:

| Rail | Mechanism | Property |
|---|---|---|
| Lightning hold invoice | The payment is held by the Lightning node and released against a preimage | Requires a node operator that can hold funds — a custody question the spec must answer explicitly, which is why it is opt-in and provider-scoped |
| Cashu mint | The buyer pays the mint; the mint holds the token until redemption | Custodial at the mint, but the mint is a named third party, not the marketplace |
| Native-Bitcoin escrow canister | A t-ECDSA contract holds the funds and enforces a release condition | Non-custodial at the protocol level; requires a chain the whole ecosystem already accepts |

A hybrid is fine as long as the *custody boundary* is named. What is not acceptable is a marketplace becoming a custodian by default, because that is the property the whole design exists to avoid.

### Should escrow state be public, private, encrypted, revealable, or projected from private receipts?

**Public settlement skeleton, private payload.** The state of a trade is split:

- A **public, addressable settlement skeleton** records what happened, in terms anyone can verify: that an order exists, that it was accepted, that a payment was made, that delivery was confirmed, that a dispute was opened, that a verdict was published. It carries no order content.
- A **commercial payload** carries the actual details — amounts, addresses, terms, delivery notes — and is encrypted to the parties, or withheld.
- The two are linked by a **commitment**: the payload's hash is published in the skeleton. A party that disputes can be asked to open the payload to an arbitrator, who can check it against the published hash.

This gives three properties at once: the history is publicly auditable by any third party; the commercial detail is not broadcast; and the disclosure is verifiable, so a party cannot produce a different payload after the fact.

### Should a marketplace ever be a custodian of funds?

**No.** The buyer pays the seller. If a marketplace-mediated flow ever needs the marketplace to see order content, that must be a separate, explicitly consented mode with its own disclosure rules — it is not the default and it is not a custody arrangement.

We should be precise here, because "we do not hold funds" and "we see who bought what" are different claims. Our own implementation currently has an inbound-orders design under evaluation in which a server-side marketplace flow would see the buyer's contact details. That is a **privacy** cost, not a custody cost, and it should be specified as its own mode with its own rules rather than smuggled in as an implementation detail.

### Which arbiter discovery mechanism is preferred?

**Publish the arbitrators.** An arbitrator is a participant with a role, and roles should be discoverable the way the rest of the ecosystem is: an arbitrator publishes a credential and a DAO or community publishes its membership. A dispute record names the arbitration body that will handle it, and the body's membership record names its arbitrators. Two mechanisms coexist and should be allowed to coexist:

- **DAO-appointed arbitration**: arbitrators are elected or appointed by a community body and their membership is published; a verdict is binding for that community's disputes.
- **Opt-in third-party arbitration**: a party may name an external arbitrator service up front, in the order, before any dispute exists.

Both are needed. A dispute between strangers who share no community has no natural arbitrator; a dispute inside a community should not need to pay a stranger.

### Which payment proof tag shape should be canonical for escrow?

**The current Open Markets shape.** The receipt tag is `["payment", "<medium>", "<medium-reference>", "<proof>"]`, and it is already deployed across implementations. It separates *which rail* from *the proof for that rail*, which is exactly what an escrow needs: the escrow layer must not care whether the proof is a Lightning preimage, a Cashu token, a transaction id or a fiat gateway reference.

We had proposed a five-element variant that folded the amount into the tag. That was a mistake, and we are withdrawing it in favour of the current shape: the amount already has its own tag, and duplicating it in the proof tag invites two sources of truth that can disagree.

One correction we want to flag, because it will bite implementers: a listing is an **addressable** event, so a zap or receipt that references it should use an `a` tag (`30402:<pubkey>:<d>`), not an `e` tag with the event id. A client that matches only on `e` will never mark an addressable listing as sold, because the reference it expects is not the one that exists. This is worth stating in the current spec, not only in an escrow extension.

### Whether checkout state should extend current kind `16` messages or use new public events?

**New public events, complementing kind `16`.** Kind `16` is a NIP-17 encrypted message, so its content is not publicly readable and not publicly indexable. A dispute arbiter who is not a party cannot read it; a marketplace cannot index it; a reputation service cannot compute anything from it without each party's cooperation. The current message model has no notion of a state that anybody can verify.

That is not a criticism of the current design — encrypted order communication is exactly right for the commercial content — it is an argument that the *state* belongs in public events and the *content* belongs in the encrypted messages. Both exist in the same order; they reference each other.

## Compatibility with the current specification

This section answers the contribution guidance for this workspace point by point.

1. **Existing work is referenced exactly.** The prior art is cited above by URL: the NIP-115 draft and its RFC on the Nostr list, the Colabonate Protocol Specification, and this workspace's own escrow page. Nothing here is presented as new prior art.
2. **Compatibility with the encrypted order messages.** Full compatibility. The layer reads kind `16` and kind `17` as they are; it adds public records alongside them and never changes their shape, their tags, or their MUST-level requirements. A client that implements only the current specification keeps working unchanged.
3. **New event kinds required.** Yes — three addressable records (checkout state, dispute, verdict) and one provider-run hold record. **No numbers are claimed in this proposal**; the allocation table above is offered as the starting point for a joint decision.
4. **Public checkout state required.** Yes, for the reasons given above: a verifiable public state is the substance of the trust layer, and it cannot be projected from private receipts because a party must be able to withhold disclosure without being able to erase the record that it did.
5. **What is revealed to marketplaces, arbiters, relays and counterparties.** Set out in the disclosure matrix below. In summary: relays and the public see the skeleton and the verdicts; the escrow provider sees the amount it holds; the arbitrator sees the payload of the disputed order only, and only after a dispute exists; the marketplace sees the skeleton and nothing else unless a party has separately consented to an inbound-orders mode.
6. **How existing e-commerce implementations remain compatible.** By addition only. No current kind changes number, shape, tag order or semantics. No current MUST, SHOULD or MAY requirement changes. The `SPEC.md` compatibility snapshot stays authoritative for the current protocol, exactly as the workspace intends.
7. **Escrow is not mandatory.** The direct buyer-to-seller payment remains the default and the recommended path for the overwhelming majority of trades. The hold activates only when both parties opt in, and the specification never asks a marketplace to be a custodian of funds.

## The trust layer

### Direct-Pay is the default

A trade that both parties accept on terms is settled by the buyer paying the seller's own invoice. No escrow, no intermediary, no custody, no fees beyond the network fee. This is the path the specification should keep pointing at, and the trust layer below is an option for the trades that need one — high-value goods, first-time counterparties, deliveries with a long gap between payment and handover, or a capacity-limited reservation.

The protection that replaces escrow is **reputation**, and it only works if reputation is computed from public events. Which is the next section.

### The public settlement skeleton

A checkout state is an addressable event. It records the state of one trade and nothing else:

```text
["d", "<checkout-id>"]
["order", "<order-identifier>"]
["status", "<state>"]
["prev", "<signed-checkout-id>"]      // on an update; absent on the first
["amount", "<amount-in-sats>"]
["payment", "<medium>", "<medium-reference>", "<proof>"]   // optional, when paid
```

The states are the ones a trade actually has:

```text
PENDING → ACCEPTED → PAID → IN_PROGRESS → COMPLETED
                     ↘ CANCELLED
         ↘ DISPUTED → RESOLVED
```

The `prev` tag makes the record a chain: each state names the state it replaced, so a client can detect a fork, a replay, or a state that was skipped. Every transition is signed by the party that performed it, and the permitted transitions per role are fixed: only the seller may accept, only the buyer may mark paid or confirm completion, either party may cancel before delivery, either party may open a dispute.

Public state and reputation are the same mechanism used twice: a completed trade produces a public record, and the record produces a reputation signal that no single party controls.

### An optional, non-custodial hold

When both parties opt in, the buyer's payment is held rather than paid out. The hold has one job: it makes the payment **conditional on a condition the parties already agree on**, and it makes the dispute path meaningful, because without a hold a "dispute" over a direct payment has nothing to redistribute.

The properties any hold mechanism must satisfy, whichever rail it uses:

- The provider cannot take the funds. It can hold them and release them per the stated condition, but it cannot move them to itself.
- The condition is enforced mechanically, not by the provider's discretion.
- The parties can exit: an expiry that returns the funds to the buyer without any third party's decision.
- The provider is named in the order, before any money moves.

An escrow provider is a participant like any other, and the same rules that make a marketplace an unsuitable custodian make an unnamed provider an unsuitable one.

### Dispute escalation

Three levels, each with a deadline and a deterministic next step:

| Level | Deadline | Who | Outcome |
|---|---|---|---|
| 1 — self-service | 7 days | The two parties | Direct negotiation; either side may settle or escalate |
| 2 — mediation | 14 days | A community-selected mediator | The mediator proposes a settlement; both parties may accept or refuse |
| 3 — arbitration | 24–48h | The named arbitration body | Binding verdict, published |

A dispute record is public and neutral: it names the order, the reason, the level and the deadline, and it does not narrate either side's case. The reason is a small closed vocabulary (`non_delivery`, `quality`, `non_payment`, `terms_violation`, `other`).

The deadlines are load-bearing. Without a deadline, a dispute is a negotiation the loser controls.

### Verdict outcomes: release, cancel, split

A verdict has one of three outcomes:

```text
RELEASE  → the held amount goes to the seller
CANCEL   → the held amount returns to the buyer
SPLIT    → the held amount is divided, by basis points, between the two
```

The split form should carry the two shares explicitly:

```text
["settlement", "<buyer-bps>", "<seller-bps>"]
```

`RELEASE` and `CANCEL` are the two extremes of the same primitive. A split is the general case, and it is what a partial fault looks like: the buyer paid for a service that was partly delivered, the seller delivered partly. Modelling only release and cancel forces a binary judgement that the underlying facts frequently do not support.

### The dispute timeout

If no verdict arrives before the dispute deadline, the default is **an automatic split**, not a silent release or a silent refund. We recommend the even split as the default because it is the only outcome that does not reward either party for being the one who waited, and it does not require the arbiter to have been reachable.

This is the same proposal that was raised in the marketplace signal group, and it is worth stating why it is right rather than merely familiar: a timeout with a binary default creates an incentive to stall the process, and a timeout with no default means the trade is frozen indefinitely. An even split on timeout is neutral between the parties and terminates the trade.

We are aware this makes the even split a consequential default rather than a rare case, and it should be a considered, explicitly stated position of this workspace.

### Arbiter discovery

An arbitrator is a role, and roles are published:

- A participant publishes an **arbitrator credential** identifying themselves.
- A community or DAO publishes a **membership** record naming its arbitrators.
- A dispute record names the **arbitration body** responsible for it.

Verdicts are published per arbitrator, and the resolution is derived from the set of published verdicts. A dissenting verdict is retained and readable. That matters: a published set of verdicts lets anyone check the outcome, not just the parties.

## Disclosure matrix

| Actor | Sees the public skeleton | Sees the commercial payload | Sees the hold amount |
|---|---|---|---|
| Any relay observer | Yes | No | No |
| The buyer | Yes | Yes | Yes |
| The seller | Yes | Yes | Yes |
| The escrow provider | The skeleton | The order it holds | Yes |
| The arbitrator | The skeleton, **after** a dispute is opened | The disputed order only, on disclosure | The held amount |
| The marketplace | The skeleton | No, unless the buyer has separately consented to an inbound-orders mode | No |

## What this proposal does not do

- It does not make escrow mandatory, and it does not change the direct-payment default.
- It does not make any marketplace a custodian of funds.
- It does not change any current kind, tag, example or MUST-level requirement.
- It does not claim a kind number.
- It does not propose a new order envelope, a new payment proof shape, or a new listing vocabulary.
- It does not require the public skeleton to carry any commercial detail.
- It does not define an arbiter election model; it defines how arbitrators are **discovered** once appointed.

## Prior work

- [NIP-115 draft — on-graph checkout layer for NIP-99 markets](https://github.com/Colabonate/nips/blob/colabonate-freedom-protocol/115.md) — the earlier form of this proposal.
- [nostr-protocol/nips PR 2323](https://github.com/nostr-protocol/nips/pull/2323) — the same draft as an RFC on the Nostr list. **Note:** that RFC predates this workspace and still describes the escrow state as a Lightning hold invoice; the current model is the one above, and the RFC needs updating to match. This proposal supersedes it in content, and the RFC should be revised or closed in favour of this page.
- [Colabonate Protocol Specification](https://github.com/Colabonate/Colabonate_Protocol) — the MIT-licensed specification this layer is drawn from, including the ticket state machine and the reputation model.
- [Pontmore PIP-00 agent definition](https://github.com/pontmore/protocol/blob/main/PIP-00-agent-definition.md) and [Switchboard escrow architecture](https://github.com/samuelralak/switchboard/blob/master/docs/escrow-architecture.md) — prior work in the same space, cited by this workspace.

## Contribution guidance for follow-ups

A follow-up that extends this layer should:

- keep the direct-payment path as the default and state explicitly that it is unchanged;
- name the custody boundary of any rail it adds, in one sentence;
- state what it reveals to each actor, using the same shape as the disclosure matrix above;
- keep every addition compatible with the current specification, and keep `SPEC.md` authoritative for current behaviour;
- not claim a kind number without an allocation agreed in this workspace.
