# Private Structured Commerce Messages

Status: experimental proposal.

This proposal replaces the current private order-message use of kinds `16` and
`17` with one versioned, extensible structured-message rumor. It does not change
the current normative compatibility snapshot until accepted.

## Problem

The inherited marketplace specification assigns:

- kind `16` to order creation, payment requests, order status, and shipping;
- kind `17` to payment receipts and verification.

Those assignments conflict with the current Nostr registry:

- [NIP-18](https://github.com/nostr-protocol/nips/blob/master/18.md) defines kind
  `16` as Generic Repost;
- [NIP-25](https://github.com/nostr-protocol/nips/blob/master/25.md) defines kind
  `17` as an external content reaction.

[NIP-17](https://github.com/nostr-protocol/nips/blob/master/17.md) and
[NIP-59](https://github.com/nostr-protocol/nips/blob/master/59.md) may carry a
rumor of a kind other than `14`, but gift wrapping does not create a separate
event-kind namespace. Decrypted clients still need one unambiguous meaning for
each inner kind.

The current numeric `type` values also make extension and debugging harder:
implementers must know that `1`, `2`, `3`, and `4` mean order, payment request,
status update, and shipping update. Adding a new operation requires assigning
another implicit number rather than naming the operation directly.

## Goals

This proposal aims to:

1. remove the kind `16` and `17` collisions for new private commerce messages;
2. use self-describing, named message types;
3. distinguish a payment claim from merchant verification of payment;
4. support order-specific private conversations and future message types;
5. keep ordinary human conversation on the standard kind `14` rumor;
6. allow portable signed evidence where another specification requires it
   without requiring signed child events for routine commerce messages.

Public order state, escrow, arbitration, temporary trade keys, and public
payment lifecycle events are outside this proposal.

## Event Kind

Private structured commerce messages use inner rumor kind `1327`.

Kind `1327` is the proposed regular event kind, not a reserved assignment.
Implementers must check and coordinate the upstream kind registry before
adoption. Experimental implementation does not make the assignment normative;
an apparently unused number is not a durable reservation by itself.

The kind `1327` rumor is sealed and gift wrapped according to NIP-59. Senders
MUST create independent recipient and sender copies according to NIP-17,
except where its explicitly chosen disappearing-message behavior applies.
Each copy follows that recipient's declared kind-10050 inbox relays. A relay
ACK is delivery evidence, not receipt, acceptance, payment or fulfillment.

## Envelope

A version 1 structured commerce rumor has this shape:

```jsonc
{
  "id": "<event-id>",
  "pubkey": "<sender-pubkey>",
  "created_at": 1700000000,
  "kind": 1327,
  "tags": [
    ["p", "<recipient-pubkey>", "<relay-hint>"],
    ["conversation", "<stable-conversation-id>"],
    ["order", "<order-id>"],
    ["operation", "<32-lowercase-hex-operation-id>"],
    ["type", "payment_confirmed"],
    ["version", "1"]
  ],
  "content": "{\"request\":\"<payment-request-operation-id>\",\"payment_id\":\"<rail-payment-identity>\",\"amount\":{\"value\":\"12\",\"unit\":\"SAT\"},\"evidence\":{\"rail\":\"lightning\",\"reference\":\"<invoice>\"}}"
}
```

The rumor MUST contain:

- exactly one `p` tag naming the other party in the version 1 two-party profile;
- one `conversation` tag containing a stable, application-independent
  conversation identifier;
- one `type` tag containing a registered named message type;
- one `version` tag containing `1`;
- one `operation` tag containing 32 lowercase hexadecimal characters, generated
  with at least 128 bits of randomness for each distinct logical operation;
- one `order` tag containing the stable private order identifier.

The order identifier may identify a proposed order before merchant acceptance;
it does not establish that an accepted order exists. The conversation identifier
MAY equal the order identifier for simple fixed-price orders. Negotiations may
retain an earlier conversation identifier while adding separate order IDs.
An order identity MUST NOT be reused for an unrelated purchase. Identifiers are
opaque strings of at most 128 characters; use application-independent random
identifiers rather than URLs or a merchant-local database primary key.

`conversation`, `order`, `operation`, `type` and `version` MUST each appear once
with exactly two tag elements. `p` has two elements plus an optional relay hint.
Duplicate singleton tags, conflicting identities and a supplied rumor ID that
does not match NIP-01 serialization MUST be rejected. The rumor is unsigned;
sender authentication belongs to the NIP-59 seal, not a rumor `sig` field.

The base version 1 profile is intentionally two-party. A future multiparty or
delegated-verifier profile must specify participants, recipients and authority;
it must not silently reinterpret these payloads or recipient rules.

The `content` field MUST contain a JSON object conforming to the schema for the
named message type. Message schemas may define additional required tags.
Duplicate JSON properties and non-finite numbers MUST be rejected. Payload
fields outside the schema MUST NOT be silently treated as registered extensions.

The exact proposed schemas, actor/reference rules, capability representation,
synthetic examples and validation command are defined in the
[version 1 implementation contract](private-commerce/v1/README.md). That
contract is part of this experimental proposal, not current `SPEC.md` behavior.

A message type has one content shape within a protocol version. Extensions
that require a different content shape MUST register a distinct type name or a
new protocol version rather than guessing from the payload at runtime.

Type names use lowercase `snake_case`. Future specifications may register more
names without allocating another event kind. A client that does not recognize a
type MUST NOT interpret it as another known type. It MAY preserve the message
as an unsupported structured message.

## Version 1 Message Types

### `order`

Buyer-authored request to purchase one or more referenced listings. The payload
contains the requested items, quantities, totals, delivery selection, and any
buyer-provided order details.

Receipt of an `order` message does not prove payment or merchant acceptance.

### `order_accepted`

Merchant-authored acceptance of an unpaid order or negotiated terms.

A merchant does not need to send another `order_accepted` after confirming a
payment against those exact terms. That confirmation records agreement and the
verified amount. Fulfillment still depends on the terms' funding and delivery
requirements; a partial confirmation does not establish full payment.

### `order_cancel_requested`

Buyer- or merchant-authored request to cancel a specific order proposal or
accepted order. A request does not itself cancel an accepted obligation, refund
a payment or withdraw a shipment. It references the exact order operation.

### `order_cancelled`

Merchant-authored effective cancellation in the version 1 two-party profile.
The payload references the exact order operation and states the reason and
whether a refund is required. A buyer sends `order_cancel_requested`; another
profile may define unconditional buyer cancellation with explicit agreed rules.
Cancellation does not itself prove that a refund occurred.

### `payment_request`

Merchant-authored request for payment. The payload contains the amount,
currency or denomination, expiration when applicable, and one or more payment
instructions.

A `payment_request` MUST NOT be interpreted as payment proof or settlement.
Clients SHOULD NOT offer a new payment request after payment has been confirmed
unless the request is clearly identified as a separate charge accepted by the
buyer.

### `payment_proof`

Buyer-authored claim that payment was made. The payload contains the payment
rail, amount, denomination, and rail-specific evidence required for
verification.

A `payment_proof` message is a claim, not merchant acceptance. Clients MUST NOT
move an order into paid fulfillment solely because an unverified proof was
received.

### `payment_confirmed`

Merchant-authored confirmation that payment was independently verified. The
payload identifies the verified amount, denomination, rail, and the payment
request or proof being acknowledged when available.

Confirmation applies only to the exact verified amount and referenced request.
A partial payment does not mark an entire order paid. The receiver validates the
merchant's authority and preserves the verifier/evidence boundary; a signature
alone does not prove rail settlement.

When verified confirmations satisfy the required payable amount, clients SHOULD
present eligible fulfillment, cancellation with refund, and refund actions.
Partial funding remains visible with the outstanding amount. Do not ask the
merchant to accept the same terms again or issue another invoice for an already
paid amount. Other charges require explicitly accepted terms.

### `payment_rejected`

Merchant-authored statement that a payment claim could not be verified or did
not satisfy the requested terms. The payload SHOULD contain a machine-readable
reason and MAY include a human-readable explanation.

### `refund_requested`

Buyer- or merchant-authored request to return a confirmed payment. This message
does not prove that a refund occurred.

### `refund_confirmed`

Merchant-authored confirmation that a refund was issued. The payload contains
the refunded amount, denomination, rail, and rail-specific evidence when
available.

The merchant must have independently verified that rail outcome. A requested
refund, outbound transfer attempt or pending transaction is not confirmation.
A partial refund does not erase the remaining paid amount or prove that all
funds reached the buyer. Receipt/finality requirements remain rail-specific.

### `payment_settlement`

Reserved design space for release, split, claim or other multiparty settlement.
This name is NOT registered in the base version 1 schemas. Until a separate
profile defines its exact payload and authorization, readers preserve it as
unsupported and writers MUST NOT emit it as a base version 1 operation. Simple
direct payments and refunds do not need this operation.

### `fulfillment_update`

Merchant-authored operational update after payment or acceptance. The payload
contains a fulfillment state such as `processing`, `ready`, `completed`, or
`exception` and MAY include a human-readable note.

Financial events such as payment confirmation, rejection, or refund MUST use
their payment-specific message types rather than a generic fulfillment state.

### `shipping_update`

Merchant-authored physical delivery update. The payload contains a delivery
state such as `processing`, `shipped`, `delivered`, or `exception` and MAY
contain carrier, tracking, and estimated delivery information.

## Plain Conversation

Unstructured human conversation remains a NIP-17 kind `14` rumor. Clients MUST
NOT use kind `1327` with a generic `message` type as an alternate chat format.

Kind `14` messages MAY use the same conversation or order subject convention in
the user interface, but they do not become structured commerce operations.

## Authentication And Signed Child Events

NIP-59 authenticates the sender of a private rumor through its signed seal. That
authentication is sufficient for routine messages exchanged by the original
participants.

A separate signed child event is useful when exact content must remain
independently verifiable outside the original encrypted conversation, for
example when:

- negotiated terms will later be published as a public event;
- a participant must present an authorization to an arbiter;
- multiple recipients must verify one stable event identifier and signature;
- another protocol requires a portable commitment.

Signed child events are therefore optional and message-type-specific. A future
message type MAY define its `content` as a signed Nostr event JSON object and
MUST then define the allowed child kinds, authors, tags, and verification rules.
Clients MUST NOT assume that every kind `1327` message contains a signed child
event.

Kind `1327` itself is private coordination, not canonical public order or
payment state. A specification that promotes or projects private messages into
public lifecycle events MUST define that mapping separately.

## Legacy Semantic Mapping

Migration is not a mechanical replacement of kind numbers. Several legacy
messages combine claims, verification, financial state, and fulfillment state
that version 1 separates explicitly.

| Legacy message | Version 1 replacement |
| --- | --- |
| kind `16`, numeric type `1` | `order` |
| kind `16`, numeric type `2` | `payment_request` |
| kind `16`, numeric type `3`, pending/accepted | `order_accepted` when the merchant actually accepts unpaid terms |
| kind `16`, numeric type `3`, confirmed/paid | `payment_confirmed` only after merchant verification |
| kind `16`, numeric type `3`, processing/completed | `fulfillment_update` |
| kind `16`, numeric type `3`, cancelled | `order_cancelled`, followed by `refund_confirmed` when money is returned |
| kind `16`, numeric type `4` | `shipping_update` |
| kind `17` buyer payment receipt | `payment_proof` |
| kind `17` merchant verification | `payment_confirmed` |

Implementations MUST NOT translate an ambiguous legacy receipt directly into
`payment_confirmed` unless the author and rail-specific evidence establish that
the merchant verified settlement.

## Relationship To The Orders Draft

[Open Markets specification PR 10](https://github.com/OpenMarketsFoundation/specification/pull/10)
also proposes kind `1327` for a private Structured Message whose content is a
signed child event, alongside public order and payment lifecycle kinds
`32122` through `32127`.

This proposal preserves the useful convergence on kind `1327` while narrowing
the base requirement: signed child events are available when portable
authorization is necessary, but routine invoices, payment confirmations, and
fulfillment updates remain simple structured payloads.

If both proposals advance, the Orders draft should consume this envelope rather
than define an incompatible second interpretation of kind `1327`. Its public
lifecycle events may register distinct names such as `order_commit` for message
types whose payloads are signed child events. It should not silently change the
content shape of an existing version 1 type such as `order` or
`payment_confirmed`.

PR 10's public lifecycle, temp-key authorization and signed commitments are
separate profiles. Adopting this base envelope does not adopt those public
events, make an arbiter mandatory or authorize publication of private data.

## Legacy Migration

Implementations migrating from the current marketplace specification SHOULD:

1. read legacy kind `16` order messages only when their tags and payload match
   the legacy commerce schema;
2. read legacy kind `17` payment receipts only when their tags and payload match
   the legacy commerce schema;
3. never treat every decrypted kind `16` event as an order, because valid
   NIP-18 Generic Reposts use that kind;
4. never treat every decrypted kind `17` event as a payment receipt, because
   valid NIP-25 external content reactions use that kind;
5. write the new format when the intended peer explicitly supports the selected
   version/types, or both parties explicitly select an experimental profile;
   do not require unrelated marketplaces or the ecosystem as a whole to adopt it;
6. preserve kind `14` for unstructured chat.

Readers MAY accept legacy numeric type values during a transition. Writers MUST
use named types for kind `1327` messages.

Implementations SHOULD record the source format locally so they do not replay a
legacy kind `16` or `17` message as if it were a new kind `1327` message without
explicit conversion and validation.

Readers SHOULD also retain strictly validated application-specific named/JSON
kind-16 histories behind a named adapter, such as existing Conduit records.
An adapter retains its original provenance and unknown fields; it MUST NOT
manufacture missing destination, payment, acceptance or fulfillment evidence.
The same decrypted kind number is never sufficient to choose an adapter.

Send one representation per logical operation. Schema/authority regressions,
known old-peer compatibility and exact retry/recovery determine an implementer's
rollout readiness. External adoption and review are communication tracks, not a
universal deployment gate. Experimental kind usage remains explicitly labeled
until the assignment and proposal are accepted upstream.

Stored legacy history is not automatically rewritten or republished. Rollback
changes future format selection, not already staged signed/encrypted bytes.
The [implementation contract](private-commerce/v1/README.md#migration-and-rollout)
defines identity, deduplication, deferred dependencies and compatibility states.

## Privacy And Verification

Addresses, contact details, invoices, payment evidence, tracking numbers, and
order contents belong only inside the encrypted rumor. Implementations MUST NOT
copy this information onto the outer kind `1059` gift wrap.

Recipients MUST perform the NIP-59 seal and rumor author checks before applying
a structured operation. They MUST also validate the payload for the named type
before changing local order state.

Payment confirmation requires rail-specific verification. The presence of a
well-formed `payment_proof` message is not evidence that the referenced payment
settled.

## Open Questions

Before this proposal becomes normative, implementers should agree on:

- the upstream registration path for kind `1327`;
- acceptance of the concrete version 1 schemas and operation/reference rules
  supplied with this proposal;
- adoption of the proposed signed capability publication convention;
- authorization rules for merchant-operated payment verifiers;
- which optional signed child message types should be shared with the Orders
  proposal;
- the duration and signaling of the legacy dual-read period.
