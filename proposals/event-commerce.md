# NIP-52-backed Event Markets

Status: experimental proposal.

This proposal defines an event-market profile by composing existing Open
Markets product collections and pickup options with existing NIP-52 calendar
events. It introduces no new event kind, stall, booth registry, marketplace
registry, or application-owned service.

The proposal is intended to let independent clients create, discover, render,
and transact through the same public event catalog. It does not make the event
organizer the merchant, payment recipient, or recipient of a buyer's full
order.

## Public sources

- [NIP-01 addressable events and relay messages](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [NIP-09 deletion requests](https://github.com/nostr-protocol/nips/blob/master/09.md)
- [NIP-19 `naddr` identifiers](https://github.com/nostr-protocol/nips/blob/master/19.md)
- [NIP-52 calendar events](https://github.com/nostr-protocol/nips/blob/master/52.md)
- [NIP-99 classified listings](https://github.com/nostr-protocol/nips/blob/master/99.md)
- [Current Open Markets compatibility snapshot](../SPEC.md)

## Scope

This proposal defines:

- an event-backed profile of a kind `30405` product collection;
- organizer provenance from the linked NIP-52 event;
- empty upcoming event catalogs;
- merchant requests and organizer acceptance through two-sided references;
- explicit open or closed acceptance of new event commerce;
- optional organizer-operated or merchant-operated fixed pickup;
- compatibility and resolution requirements for independent clients.

This proposal does not define ticketing, RSVP policy, check-in, recurring
calendar events, reputation, global event discovery, payment custody, a new
order envelope, or private organizer handoff authorization.

## Event-market graph

The profile composes these addressable coordinates:

```text
calendar   = 31922:<organizer-pubkey>:<d-tag>
          | 31923:<organizer-pubkey>:<d-tag>
collection = 30405:<collection-author-pubkey>:<d-tag>
product    = 30402:<merchant-pubkey>:<d-tag>
pickup     = 30406:<handler-pubkey>:<d-tag>
```

The full kind, author, and `d` value identify each record. A `d` value by
itself does not identify an event, collection, product, or pickup option.

An event-market collection MUST contain exactly one `a` tag whose coordinate
kind is NIP-52 `31922` or `31923`. The coordinate kind distinguishes this
calendar reference from kind-`30402` product membership. A collection with no
NIP-52 reference remains an ordinary Open Markets collection.

A kind `31924` NIP-52 calendar MAY independently group multiple calendar
events. It is not the product catalog and is not required by this profile.

## Event-market collection

An event-market collection uses kind `30405` and contains:

- required `d` and `title` tags from the existing collection contract;
- exactly one `a` reference to a kind `31922` or `31923` calendar event;
- zero or more `a` references to exact kind-`30402` product coordinates;
- exactly one canonical `event_market` lifecycle declaration for new writers,
  plus at most one agreeing legacy alias during migration;
- optional existing collection display and location metadata;
- zero or one organizer-operated pickup option for this profile.

Product references are zero-or-more so an organizer MAY publish an upcoming
event before accepting any products. This is a narrow relaxation of the
current collection text, which lists a product `a` tag as required while also
allowing collections to contain any number of products.

Clients MUST classify `a` references by coordinate kind. A calendar reference
MUST NOT become a product, and an unknown reference kind MUST NOT silently gain
calendar, product, organizer, or fulfillment authority.

Multiple NIP-52 references are conflicting evidence for this profile. Clients
MUST NOT select one implicitly.

For version 1, collection inheritance is conflicting only when it resolves more
than one eligible organizer-authored option whose `service` is `pickup`. Other
collection shipping options retain their existing meaning. A product that
directly selects a valid merchant-authored pickup remains independent of the
organizer inheritance path.

## Organizer provenance

When the collection and linked NIP-52 calendar event have the same author,
clients MAY describe the collection as organizer-authored. When the authors
differ, the collection is third-party curation unless another explicit trust
mechanism establishes the relationship.

Cryptographic authorship establishes provenance. It does not establish the
author's reputation, physical control of the venue, or authority over another
merchant's products, orders, inventory, or payments.

NIP-52 participant tags, calendar membership, and RSVP events do not imply
merchant enrollment, product acceptance, payment authority, or fulfillment
authority.

## Product participation

A merchant MAY place an `a` reference to the event-market collection on its
kind-`30402` product. This is a discoverability claim and a request for
inclusion. It does not grant official membership.

The current valid organizer collection revision is authoritative for the set
of exact product coordinates selected by the collection author. Clients MAY
describe a product as an accepted event participant only when:

1. the current product revision references the exact collection coordinate;
2. the current collection revision references the exact product coordinate;
3. the collection is organizer-authored under this profile; and
4. neither reference is invalidated by stronger current deletion or conflict
   evidence.

A one-sided merchant reference MUST NOT be presented as organizer approval. A
one-sided organizer reference MAY be presented as organizer curation, but MUST
NOT be presented as merchant-confirmed event participation.

The organizer accepts or removes a product by replacing the same collection
coordinate. This does not rewrite the merchant's product and does not transfer
product authorship, price, stock, payment, or order authority.

## Commerce lifecycle

NIP-52 `start` and `end` describe the advertised schedule. They do not state
whether the organizer currently accepts new event-market orders or product
admissions.

New event-market collection writers MUST include exactly one canonical,
versioned lifecycle tag:

```text
["event_market", "1", "open"]
["event_market", "1", "closed"]
```

The tag applies only to a valid event-market collection. It does not turn an
ordinary collection into an event market and does not grant authority when the
calendar, collection, authorship, membership, or fulfillment graph is invalid.

The states have these meanings:

- `open`: the organizer accepts new event commerce and product admissions.
  Clients MAY initiate new purchases only for otherwise valid, mutually
  accepted products. The event MAY remain open after its advertised NIP-52
  end.
- `closed`: the organizer does not accept new event commerce or product
  admissions. The event MAY close before its advertised NIP-52 end.

These states describe commerce availability, not whether the physical venue is
currently open. A later valid collection revision MAY reopen a closed market.
Neither state proves product stock, current price, merchant consent, payment
authority, or fulfillment readiness.

Closure is not deletion. It MUST NOT erase the event, remove its history,
cancel an existing order, invalidate a prior payment, or prevent recovery and
fulfillment that remain authorized by their original exact terms.

Closed events MUST NOT authorize a new order, replacement invoice, or new
payment attempt. Existing merchant-issued invoice authority, settlement
inspection, payment-proof recovery, and fulfillment MAY continue only under
their independently validated original terms. Closure never authorizes a
duplicate charge or a weaker recovery check.

When neither a supported canonical lifecycle declaration nor a recognized
compatibility declaration is present, lifecycle metadata is in a legacy state.
A legacy event-market collection is open before the linked calendar's effective
NIP-52 end and closed at or after that end. Only an explicit
organizer-authored lifecycle declaration opts the collection into manual close
and reopen behavior.

A lifecycle-aware writer MUST preserve the declaration when changing products,
pickup references, or display metadata. A lifecycle-only update MUST preserve
the collection content and every non-lifecycle tag. Duplicate, malformed, or
unsupported lifecycle declarations are unusable evidence and MUST NOT
authorize new commerce. Clients MAY still show the catalog with an unsupported
or conflicting status when doing so cannot be mistaken for purchase authority.

A client that allows existing-order continuity across a lifecycle-only update
MUST compare the exact signed revisions and verify that content and every
non-lifecycle tag are identical. A revision that also changes membership,
pickup, or other terms is not lifecycle-only.

A reader that retained a valid declaration and then observes a newer revision
that omits every supported canonical and recognized compatibility declaration
SHOULD treat the lifecycle as conflicting rather than silently reverting to
legacy behavior. A reader with no prior evidence can only apply the legacy
fallback. This limitation follows from addressable event replacement and does
not create global history or locking.

## Pickup profile

A fixed pickup option uses kind `30406` with the existing required `d`, `title`,
`price`, `country`, and `service` tags. `service` MUST be `pickup`, and the
option MUST include a public `location` and/or `g` value.

An organizer-authored event-market collection MAY advertise one exact
organizer-authored pickup coordinate through `shipping_option`. Omitting it
means the organizer is not offering to perform handoff. It does not prevent an
accepted merchant from selecting a merchant-authored pickup option for its own
booth.

A participating product MAY select fixed pickup by:

- directly referencing the exact kind-`30406` pickup coordinate; or
- referencing the event-market collection through `shipping_option`, in which
  case the client MUST resolve the current collection revision and its exact
  organizer pickup coordinate.

Collection membership alone does not grant or imply a fulfillment option.
When the selected pickup author is the product merchant, clients MAY present
merchant-operated booth pickup. When the pickup author is the organizer and
the current organizer collection advertises that exact option, clients MAY
present organizer-operated pickup. A third-party pickup author requires a
separate explicit authorization contract and MUST NOT silently receive either
role.

The product, collection, calendar, and pickup retain distinct identities and
authors throughout checkout and order handling. Pickup cost and currency come
from the exact selected pickup revision and any product-level extra cost
already defined by the current Open Markets contract.

## Orders and authority

This proposal does not define or replace an order-message envelope. Whichever
compatible order protocol an implementation uses, a pickup order MUST bind the
exact selected kind-`30406` coordinate. A fixed pickup does not require a buyer
delivery-address field or carrier and tracking flow.

The buyer's order remains directed to the product merchant. Event membership
or organizer-operated pickup does not grant the organizer authority to:

- receive the buyer's full order, address, contact information, or notes;
- change product price, stock, merchant identity, or payment destination;
- confirm merchant payment, cancel or refund an order, or author the merchant's
  ordinary order status;
- release merchandise without a separate private merchant authorization.

Private organizer handoff authorization, revocation, and acknowledgement are
outside this public collection profile. They require a separate protocol that
binds exact order and graph revisions and minimizes disclosed buyer data.

## Resolution and relay evidence

Implementations MUST apply NIP-01 addressable replacement and NIP-09
author-scoped deletion semantics independently to the calendar, collection,
product, and pickup records.

A relay `OK` response proves acceptance by that relay. It does not prove global
visibility, recipient observation, or semantic confirmation. An empty, capped,
timed-out, or partially failed relay read does not prove global absence.

Clients SHOULD preserve source, freshness, and bounded coverage where those
facts affect presentation or an irreversible action. Browsing MAY use retained
signed evidence with an honest degraded state. New commerce MUST validate the
current positive calendar, collection, product-membership, lifecycle, and
pickup evidence required by the selected flow.

Implementations SHOULD distinguish missing, partial, unavailable, stale,
deleted, malformed, conflicting, and unsupported evidence instead of reducing
all unsuccessful observations to absence.

## Interoperability example

The following excerpts omit standard event envelope and signature fields. They
show all relationship and lifecycle tags defined by this profile; each event
must also satisfy its underlying NIP-52 or Open Markets contract.

Organizer `O` publishes a timed calendar event and an optional pickup:

```text
31923:O:event-2026
  ["d", "event-2026"]
  ["title", "Community Market"]
  ["start", "1786208400"]
  ["end", "1786230000"]
  ["D", "20673"]
  ["start_tzid", "America/New_York"]
  ["location", "Public Hall, Main Entrance"]

30406:O:event-2026-pickup
  ["d", "event-2026-pickup"]
  ["title", "Event pickup"]
  ["price", "0", "USD"]
  ["country", "US"]
  ["service", "pickup"]
  ["location", "Public Hall, Main Entrance"]
```

Organizer `O` can then publish an open event market before accepting products:

```text
30405:O:event-2026-market
  ["d", "event-2026-market"]
  ["title", "Community Market"]
  ["event_market", "1", "open"]
  ["a", "31923:O:event-2026"]
  ["shipping_option", "30406:O:event-2026-pickup"]
```

Merchant `M` requests inclusion and explicitly selects the organizer pickup:

```text
30402:M:product-1
  ["d", "product-1"]
  ["title", "Market product"]
  ["price", "12", "USD"]
  ["type", "simple", "physical"]
  ["a", "30405:O:event-2026-market"]
  ["shipping_option", "30406:O:event-2026-pickup"]
```

The request remains pending while the collection is empty. Organizer `O`
accepts it by replacing the collection with the same `d` tag and adding:

```text
["a", "30402:M:product-1"]
```

Removing that product coordinate from a newer collection revision removes
official participation without rewriting the merchant's product.

A merchant-operated booth uses the same calendar and membership graph while
the product instead selects merchant `M`'s pickup:

```text
30406:M:booth-pickup
  ["d", "booth-pickup"]
  ["title", "Merchant booth pickup"]
  ["price", "0", "USD"]
  ["country", "US"]
  ["service", "pickup"]
  ["location", "Public Hall, Booth 12"]

30402:M:product-1
  ["d", "product-1"]
  ["title", "Market product"]
  ["price", "12", "USD"]
  ["type", "simple", "physical"]
  ["a", "30405:O:event-2026-market"]
  ["shipping_option", "30406:M:booth-pickup"]
```

Organizer `O` closes new event commerce by replacing the collection and
changing only the lifecycle state:

```text
["event_market", "1", "closed"]
```

The calendar schedule and historical catalog remain visible. Existing orders
continue under their independently authorized terms.

## Compatibility and migration

This profile is additive:

- existing collection clients can ignore the NIP-52 and `event_market` tags and
  continue reading product and shipping references;
- NIP-52 clients can read the calendar event independently;
- ordinary collections without a calendar reference retain their current
  meaning;
- a calendar event can exist without an event-market collection;
- no new event kind or migration to NIP-15 stalls is required.

An early implementation used the application-namespaced lifecycle declaration:

```text
["conduit_event_market", "1", "open|closed"]
```

The canonical proposal uses `event_market`. A migrating implementation MAY
temporarily emit both declarations with the same state so older readers retain
the explicit lifecycle. A reader that understands both declarations MUST
require their versions and states to agree. A mismatch is conflicting evidence
and MUST NOT authorize new commerce. Unknown namespaced tags MUST otherwise be
preserved during collection updates.

A migration-aware reader MAY interpret the namespaced declaration with the same
version 1 semantics when no canonical declaration is present. Once the
canonical declaration is present, it is required for interoperable lifecycle
state; the namespaced declaration is compatibility evidence only. An unknown
canonical version remains unsupported even when a recognizable namespaced
declaration is also present.

After supported readers understand `event_market`, writers SHOULD stop emitting
the namespaced declaration. Implementations MUST NOT silently reinterpret or
drop previously observed signed lifecycle evidence during migration.

Clients that do not implement this proposal may ignore lifecycle declarations
and apply different schedule-based behavior. An organizer therefore cannot
infer network-wide closure merely from publishing `closed`; interoperable
clients implementing this proposal must honor it for new commerce.

## Conformance cases

Implementations of this proposal should cover at least:

1. an empty upcoming date-based and timed event market;
2. an event market with and without organizer pickup;
3. merchant request, organizer acceptance, and organizer removal;
4. organizer-listed but merchant-unconfirmed products;
5. merchant-operated booth pickup;
6. organizer-operated pickup selected directly and through the collection;
7. open commerce after the advertised end and early explicit closure;
8. legacy lifecycle fallback and migration from a namespaced declaration;
9. lifecycle-only updates preserving all non-lifecycle collection data;
10. third-party curation, cross-author pickup, and multiple calendar references;
11. malformed coordinates, duplicate lifecycle tags, deletion, and conflicting
    revisions;
12. partial or unavailable relay reads that do not become global absence; and
13. ordinary kind-`30405` collections as a negative control.

## Implementation evidence and open work

The public collection graph, two-sided membership, pickup profile, and
equivalent lifecycle behavior have implementation and deterministic fixture
coverage in [Conduit](https://github.com/Conduit-BTC/conduit-mono), including
the namespaced lifecycle work in
[Conduit PR #482, "Separate event availability from scheduled hours"](https://github.com/Conduit-BTC/conduit-mono/pull/482).
The neutral-tag dual-read and dual-write migration proposed here is not yet
implemented. Conduit is evidence for review, not authority over this proposal.

Independent implementation and cross-client fixtures remain desirable before
this proposal advances from experimental to normative status. Private organizer
handoff should be evaluated separately against whichever order and private
message contracts Open Markets adopts.
