# Commerce Testing

Status: **Experimental proposal**, not an adopted Open Markets requirement.

Support is optional. MUST, SHOULD, and MAY below describe conformance to this
experimental profile only. The current [compatibility snapshot](../SPEC.md)
remains unchanged. The namespace below is proposed, not an existing allocation.

## Purpose and scope

A staging client can publish to the same Nostr relays as a production client.
Other applications cannot infer testing intent from its deployment branch.
This proposal lets cooperating clients identify synthetic commerce activity,
exercise actual relay and cross-client behavior, and keep test activity out of
ordinary shopping and merchant operations.

The profile combines author-supplied event labels with voluntarily designated
test identities. It provides cooperative classification, not enforced network
separation. Older clients may display or act on test events. A designation
does not prove trustworthiness, prevent a payment, or guarantee erasure.

The initial scope covers public listings (`30402`), collections (`30405`),
shipping options (`30406`), reviews (`31555`), and private commerce messages
described by the current specification. General conversation (`14`) is covered
only when explicitly associated with a test commerce transaction. Profile,
relay-list, authentication, and wallet-protocol events keep their existing
meaning; they are not automatically labeled or redefined by this proposal.

No new event kind, global registry, profile format, or mandatory relay feature
is introduced. Adapters to experimental order envelopes belong with those
proposals; this profile does not depend on their acceptance or resolve existing
kind-number conflicts in private commerce messages.

## Event designation

Publishers MUST include both of these NIP-32 self-labels on each test commerce
event or inner private commerce rumor:

```json
[
  ["L", "org.openmarkets.testing"],
  ["l", "org.openmarkets.testing:test", "org.openmarkets.testing"]
]
```

The designation means that the author intends this event for testing rather
than ordinary commerce. It is an event-level declaration, not an automatic
declaration about every event from that author.

Matching is exact and case-sensitive. Other namespaces and ordinary tags do
not affect this designation. Identical repeated testing tags are interpreted
idempotently; publishers SHOULD emit each once. A testing namespace without
its canonical label, a reserved label without its matching namespace, a wrong
namespace mark, extra values in a testing tag, or another value declared in
this namespace is ambiguous or unsupported. Readers MUST quarantine such
commerce events from live automation and report the declaration problem.
They MUST NOT interpret an unsupported value as permission for live commerce.

An external `kind:1985` label is not this self-designation. An unrelated
party's label MUST NOT, by itself, suppress or reclassify another author's
listing under this profile. Other moderation policies remain independent.

Unsigned public event template, to be completed and signed by a controlled
test identity before an authorized trial:

```json
{
  "kind": 30402,
  "content": "Synthetic listing for an agreed interoperability session.",
  "tags": [
    ["d", "interop-demo-product"],
    ["title", "TEST: demonstration product"],
    ["price", "1", "USD"],
    ["L", "org.openmarkets.testing"],
    ["l", "org.openmarkets.testing:test", "org.openmarkets.testing"]
  ]
}
```

The title helps humans using older clients. It is not a machine-readable
substitute for the designation and does not disable purchase in older clients.

## Dedicated test identities

Participants SHOULD use dedicated, securely generated Nostr identities for
interoperability testing. These use ordinary keys generated with a CSPRNG.
This proposal reserves no key space and introduces no predictable or publicly
shared private keys. Public npubs may be exchanged between participants;
private keys and signer connection credentials MUST remain controlled by
their operators and MUST NOT appear in fixtures, traces, or published evidence.

Clients MAY recognize test identities through explicit local configuration or
an agreed test-session roster. A roster contains public identities and session
configuration only; its exchange format is outside this initial profile.
Importing a roster requires explicit operator selection. An arbitrary remote
label or unsolicited roster MUST NOT silently change local identity policy.

Participating clients MUST:

- Perform normal signature, schema, sender, recipient, and authorization
  validation. Roster membership grants no extra authority or trust.
- Keep commerce activity authored by a configured test identity in test
  context even if its event label is missing. Report the omission as a
  conformance failure; do not treat it as live processing permission.
- Classify private commerce using the authenticated inner author and intended
  recipient, not the temporary gift-wrap author. A configured test recipient
  also requires test handling in that recipient's client.
- Continue requiring event labels from their own test publishers. A roster
  supplements the portable event declaration.
- Preserve already recorded test classification when an identity is removed
  from a roster. Removal is not a conversion of existing test operations.

Participants SHOULD use a separate identity for live commerce rather than
repurposing a designated test identity. Unknown identities can still publish
validly self-labeled test events; roster membership is not required to hide
them from ordinary commerce.

## Classification and ordinary client behavior

Only authenticated, schema-valid evidence can establish a declaration or
relationship. Invalid events MUST NOT alter the classification of legitimate
resources or transactions. For public events, authenticate the signed event.
For private rumors, validate the NIP-59 layers, rumor hash and structure, and
equality of the seal author and rumor author before using inner metadata.

Within this profile, process valid commerce evidence in this order:

