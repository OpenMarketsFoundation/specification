# Private commerce version 1 implementation contract

**Status: experimental proposal, part of [PR #12](https://github.com/OpenMarketsFoundation/specification/pull/12).**
This contract specifies a two-party private commerce profile. It does not change
[the current compatibility snapshot](../../../SPEC.md), assign a Nostr kind,
certify a deployment or require public order/payment events.

## Schema and validation boundary

- [message.schema.json](message.schema.json) validates a decoded `{type, payload}`
  object. `type` comes from the rumor tag; `payload` is parsed `rumor.content`.
  That object is a validator input, not an additional wire wrapper.
- [capabilities.schema.json](capabilities.schema.json) defines the proposed
  capability object. Unknown offered versions remain data, not supported versions.
- [fixtures.json](fixtures.json) contains synthetic payload and sequence vectors.
  Reusable `messages` entries are referenced by each sequence's `messages` list.
- [legacy-fixtures.json](legacy-fixtures.json) gives current numeric and
  application-specific named/JSON classification examples. These require the
  original format's full schema and domain checks before becoming actionable.
- [check-private-commerce.py](../../../tools/check-private-commerce.py) checks
  schema validity, rumor hashes and a bounded reference model of the rules below.

JSON Schema describes shape. The application must separately authenticate the
NIP-59 envelope, verify the rumor hash/author, bind the local recipient, validate
roles and dependencies, and verify consequential signed and payment evidence.
Schema validity alone MUST NOT authorize a payment or order transition.

The reference model's `accepted` outcome means that a synthetic operation passes
its schema/reference/actor checks. It is not commercial acceptance or proof of
real settlement. `verified_operations` is explicit test input standing in for a
rail verifier; the tool does not authenticate signatures, encrypt messages,
query relays, inspect a wallet or verify payments. Its scenarios are not a full
production lifecycle implementation.
Its quantity profile is `item`; its example denomination registry is SAT, MSAT,
BTC, USD and EUR. Other valid units require the implementation's registered
profile/precision data, not an assumption based on a schema-valid string.

Run from the repository root:

```sh
python3 -m venv /tmp/open-markets-commerce-validator
/tmp/open-markets-commerce-validator/bin/python -m pip install -r tools/requirements-private-commerce.txt
/tmp/open-markets-commerce-validator/bin/python tools/check-private-commerce.py
```

The package is development tooling only. No implementation is required to use
Python or the reference validator. Test fixtures contain no real invoice,
preimage, signature, account key, contact or payment.

## Identity, causality and exact retry

The envelope requires kind `1327`, one `p`, and singleton `conversation`, `order`,
`operation`, `type`, `version` tags. The rumor has the NIP-01 event ID and no
signature. NIP-17/NIP-59 transport remains unchanged.

Identity is scoped by the authenticated buyer/merchant pair, conversation and
order. `operation` identifies one immutable logical action in that scope, not
an entire order or a mutable state slot. Generate a new 128-bit random operation
ID for each distinct action. References in payloads name these operation IDs,
never outer wrapper IDs. Referenced operations MUST belong to the same parties,
conversation and order, and have the required type and author.

The exact same inner rumor has the same event hash when wrapped to each party
or carried by several relays. A transport retry MUST reuse its staged bytes and
operation ID. Do not rebuild timestamps, terms, invoices or proofs during retry.
Protocol selection happens before staging, not on each network attempt.

Deduplicate both exact rumor IDs and logical operation IDs. Reusing an operation
ID with conflicting author, recipient, type, references or terms is a conflict,
not last-write-wins. Preserve both originals for bounded inspection. Equivalent
observations and adapter aliases MUST NOT credit payment, refund or inventory
twice. Any alias must remain resolvable for later dependent operations.

Missing dependencies are `deferred`, not disproved. Retain the authenticated
record and retry projection when the dependency or verification becomes available.
Wrong known type/author/scope is rejected. Unsupported type, version, quantity
unit or required extension is preserved as unsupported. Cryptographic failure
is distinct from those outcomes. Never resolve a disagreement with the newest
gift-wrap timestamp; those timestamps are randomized for privacy.

## Money, quantities and exact terms

Money is `{ "value": "1100", "unit": "SAT" }`. Values are nonnegative plain
decimal strings with no exponent, leading zeroes, unnecessary trailing fractional
zeroes, binary-float encoding or implicit unit conversion. `SAT` and `MSAT` use
whole integer values; `BTC` has at most eight decimal places. ISO 4217 currencies
use their defined precision. An unknown denomination is not interchangeable with
a known one. Decimal arithmetic MUST preserve the precision of all operands.

Each order line has an immutable `line_id`, an exact listing coordinate and
event ID, a positive decimal quantity with an explicit unit, and its complete
line amount in the order total's denomination. `item` quantities are whole
numbers. Other quantity units require a profile that defines their semantics.
The base profile does not infer service units from listing prose.

All line amounts and adjustments MUST use the order total's denomination.
Total = sum of line amounts + charge adjustments - credit adjustments. All
identifiers within items, adjustments and deliveries must be unique. A delivery
references existing line IDs, and a line cannot be allocated to two delivery
selections in this base profile. A shipping reference pins the exact same-merchant
kind-30406 revision. A third-party shipping or more complex allocation profile
must define its authority explicitly.

Price/quantity/delivery terms still require validation against the signed listing
and applicable agreement. Pinning an event ID is not a substitute for obtaining
and validating that event. Missing evidence remains unknown. Implementations may
carry signed snapshots through a registered extension rather than depend on a
mutable relay lookup; that extension must specify its exact schema and checks.

`supersedes` links one buyer-authored proposal to another proposal in the same
scope. It does not erase prior agreement, invoices or payment evidence. Accepted
terms are immutable; changing them needs an explicitly agreed amendment profile
or another proposal/acceptance, while preserving earlier obligations. Do not
silently reprice an invoice or apply a newer listing revision to an existing order.

## Registered payloads and authority

The JSON Schema is the exact field definition. Optional `note` is display text.
It cannot establish amounts, destinations, authority or state. All operations
also allow the explicit extension fields described below.

| Type | Author in base v1 | Required payload fields | Meaning and prerequisite |
| --- | --- | --- | --- |
| `order` | Buyer | `buyer`, `merchant`, `items`, `total` | Purchase request. Buyer must match seal/rumor author; merchant matches the recipient and signed listing author. Optional adjustments, deliveries and `supersedes`. Not acceptance or payment. |
| `order_accepted` | Merchant | `order_operation` | Accepts the exact referenced `order` terms. Does not prove funding. |
| `order_cancel_requested` | Buyer or merchant | `order_operation`, `reason` | Requests cancellation. Does not end an accepted obligation. |
| `order_cancelled` | Merchant | `order_operation`, `reason`, `refund_required` | Effective merchant cancellation; optional cancellation `request`. Never proof of refund. |
| `payment_request` | Merchant | `terms`, `amount`, `methods` | References an `order` or `order_accepted`; states an exact charge and payment instructions. Optional expiry. Never proof of payment. |
| `payment_proof` | Buyer | `request`, `payment_id`, `amount`, `evidence` | Claims payment of that request. Evidence identifies rail/reference and optional rail-specific proof. Does not itself credit money. |
| `payment_confirmed` | Merchant | `request`, `payment_id`, `amount`, `evidence` | Independently verified amount for the exact request; optional `proof_operation` identifies the acknowledged proof. |
| `payment_rejected` | Merchant | `request`, `reason` | Payment could not be verified or did not satisfy terms; optional `proof_operation`. Does not erase stronger established settlement evidence. |
| `refund_requested` | Buyer or merchant | `payment_confirmation`, `amount`, `reason` | Requests return of all or part of a specifically confirmed payment. Does not debit money. |
| `refund_confirmed` | Merchant | `payment_confirmation`, `refund_id`, `amount`, `evidence` | Independently verified outgoing refund outcome; optional refund `request`. Not a promise or pending send. |
| `fulfillment_update` | Merchant | `order_operation`, `fulfillment_id`, `items`, `state` | Quantity-scoped group after acceptance or verified payment; states `processing`, `ready`, `completed` or `exception`. |
| `shipping_update` | Merchant | `fulfillment_operation`, `state` | References a specific fulfillment group; states `processing`, `shipped`, `delivered` or `exception`. Optional carrier, tracking and ETA. |

Operations must address the other party in the referenced order. Public profile
metadata, a relay ACK, an invoice string or a supplied author field is not
delegation. Merchant-operated verifier/delegation profiles require separate
explicit authorization; base v1 accepts the merchant's authenticated author.
The transport self-copy retains the logical counterparty `p` tag in the rumor.

### Partial payment, refund and fulfillment

A payment request's amount must be positive and no greater than its agreed
terms. Each verified payment amount is positive and no greater than that request;
the sum of distinct credited payments cannot exceed its request or the agreed
order amount. Extra charges require separately accepted terms. A request does
not itself consume funds or justify a second invoice for an already-paid amount.

The verifier must establish rail-specific payment identity, denomination, amount,
intended payee, request correlation and finality. An evidence reference must
match an offered rail/instruction. `payment_id` helps correlate observations;
it is not payment proof. The authoritative verifier must also deduplicate the
actual rail transaction, even if a sender invents different payment IDs.

If a confirmation names a proof, its request, amount, denomination and payment
identity must agree. Unverified claims remain claims. Confirmed partial amounts
remain partial; a generic UI status cannot promote them to full payment.

`expires_at` constrains new payment attempts, not historical evidence. If a rail
verifier establishes settlement after a request expired, retain that outcome
and reconcile it through the agreed order rules; expiry must not erase funds.

Refunds reference the original confirmed payment. Sum independently verified,
distinct refunds against that payment; do not exceed its credited amount. A
refund referring to a refund request must match its confirmation and requested
amount. The rail verifier must establish the intended refund recipient and
actual transfer, not just an attempted send. Cross-denomination refunds require
an explicit agreed conversion profile. Refund proof cannot cancel fulfillment
or erase the retained original payment evidence.

`fulfillment_id` identifies an immutable group of line IDs and quantities.
Progress updates for that group do not allocate those quantities again. Each
subsequent fulfillment or shipping update includes `previous`, referencing
its direct predecessor of the same operation type and fulfillment group. A
missing predecessor is deferred; a conflicting branch is retained as a conflict
for domain resolution, not selected by timestamp. The
sum allocated across distinct groups must not exceed accepted line quantities.
Different groups permit partial delivery. State changes must be causally related
to that group; missing progress is not proof of regression. Completion/delivery
evidence is retained. Reordered messages must not reset a completed group, and
corrections require explicit evidence and a defined correction profile.

`payment_settlement`, generic chat `message`, signed `order_commit`, amendment,
escrow and delegated-verifier operations are not registered base v1 payloads.
They require a distinct defined profile/type, not an alternate interpretation
of one of the table's existing types. Kind-14 chat remains available alongside
commerce, but prose cannot drive a structured financial transition.

## Version and extension rules

`version` versions the envelope and registered operation schemas. Each
`(version, type)` has one meaning and content shape. A breaking field, authority
or semantic change requires a new version or distinct type, not payload guessing.
Unknown versions must not be parsed under version 1 merely because they look
similar. Adding a type never reassigns another type or requires a new Nostr kind.

Base payloads reject undeclared fields. Put optional namespaced additions in
`extensions`, for example `example:display`; list additions necessary to
understand the action in `requires`. Every required name must occur in
`extensions` and have a supported, validated schema and meaning. Unknown required
extensions make the operation unsupported and non-actionable. Unknown optional
extensions can be preserved and ignored only because they cannot change base
amounts, roles, references or state semantics. Do not put indispensable signed
terms in an optional extension and then authorize without them.

Bound messages, extension depth and queues before encryption/storage. Refuse an
oversized operation without truncating signed terms or proof. Capability discovery
is not permission to weaken the reader's privacy/transport limits.

## Proposed capability publication

This section is experimental interoperability signaling, not a new NIP rule.
An implementation may advertise a peer's receive capabilities in the peer's
signed kind-0 profile content under `open_markets.private_commerce`, using
[capabilities.schema.json](capabilities.schema.json):

```json
{
  "open_markets": {
    "private_commerce": {
      "versions": [{
        "version": "1",
        "receive": ["order", "payment_proof", "order_cancel_requested"],
        "extensions": []
      }],
      "legacy_receive": ["open_markets_16_17", "conduit_named_16"],
      "expires_at": 1900000000
    }
  }
}
```

This object is merged into existing profile JSON, not a replacement profile.
Only the peer's own valid signature advertises that peer's capabilities. Validate
the replaceable-event frontier, expiration, duplicate versions and known types.
An application handler descriptor is not evidence of a user's installed reader.
Unknown offered versions/types remain data; use only the supported intersection.
The listed types indicate receive support, not authorization to send those types.

Absent, stale or unavailable capability observations are unknown. They must not
be invented into support or mislabeled as refusal. A fresh explicit empty
`versions` list advertises no new-format support. Profile editors should preserve
the namespaced object; a missing object after another edit requires repair or
explicit peer-format selection. Use latest validated applicable evidence, not
stale positive evidence to override a fresh explicit withdrawal.

Recipients may also explicitly select a bounded experimental profile with their
counterparty. Record that selection and supported operations; do not infer it
from a client brand or successful decryption. This allows implementation and
rollout without waiting for unrelated marketplaces. The public convention and
kind assignment still require upstream coordination before normative adoption.
Capability metadata is not an inbox relay list: kind-10050 remains authoritative.

Do not use NIP-78 app-private storage as a public cross-client capability format;
its current specification explicitly excludes that interchange purpose.

## Migration and rollout

Implement three named readers: current Open Markets numeric kind-16/kind-17,
existing application-specific named/JSON kind-16, and this versioned envelope.
An application-specific reader validates its own exact published schema; an
arbitrary JSON object or named `type` is not sufficient. Retain encrypted originals,
source format, authenticated author, exact references and unsupported fields.

The [legacy semantic mapping](../../private-structured-messages.md#legacy-semantic-mapping)
is conditional: `pending` does not prove acceptance; a buyer receipt is a payment
claim; merchant `confirmed` only authorizes paid state when the required evidence
is established. A free-form address with no machine-readable country remains
unknown for automatic destination checks. Do not infer it from text or silently
discard the order. Independent receipt of a legacy order must not bypass current
signed terms, verifier or inventory admission requirements.

1. Freeze a proposal/schema revision and capability rules; publish fixtures.
2. Ship readers and recover retained unsupported history before changing writers.
3. Select one supported format for a logical send, then stage exact encrypted
   recipient/self copies before network I/O. Do not dual-send invoice-generating
   actions. A legacy adapter uses an explicit correlation alias only when verified
   identities and terms match; title, amount or timestamp heuristics are unsafe.
4. Migrate full purchase/payment and existing operational flows, preserving old
   histories and known old-peer replies. Unknown-format selection must have a
   clear recovery/repair action rather than silently dropping messages.
5. Make updated implementation defaults follow the selected contract after its
   own schema, authority, old-reader, cryptographic and recovery checks pass.
   External adoption or participation is useful evidence, not a universal gate.
6. Communicate the exact contract, kind coordination, support matrix, migration
   and legacy-write retirement. Retain bounded legacy reads for actual saved
   histories; do not require another marketplace to approve implementation work.

Rollback changes future selection only. Staged jobs retain their original format,
identity, targets and bytes. Readers continue to understand already-written new
history. An implementation must not turn rollback into a second semantic send,
broader relay fanout or rewritten payment evidence.

## Remaining upstream decisions

- Kind registration and agreement on one interpretation of `1327` with PR #10.
- Acceptance of these proposed schemas, operation semantics and profile signal.
- Separate signed-child, amendment, verifier and multiparty profiles when needed.
- Implementation-specific legacy retention and deployment support windows.

These are recorded proposal decisions, not claims of accepted ecosystem behavior.
