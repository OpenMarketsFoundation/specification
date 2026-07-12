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

Kind `1327` is a regular event kind and is currently unassigned in the Nostr
event-kind registry. Adoption of this proposal requires coordinating and
registering that assignment upstream. An apparently unused number is not a
durable reservation by itself.

The kind `1327` rumor is sealed and gift wrapped according to NIP-59. Senders
SHOULD publish a recipient gift wrap and a self-addressed gift wrap according
to NIP-17 recovery guidance.

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
    ["type", "payment_confirmed"],
    ["version", "1"]
  ],
  "content": "{\"amount\":\"12\",\"currency\":\"SAT\"}"
}
```

The rumor MUST contain:

- one or more `p` tags naming the recipients;
- one `conversation` tag containing a stable, application-independent
  conversation identifier;
- one `type` tag containing a registered named message type;
- one `version` tag containing `1`.

The rumor SHOULD contain an `order` tag once an order identifier exists. The
conversation identifier MAY equal the order identifier for simple fixed-price
orders. Negotiations that begin before an order is committed MAY retain an
earlier trade or conversation identifier while adding the eventual order
identifier separately.

The `content` field MUST contain a JSON object conforming to the schema for the
named message type. Message schemas may define additional required tags.

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

A merchant does not need to send `order_accepted` after authoring a valid
`payment_confirmed` message. Payment confirmation already communicates that the
merchant has verified payment and the order may proceed to fulfillment.

### `order_cancelled`

Buyer- or merchant-authored cancellation. The payload SHOULD state whether the
order was unpaid, payment was rejected, fulfillment was impossible, or a refund
is required. Cancellation does not itself prove that a refund occurred.

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

After a valid `payment_confirmed` message, clients SHOULD present fulfillment,
cancellation with refund, and refund actions rather than asking the merchant to
accept the order or issue the same invoice again.

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

### `payment_settlement`

Optional advanced payment outcome for release, split, claim, or other
multi-party settlement. Simple direct payments and refunds do not need this
message type. Any escrow or arbitration specification using this type MUST
define its payload and authorization requirements separately.

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
5. write new version 1 structured commerce messages as kind `1327` after the
   recipient ecosystem has adopted this proposal;
6. preserve kind `14` for unstructured chat.

Readers MAY accept legacy numeric type values during a transition. Writers MUST
use named types for kind `1327` messages.

Implementations SHOULD record the source format locally so they do not replay a
legacy kind `16` or `17` message as if it were a new kind `1327` message without
explicit conversion and validation.

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
- the exact JSON schema for each version 1 message type;
- whether `conversation` should use a random identifier, order identifier, or a
  deterministic trade identifier in each market lane;
- authorization rules for merchant-operated payment verifiers;
- which optional signed child message types should be shared with the Orders
  proposal;
- the duration and signaling of the legacy dual-read period.