1. An ambiguous or unsupported testing declaration is quarantined. Known test
   context is retained while the declaration problem is reported.
2. A canonical self-label, an explicitly configured test participant, or
   previously established test context requires test handling.
3. An event with none of those signals follows existing client rules. The
   absence of a test declaration establishes neither trust nor purchase
   authority, and no global search for test metadata is required.

Participating clients MUST exclude test activity from ordinary discovery,
recommendations, reputation calculations, sales totals, and live operational
queues. They MAY expose an explicitly enabled testing view. Every display of
test activity, including direct links and notifications, MUST visibly identify
it as test activity. A direct link MUST NOT bypass processing restrictions.

Quarantined events MAY be inspected in a diagnostic view but MUST NOT enter
live automation. Quarantine does not authorize deleting unrelated records.

## Transactions, references, and persistence

A client generating an order, response, receipt, update, or review in known
test context MUST preserve the event designation. Test order context MUST be
bound to the authenticated participants and existing transaction identity,
not just a bare order string or arbitrary incoming reference. An attacker
cannot reclassify an existing live order by claiming its identifier.

Missing labels on a later authenticated message MUST NOT promote a known test
transaction to live commerce. Persist test context with the transaction so
retry, duplicate delivery, restart, and roster removal preserve it. Existing
deduplication and idempotency rules still apply; this profile supplies no new
order identity or payment authority.

Mixed test/live commerce objects MUST be rejected from automatic processing.
A test transaction cannot consume live inventory, apply a live shipping
policy, or contribute a live review. A test event referencing a live resource
does not reclassify or authorize mutation of that resource. An unresolved
referenced resource remains unresolved; automatic test processing waits for
adequate positive test-context evidence rather than assuming it is a test
resource. This rule does not introduce a metadata-discovery gate for ordinary
unmarked commerce.

Test publishers MUST use distinct commerce resource coordinates and MUST
prevent writes to coordinates already used for live resources. Labels do not
change NIP-01 replacement identity: an addressable event remains identified by
kind, author, and `d`. A configured test author is especially useful because
its publications cannot replace another identity's live listings.

Test coordinates MUST NOT be repurposed as live resources. A real offering
requires a deliberate new live coordinate. If a client has authenticated test
history for a coordinate, removing its label in a later version does not make
that coordinate live in that client. This local protection cannot prove that
another client has observed the same history.

## Private-message handling

Put the testing labels inside the inner commerce rumor before NIP-17/NIP-59
encryption. Keep the rumor unsigned and the seal tags empty as required by
NIP-59. This proposal adds no test label, shared session identifier, or commerce
metadata to public gift-wrap tags. Existing recipient routing and encryption
requirements remain in force. Relays cannot classify these inner labels.

Decoded private order fragment, not a signed event or an encryption vector:

```json
{
  "kind": 16,
  "tags": [
    ["p", "<test-merchant-public-key>"],
    ["subject", "TEST: interoperability order"],
    ["type", "1"],
    ["order", "interop-demo-order"],
    ["amount", "1"],
    ["item", "30402:<test-merchant-public-key>:interop-demo-product", "1"],
    ["L", "org.openmarkets.testing"],
    ["l", "org.openmarkets.testing:test", "org.openmarkets.testing"]
  ],
  "content": "Synthetic order; no real payment or fulfillment."
}
```

Placeholder strings in this fragment must be replaced by actual public keys
for a trial. It includes no customer contact, address, invoice, or payment proof.

Before initiating a private test transaction, participants MUST explicitly
agree to the session and configure the intended test counterparties. Initial
trials use local/session configuration; they MUST NOT assume an arbitrary
recipient supports the convention or send unsolicited test orders to real
merchants. Receipt of a labeled message alone is not permission to respond or
an authorization to perform side effects.

## Payments and operational effects

The initial profile MUST disable real-value wallet operations, live inventory
mutation, and live fulfillment for test activity. Simulated inventory and
fulfillment state MAY advance inside the isolated testing context.

Payment exercises MAY use explicitly configured simulated providers or test
networks. Provider and network checks are independent of event labeling.
Unknown payment-network/provider state MUST block the test payment operation.
A test label does not turn a real invoice, mint, wallet, refund, or payment
destination into a simulation. Real-value payment testing is outside this
profile and needs a separate explicit operating agreement.

## Relay filtering and cleanup

A test client can request labeled public listings using the existing NIP-01
filter syntax:

```json
{
  "kinds": [30402],
  "#l": ["org.openmarkets.testing:test"],
  "limit": 20
}
```

Clients still validate the namespace mark and event after receiving it. A
known roster can also be used in positive `authors` filters for public test
activity. These queries do not classify encrypted inner messages.

NIP-01 has no general negative tag or author filter. Production clients
generally exclude test activity after receiving it; this proposal does not
eliminate its relay storage, bandwidth, or initial-query limit cost. Requiring
every live event to carry a new production label would break compatibility
and is not part of this proposal.

Repetitive CI, fault injection, and high-volume agent tests SHOULD use local
or dedicated relays. Public-relay sessions SHOULD be bounded, explicitly
authorized by the participants, and follow relay operator policies. No test
publication or real-world payment is required to validate this proposal PR.

NIP-40 expiration MAY be used where supported, with NIP-09 deletion requests
for cleanup. Neither guarantees erasure. Synthetic data MUST NOT include real
customer information, credentials, or bearer-value payment material. A test
designation makes no privacy or retention promise.

## Conformance and adoption evidence

[Conformance examples](../examples/commerce-testing/README.md) explain the
synthetic scenario format; [cases.json](../examples/commerce-testing/cases.json)
records the expected outcomes below. These are policy scenarios, not signed
events, cryptographic vectors, or evidence of implemented client behavior.

| ID | Scenario | Required outcome |
| --- | --- | --- |
| TEST-01 | Tagged listing in production discovery or a direct link | Hide from ordinary browsing; mark test on inspection; block live effects |
| TEST-02 | Order and response across participating clients | Both retain the canonical test designation |
| TEST-03 | Follow-up omits its marker | Keep authenticated transaction test context; report omission |
| TEST-04 | Test order references a known live product | Reject automatic processing; live product unchanged |
| TEST-05 | Third party labels another author's listing | Do not reclassify the target under this profile |
| TEST-06 | Test write reuses a known live coordinate | Prevent publication before signing or sending |
| TEST-07 | Test flow reaches a real-value wallet operation | Block the operation |
| TEST-08 | Retry, duplicate, or restart | Retain test context and existing idempotency behavior |
| TEST-09 | Roster author publishes unmarked commerce | Keep test context; report missing label |
| TEST-10 | Identity removed from roster | Previously recorded test operations remain test |
| TEST-11 | Invalid signature, sender binding, or authorization | Reject; no mutation of legitimate state |
| TEST-12 | Unknown author sends a validly self-labeled test event | Recognize test designation without requiring roster membership |
| TEST-13 | Malformed or unsupported testing declaration | Quarantine; no live automation |
| TEST-14 | Private test message wrapping | Labels inside authenticated rumor; no testing metadata added to public envelope |
| TEST-15 | Test order references an unresolved product | Defer automatic processing; do not assume test context for the product |
| TEST-16 | Ordinary event has no testing signals | Apply existing rules; no new trust or purchase authority |
| TEST-17 | Marker removed from a known test coordinate | Preserve its recorded test classification |
| TEST-18 | Unmarked commerce reaches a configured test recipient | Recipient keeps activity in test context; reports omission |
| TEST-19 | Outbound test order targets an unagreed recipient | Block initiation; do not probe by sending an order |

Before proposing adoption, two independently implemented clients should
demonstrate labeled discovery and private order/response exchange in a bounded
session. Record client versions, proposal revision, relay capabilities, which
cases were exercised, and remaining gaps. Relay acceptance is not recipient
observation or semantic confirmation. Synthetic fixture checks alone do not
establish cryptography, relay delivery, privacy, or cross-client interoperability.

## Prior art and review questions

Public Nostr sources checked on 2026-11-03, pinned to revision
`400d157c53264b8e58c7b3cdbd21ef546fb7a157`:

- [NIP-01](https://github.com/nostr-protocol/nips/blob/400d157c53264b8e58c7b3cdbd21ef546fb7a157/01.md): tags, filters, signatures, and replacement identity.
- [NIP-32](https://github.com/nostr-protocol/nips/blob/400d157c53264b8e58c7b3cdbd21ef546fb7a157/32.md): indexable namespaced self-labeling; it does not define this testing vocabulary.
- [NIP-17](https://github.com/nostr-protocol/nips/blob/400d157c53264b8e58c7b3cdbd21ef546fb7a157/17.md) and [NIP-59](https://github.com/nostr-protocol/nips/blob/400d157c53264b8e58c7b3cdbd21ef546fb7a157/59.md): authenticated private-message wrapping and metadata boundaries.
- [NIP-87](https://github.com/nostr-protocol/nips/blob/400d157c53264b8e58c7b3cdbd21ef546fb7a157/87.md): network identifiers in mint discovery are related precedent, not a general testing convention.
- [NIP-40](https://github.com/nostr-protocol/nips/blob/400d157c53264b8e58c7b3cdbd21ef546fb7a157/40.md) and [NIP-09](https://github.com/nostr-protocol/nips/blob/400d157c53264b8e58c7b3cdbd21ef546fb7a157/09.md): expiration and deletion requests do not guarantee erasure.
- [Issue #352](https://github.com/nostr-protocol/nips/issues/352): a testing/local key-space proposal was withdrawn after enforceability objections. Dedicated ordinary test identities do not reserve keys or promise enforcement.

Review should focus on the proposed namespace, whether a deployed vocabulary
should be reused, the initial event coverage, and whether the classification
and operational rules are precise enough for independent implementations.
A portable identity declaration or interoperable roster format may be explored
after the initial trial; neither is required by this proposal.
