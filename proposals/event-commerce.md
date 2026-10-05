# NIP-52-backed Event Markets

Status: experimental proposal. This page is not current normative Open Markets text.

This proposal adds a dedicated, organizer-signed Event Market record, per-merchant causal authorization, and merchant-signed assignments of existing standard products to specific occurrences. A market may link one concrete NIP-52 occurrence or one organizer-authored finite kind `31924` calendar whose current signed revision lists concrete occurrences. Client-side weekly generation publishes ordinary NIP-52 events and a finite calendar list; this profile defines no RRULE or recurring scheduler. The organizer controls merchant admission, commerce state, and public handoff labels. Approved merchants control their own products, shipping, inventory, prices, and payment destinations. Occurrence assignments add optional pickup and temporary variant-level stock allocation without creating event-specific products or requiring individual organizer product approval. Signed parent relationships make observed stale or concurrent approval edits detectable; relay observation never proves that no unseen event exists.

## Public sources and kind allocation

- [NIP-01 addressable events, tags, filters, and replacement](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [NIP-09 author-scoped deletion](https://github.com/nostr-protocol/nips/blob/master/09.md)
- [NIP-19 shareable addresses](https://github.com/nostr-protocol/nips/blob/master/19.md)
- [NIP-52 calendar events](https://github.com/nostr-protocol/nips/blob/master/52.md)
- [NIP-65 relay list metadata](https://github.com/nostr-protocol/nips/blob/master/65.md)
- [NIP-67 EOSE completeness hint](https://github.com/nostr-protocol/nips/blob/master/67.md)
- [NIP-77 Negentropy syncing](https://github.com/nostr-protocol/nips/blob/master/77.md)
- [NIP-99 classified listings](https://github.com/nostr-protocol/nips/blob/master/99.md)
- [Nostr kind registry](https://github.com/nostr-protocol/registry-of-kinds/blob/master/schema.yaml)
- [Current Open Markets compatibility snapshot](../SPEC.md)

Kinds `30409`, `30410`, and `3841` are proposed for this experimental profile. In the public registry checked on 2026-10-05 they are unassigned; they are not registered kinds. `30409` and `30410` are addressable, and `3841` is a regular immutable event. Current Open Markets text uses `30402` for products, `30405` for collections, and `30406` for shipping options. Those existing kinds retain their current meaning. The occurrence cancellation tag and encrypted order extension below are also experimental profile requirements, not changes to NIP-52 or the current Open Markets specification.

## Scope and coordinates

```text
occurrence = 31922:<organizer-pubkey>:<occurrence-d>
           | 31923:<organizer-pubkey>:<occurrence-d>
schedule   = 31924:<organizer-pubkey>:<schedule-d>  // series only
market     = 30409:<organizer-pubkey>:<market-d>
auth       = (market coordinate, merchant pubkey)
product    = 30402:<merchant-pubkey>:<product-d>
assignment = 30410:<merchant-pubkey>:<assignment-d>
```

The full kind, author, and `d` value identify each addressable record. A `d` value alone is insufficient. The linked `31922` or `31923` gives one advertised occurrence and venue. Alternatively, the linked `31924` is a finite schedule container; its current signed revision lists concrete `31922` and `31923` occurrences. The `30409` remains the sole organizer commerce authority in either case. The organizer MUST author the market, its linked schedule, and every commerce-relevant member occurrence. Only exact full coordinates in the current signed `31924` revision establish series membership. A child event's `a` tag requesting calendar inclusion does not establish membership, nor does an RSVP. A current market roster row and a valid active per-merchant grant are both required for admission. NIP-52 participant tags do not grant merchant admission.

This proposal does not define ticketing, check-in, global event discovery, payment custody, a new order envelope, or private handoff messages. It does not redefine ordinary kind `30405` collections or kind `30406` shipping options.

## Event Market record: kind `30409`

The market MUST be signed by the same pubkey that authored its linked NIP-52 occurrence or kind `31924` calendar. A series member used for commerce MUST also be authored by that pubkey. Its current signed revision contains:

- exactly one nonempty `d` tag, at most 128 UTF-8 bytes;
- exactly one `a` tag referencing an organizer-authored kind `31922` or `31923` occurrence coordinate, or one organizer-authored kind `31924` schedule coordinate;
- exactly one `event_market` tag with version `2` and state `open` or `closed`;
- zero to 128 `merchant` rows, each with a unique merchant pubkey, one mode, and a nonempty public assignment;
- exactly one `prev` tag on an update, referencing the signed market revision the organizer edited from; the initial revision has none; and
- optional display tags such as `title`, `summary`, and `image`, without making them authority for schedule, admission, price, or payment.

```text
["d", "<market-id>"]
["a", "31922:<organizer>:<occurrence-id>"]  // one-date market
// Or exactly one ["a", "31924:<organizer>:<schedule-id>"] for a series
["event_market", "2", "open|closed"]
["merchant", "<merchant-pubkey>", "merchant_present|organizer_handoff", "<public-assignment>"]
["prev", "<prior-market-event-id>"]  // updates only
```

Each merchant pubkey is 64 lowercase hexadecimal characters. The roster assignment is a public booth or pickup label (distinct from a merchant product assignment of kind `30410`) of at most 120 UTF-8 bytes, with no control characters. The serialized signed event MUST fit within 64 KiB. The `merchant` row is a multi-letter tag; clients fetch the known market coordinate and read its finite roster rather than assuming relays index that tag. A duplicate merchant row, unknown mode, malformed row, over-limit record, wrong occurrence or schedule author, multiple calendar links, or duplicate lifecycle tag is unusable admission evidence. Clients MUST NOT choose one of two conflicting rows.

`merchant_present` means the merchant handles physical handoff at the public assignment. It does not itself prove that a buyer or merchant is currently present. `organizer_handoff` means the organizer performs physical handoff at the public assignment under a separate order-specific release authorization. Neither mode transfers product, inventory, price, payment, or full-order authority from the merchant. The organizer may change the mode or assignment in a later signed roster revision.

Approval requires both a current roster row and an active causal grant for the same market and merchant. There is no separate approval boolean or organizer list of product coordinates. A market with zero merchants is valid before enrollment. Removing a row or signing a descendant revoke removes that merchant's products from the event catalog without modifying the shop. Reapproval requires a new descendant grant and a current row; it makes every still-valid active occurrence assignment eligible again, subject to its occurrence and inventory checks. Organizer clients SHOULD disclose that effect before reapproval. A grant without a row has no event mode or handoff label and cannot authorize event participation; a row without a grant cannot authorize it either.

## Merchant enrollment and occurrence assignments

A request or invitation concerns a merchant pubkey and one market coordinate, not particular products. The request transport is outside this public profile; a client using one MUST authenticate the requesting merchant or inviting organizer. A request or invitation does not grant admission. Only a valid current organizer-signed roster row together with an active causal grant does.

### Wire choice: a separate proposed kind 30410

An occurrence assignment has an independent replacement and removal lifecycle. Embedding allocation rows in `30402` would make every occurrence edit replace the ordinary product and mix several occurrences' inventory and fulfillment state into one listing revision. Reusing `30405` or `30406` would change their existing collection or shipping semantics. This profile therefore proposes one small merchant-signed addressable kind `30410`, without a new product type, private variant identifier, or series-wide inventory record.

Each assignment binds one market, one concrete occurrence, and one existing sellable `30402`. A simple product is assigned directly. For a variable product, each offered variation has its own assignment referencing the existing `type=variation` product coordinate; its current signed `a` parent reference MUST resolve to a `type=variable` product by the same merchant. A variable parent itself is not a sellable allocation target. Different variations have independent stock and allocations; clients MUST NOT subtract variation stock again from a parent aggregate.

The assignment author MUST equal the product author. The market and occurrence MUST have the same organizer author. For a one-date market, the occurrence MUST equal the market's linked occurrence. For a series, it MUST be an exact member of the current signed schedule. A schedule coordinate is never an allocation target. All coordinates use canonical decimal kinds, lowercase hexadecimal pubkeys, and the exact `d` string, parsed by splitting only the first two colons.

The assignment's `d` is the lowercase hexadecimal SHA-256 of the UTF-8 serialization of `[market, occurrence, product]`, in that order, using NIP-01's compact JSON string escaping rules with no Unicode normalization. This deterministic identifier gives one assignment coordinate per tuple per merchant, prevents duplicate counting, and changes for every new occurrence. A different `d` for the same tuple is invalid.

Tuple-hash test vector (serialize the following array compactly before hashing):

```json
[
  "30409:1111111111111111111111111111111111111111111111111111111111111111:fair-market",
  "31923:1111111111111111111111111111111111111111111111111111111111111111:fair-week-1",
  "30402:2222222222222222222222222222222222222222222222222222222222222222:soap"
]
```

Expected `d`: `3fd6f9c22e854c3ebb1c76ea8b9538f8fa0b8a3219559d2a955f82b263b12367`.

The content is empty. The profile tags are:

```text
["d", "<64-lowercase-hex tuple hash>"]
["openmarkets", "event-market-assignment", "1"]
["a", "30409:<organizer>:<market-d>"]
["a", "31922:<organizer>:<occurrence-d>"]  // or 31923, never 31924
["a", "30402:<merchant>:<simple-or-variation-d>"]
["state", "active|removed"]
["inventory", "tracked", "<remaining-pickup-allocation>"]
// Or exactly one ["inventory", "untracked"], with no quantity
["fulfillment", "pickup"]    // zero or one per supported method
["fulfillment", "shipping"]
["fulfillment", "digital"]
["prev", "<prior-assignment-event-id>"]  // updates only
["alt", "Open Markets occurrence product assignment"]
```

The `d`, profile marker, state, inventory, and `alt` are singletons with the exact shapes shown. There are exactly three `a` tags, distinguished by kind; each MAY have a third element containing a relay hint. There is exactly one `prev` on an update and none on the initial revision. Event IDs and hashes are 64 lowercase hexadecimal characters. At least one distinct fulfillment method is required on an active assignment. A removed revision retains its tuple, uses `["inventory", "tracked", "0"]` or `["inventory", "untracked"]`, and has no fulfillment tags. Unknown states, inventory modes or methods, duplicate methods or singleton tags, wrong authors, malformed references, and records exceeding 64 KiB serialized signed size cannot authorize commerce. Additional display tags cannot override these fields.

An active tracked assignment requires a current nonnegative integer `stock` on the sellable product. Its allocation is a canonical decimal integer from `0` through `2_147_483_647`, with no sign or leading zeros except `0`, and cannot exceed that product's remaining stock. An untracked assignment requires that product to omit `stock`; it carries no numeric allocation. Missing stock is never interpreted as zero or infinite guaranteed supply. Changing stock tracking mode requires the merchant to reconcile all current assignments for that product.

Pickup is permitted only for a physical product and uses the current organizer roster mode, public handoff label, and signed occurrence venue. The merchant enables or disables this method on the assignment but cannot replace the organizer's handler or booth, add an event fee, or grant itself admission. A physical product MAY also offer shipping. A digital product uses digital fulfillment and MUST NOT offer physical pickup or shipping. A positive tracked allocation requires pickup to be enabled; remote shipping-only or digital assignments use zero allocation when tracked.

Shipping remains product-owned. The product's existing `shipping_option` references, explicitly referenced collections, merge rules, constraints, and prices determine available shipping methods. Assignment does not edit, inherit, suppress, or replace them. The assignment's shipping method is usable only when an ordinary product-authorized non-pickup `30406` option is valid for the purchase; a roster row never creates a shipping option. Event pickup is an additional capability under this experimental profile, not a mutation of `30402` or a new `30406` event.

Once admitted, a merchant may publish, edit, replace, hide, or delete its standard products and publish or remove assignments without a separate organizer product decision. A hidden, invalid, or validly deleted current product cannot be sold through its assignment. A `30402` market `a` tag, if retained from an earlier experimental reader, is only a discovery hint: it is neither necessary nor sufficient for occurrence participation. Untagging a product does not remove a separate assignment; explicit removal replaces `30410` with `state=removed`.

### Replacement, expiration, and inventory

Readers resolve current assignments under NIP-01 ordering and retain stronger signed revision and applicable author-scoped NIP-09 evidence. An observed removed or deleted assignment cannot fall back to an older active revision. A malformed or unsupported strongest observed current revision blocks use of the tuple; readers MUST NOT select an older usable revision instead. A later deliberate active revision may restore a removed assignment at the same still-eligible occurrence, subject to all current inventory checks; it does not resurrect deleted revisions. Writers MUST compare the strongest observed current assignment, reject an edit based on an older known revision, preserve the tuple, and reference that revision with `prev`. The referenced payload MUST validate to the same tuple and author. Known divergent roots or parent branches with material quantity, state, or fulfillment differences block new purchases using that assignment until the merchant reviews them and publishes a revision based on the strongest observed winner. A missing parent needed to resolve a known conflict is incomplete evidence, not an active assignment. As with market updates, `prev` exposes observed concurrency but provides no global compare-and-swap.

An allocation reserves only unsold, uncommitted stock for its named occurrence, including before its start. It stops counting automatically at the occurrence's exclusive end, on observed organizer cancellation, or on explicit merchant removal or applicable deletion of the assignment. These transitions release only unused allocation; they do not restore sold stock or cancel outstanding orders. No expiration revocation is needed, and signed history is retained. Hiding a product, closing a market, revoking admission, or dropping a schedule member disables relevant new purchases but does not prove physically allocated inventory returned; the merchant explicitly removes the allocation to release it early. Missing or unavailable occurrence evidence does not prove expiry or release.

For each tracked sellable product, let `S` be its current remaining total `stock`, excluding already accepted commitments; let `q_i` be each current tracked assignment's remaining allocation whose occurrence has not ended or been cancelled and whose assignment has not been removed or deleted. Across all markets and occurrences, count each deterministic assignment coordinate once. Then:

```text
reserved pickup stock = sum(q_i)
ordinary shipping/digital stock = max(0, S - sum(q_i))
pickup stock at occurrence i = q_i, subject to current admission and fulfillment
```

An observed allocation sum greater than `S`, tracking-mode mismatch, or unresolved allocation conflict requires merchant reconciliation before promising new stock. Buyers cannot establish that sum is globally complete from relay discovery. Merchant inventory acceptance MUST account for all of its commitments and allocations, including those a buyer has not discovered. Untracked products expose availability subject to merchant acceptance, without manufactured quantities.

An accepted tracked pickup quantity `n` consumes `S` and that occurrence's `q_i` exactly once. For untracked inventory, acceptance records the order commitment without inventing a counter. Tracked shipping or digital fulfillment consumes only ordinary stock and `S`, leaving pickup allocations unchanged. The merchant MUST serialize its own acceptance and use the order ID to prevent retries, payment notifications, or publication retries from consuming inventory twice. Updating `30402` stock and `30410` allocation is not atomic across relays; signed assertions, relay acknowledgments, and a cart do not themselves reserve or prove availability. Intermediate inconsistent observations cannot authorize a new inventory promise. Existing payment and order acceptance remain merchant-controlled.

Rollover publishes a new assignment for a different concrete occurrence and may copy the merchant-confirmed unused quantity. It never retargets the old tuple or allocates stock to `31924`. After natural expiry or cancellation, the old allocation no longer counts. Before then, a transfer explicitly removes or reduces the old assignment before increasing the new one; it MUST NOT count the same stock at both occurrences or move existing order commitments. Partial publication requires reconciliation before further acceptance.

## Causal merchant authorization

The organizer's current `30409` row supplies the merchant's event mode and
public assignment. A separate organizer-authored causal history protects
merchant-level grants and revocations from **observed** stale or concurrent
writes. Both a current row and an active grant are required for new commerce.
Neither a product tag, merchant assignment, nor a relay response grants authority by itself.

### Authorization transition: proposed regular kind 3841

Each immutable transition is signed by the organizer named in the market
coordinate and scoped to `(market coordinate, merchant pubkey)`. Its content
is empty. The profile tags are:

```text
["openmarkets", "event-market-auth", "1"]
["a", "30409:<organizer>:<market-d>"]
["p", "<merchant-pubkey>"]
["state", "active" | "revoked"]
["seq", "<canonical-nonnegative-decimal>"]
["auth_parent", "<parent-transition-id>"]  // zero on a root, 1..8 otherwise
["repair", "<kind5-id>", "<deleted-transition-id>"]  // only on repair
["alt", "Open Markets event merchant authorization"]
```

The profile marker, market coordinate, merchant, state, sequence, and `alt`
are singletons. Parent IDs MUST be distinct; a transition has at most eight
parents. The multi-letter `auth_parent` tag is a causal reference; clients
retrieve the signed parent by its exact event ID. The organizer pubkey in the
`a` coordinate MUST equal the transition author. A parent MUST be a validated transition with the same
market coordinate and merchant. A root has no parents and `seq = 0`; every
non-root has `seq = 1 + max(parent.seq)`. The maximum sequence is
`2_147_483_647`. Clients recompute it from signed parents. Timestamps,
sequence magnitude, event IDs, relay order, and state text do not choose a
winner among concurrent branches.

When exactly one observed causal tip exists, `active` with validated
observed ancestry satisfies the grant gate and `revoked` denies it. Multiple
incomparable observed tips are `CONFLICTING`, even when they state the same
value, and block new commerce.
An intentional regrant must descend from the revoked tip. A reconciliation
must descend from every observed conflicting tip. Missing required parent
payloads or an observed unresolved deletion also block new commerce. A
later-discovered branch reopens the conflict; it does not rewrite an order
created under an earlier exact snapshot. The reducer makes no claim about
unseen branches.

To revoke merchant approval, the organizer MUST sign a descendant
`revoked` transition, publish it to the organizer's advertised write relays when available (using
appropriate fallback relays otherwise), and remove the market row. Relay
acceptance does not prove every client saw it. A removed row immediately
denies participation to a client that observes it; the causal revoke protects
against a later stale row edit restoring an unchanged active grant. An
intentional reapproval requires a descendant `active` transition and a
current row with one mode and assignment. Changing only mode or assignment
does not require another grant or product republication.

### Relay discovery and observation

Clients SHOULD resolve the organizer's best observed signed NIP-65
kind-`10002` relay list and query its advertised **write** relays for organizer-authored
`30409`, kind-`3841` transitions, and relevant kind-`5` deletion
requests. In NIP-65, an `r` tag without a marker is both read and write.
Relay hints attached to references and locally configured fallback relays MAY
supplement discovery, particularly when NIP-65 is missing, stale, or
unavailable. NIP-65 and relay hints locate possible evidence; neither is
authorization, an exhaustive source list, or a guarantee of currentness.

For one merchant, a bounded transition candidate filter uses organizer
author, kind `3841`, `#a` market coordinate, and `#p` merchant. Clients
fetch referenced parent IDs as needed. They query organizer-authored kind-`5`
by known transition and market revision IDs and market coordinate, and MAY
also use organizer/market/merchant scope tags when present. Product and assignment deletion evidence is sought from the merchant's NIP-65 write
relays, supplemented by hints and fallbacks, by known revision IDs and coordinates.
They union valid signed observations from the selected relays and
retain previously observed stronger revocation, deletion, fork, and newer
market-revision evidence. A later stale or empty response cannot erase it.
An unavailable relay is incomplete observation, not proof of absence and not
an automatic veto when other evidence is adequate for the transaction.

NIP-67 `finish`, NIP-77 reconciliation, and ordinary EOSE MAY improve
synchronization with an individual relay. They do not establish that the
client has a complete organizer history or that no relay hid or pruned an
event. This profile requires no fixed event-specific relay set, relay quorum, or
historical-completeness proof.

### Deletion evidence and actionability

Organizers SHOULD change authorization with kind-`3841` transitions rather
than NIP-09 deletion requests. A valid **observed** organizer-authored
kind-`5` request that targets a known transition is negative evidence. It
does not subtract the transition, select an older active ancestor, or erase a
known conflict. A deletion request whose target payload is unavailable is
unresolved when its market/merchant scope can be established from signed
evidence; it blocks new commerce for that scope. A repair transition MAY
name the exact deletion and target in a `repair` pair, descend from every
observed tip including the affected branch, and supply enough retained signed
payload to validate ancestry. An unrelated deletion is not repaired by that
pair. Clients retain observed deletion evidence even if later relays omit it.

A standard NIP-09 request may contain only a target `e` tag. If the client
has never seen that target, it may be unable to associate the request with
this merchant. Publishers SHOULD include the market `a` and merchant `p`
scope tags on authorization-deletion requests to improve discovery, but
their absence does not invalidate NIP-09. The proposal does not claim that a
client can discover every deletion or prove a negative from relay silence.

For new commerce, the client needs positive signed evidence of a current
open market, current merchant row, valid NIP-52 link (including a current
signed schedule and selected member occurrence for a series), active observed causal
tip, current valid merchant product, and current active occurrence assignment
supporting the selected fulfillment and inventory pool. It MUST block a known unresolved
authorization conflict or deletion and MUST fail closed when it cannot
obtain adequate positive current evidence for the transaction. The client
chooses its relay coverage and freshness policy; any admission claim is
relative to the signed evidence it actually observed and retained.

## Commerce lifecycle

The versioned `event_market` state supplies the market-wide commerce gate:

- `open`: new event purchases may proceed only if the current organizer roster, active merchant grant, occurrence, assignment, product, chosen fulfillment, inventory, and payment terms are valid.
- `closed`: no new event purchases or new payment attempts may start. The organizer may reopen by signing a later valid revision.

### Occurrence end and cancellation

NIP-52 does not define cancellation. This profile permits at most one organizer-signed `["event_occurrence", "1", "scheduled|cancelled"]` tag on each linked `31922` or `31923` revision; omission means scheduled. A duplicate, unknown version, or unknown state is unusable occurrence evidence. Only the occurrence author can cancel it. An observed cancelled revision is terminal for this occurrence coordinate in this profile; an organizer uses a new coordinate for a replacement date. Clients retain cancellation evidence and MUST NOT let a later scheduled revision or stale relay response reactivate its allocations. Applicable organizer-authored NIP-09 deletion that removes the currently actionable occurrence also blocks new commerce and releases unused allocations when its exact scope is established; deletion of an older superseded revision alone is not cancellation of the current occurrence. An unresolved deletion whose scope or applicability cannot be validated blocks affected purchases and does not establish inventory release.

For a timed `31923`, this profile requires a valid explicit `end > start` for allocation and new event commerce. NIP-52 permits an omitted end, but its instantaneous default is insufficient for a pickup window here. For a date-based `31922`, use the NIP-52 exclusive `end` date, or the day after `start` when end is omitted. For deterministic inventory expiry, date boundaries in this profile are 00:00 UTC; clients SHOULD display that boundary before a merchant allocates stock. These rules do not change NIP-52 for other clients.

At or after that exclusive end, the occurrence cannot authorize new event commerce and its unused allocations cease to reserve stock, for both one-date and series markets and every fulfillment method. Ended occurrence coordinates MUST NOT be reused for a future allocation; rescheduling an ended or cancelled occurrence requires a new coordinate and new merchant assignments. Known ended/cancelled evidence cannot be erased to restore an old allocation. For a series, an otherwise current or future occurrence must additionally belong to the current signed schedule. Expiry or cancellation of one occurrence does not close the whole market or another date. An open market cannot make an expired allocation usable.

Closing or changing a market does not delete its history, cancel an existing order, invalidate a prior payment, or prevent independently authorized settlement inspection and fulfillment. A valid market lacking the required versioned state cannot authorize new commerce. An unsupported, malformed, deleted, or legacy version-1 current revision is not a fallback to an older version-2 revision or calendar time. Version-1 `30409` records never synthesize causal grants.

There is no separate buyer event-pickup fee. A merchant accounts for event costs in their product prices and remains the payee even when the organizer performs physical pickup.

## Resolution and discovery

Clients start from a known market coordinate, resolve its signed current version-2 revision and linked NIP-52 occurrence or schedule, then derive the finite roster author set. For a series, clients resolve the strongest observed current signed `31924` revision under NIP-01 ordering, then fetch its member coordinates in bounded batches. They validate each member's signature, exact coordinate, organizer author, NIP-52 fields, profile cancellation state, and applicable author-scoped NIP-09 evidence. Duplicate, malformed, or cross-author member references cannot authorize a selected occurrence. A member's request to join the schedule without a current schedule reference is insufficient. They query kind `30410` by roster authors and `#a` market coordinate as a bounded candidate plan, then validate the exact occurrence and product references locally. Multiple values within a NIP-01 `#a` filter are OR, so listing market and occurrence in one filter is not an intersection. Product and variation-parent payloads are fetched by exact coordinates. Neither a filter hit nor an incomplete filter result proves admission or absence. Authorization reads remain scoped per merchant to the stable market coordinate.

Before showing a candidate as offered at an occurrence, including at a direct product link, a client MUST resolve the current signed product and deterministic assignment revisions and applicable NIP-09 deletion evidence, then validate their authors, tuple, product fields, visibility, inventory mode, fulfillment, and current occurrence against the current roster and active causal authorization. Without a current row, active grant, and active occurrence assignment, a product MUST NOT enter that occurrence's official catalog. An active zero-allocation assignment may remain listed with valid ordinary shipping or digital fulfillment; it cannot offer tracked pickup. A newer hidden product, removed assignment, or signed roster removal wins over older evidence returned by a lagging relay. A bare product link does not silently select an occurrence or fulfillment.

To estimate ordinary available stock, clients also query the merchant's `30410` assignments by author and `#a` sellable product coordinate across markets, resolve their current revisions and occurrence lifecycle evidence, and avoid duplicate counting. That read may be incomplete and is advisory; the merchant's authoritative acceptance must account for all allocations. Missing lifecycle evidence for a known allocation MUST NOT be treated as release or ordinary stock. Applicable retained removal, expiry, cancellation, and deletion evidence is evaluated under the lifecycle rules above.

NIP-01 orders addressable revisions by `created_at`, then lowest event ID at the same timestamp. NIP-09 deletion is author-scoped; a third party cannot remove a merchant listing or organizer market. Readers MUST retain stronger valid signed revision or deletion evidence they already hold instead of treating a partial or empty relay response as reversal. A partial sibling read does not prove another occurrence absent and need not invalidate an otherwise verified selected member. A missing, stale, divergent, or unresolved current schedule, or missing selected member payload, cannot authorize a new series pickup. An observed newer schedule that removes a date defeats an older schedule returned by a lagging relay; an empty response alone does not prove removal. A signed kind-`5` request is evaluated against its author's exact known target, and an unresolved observed deletion targeting the schedule or selected occurrence blocks new commerce on that evidence. Clients SHOULD expose partial, unavailable, stale, conflicting, malformed, and deleted observations where those distinctions affect a purchase. Relay `OK` means relay acceptance, not recipient observation or network-wide convergence.

Before signing a roster update, a writer MUST read and compare the strongest observed current market revision, preserve unaffected rows, and reject an edit based on an older known revision. The required `prev` reference on market updates exposes the parent used and helps detect divergent edits when both branches are observed. Multiple observed roots for one market coordinate are divergent too. NIP-01 does not provide a global compare-and-swap; a client cannot prove that no unseen concurrent revision exists. Known divergent market ancestry MUST be surfaced for organizer review. An unresolved material state or assignment conflict blocks new commerce until the organizer signs a reviewed revision based on the strongest observed winner. A stale market revision cannot restore a merchant whose known grant is revoked. New purchases require positive current market, occurrence, assignment, product, and authorization evidence; incomplete reads do not prove admission or removal by themselves. The same check applies to direct product links.

A schedule writer MUST compare the strongest observed current `31924` revision before replacing it, preserve unaffected member references, and surface an observed newer or conflicting revision instead of silently overwriting it. To extend a series, publish new signed occurrences before the schedule revision that references them. Removing a future date changes schedule membership; it does not require deleting its standalone NIP-52 event. Organizers SHOULD retain past members for timeline history. NIP-52 does not define a schedule `prev` tag or a global compare-and-swap; the writer cannot prove that no unseen concurrent revision exists.

## Checkout and historical orders

For an unpaid cart or a new payment attempt, clients resolve the current open market, merchant row and observed causal grant, current product/payment terms, selected occurrence, and active assignment for every sellable item. They refresh the strongest observed signed schedule for a series and verify membership and organizer provenance. They validate the chosen fulfillment and inventory pool before requesting merchant acceptance. A created-order snapshot alone is not acceptance or a reservation. For an already accepted unpaid order, inventory revalidation uses its merchant-held commitment instead of demanding the same units again from remaining public stock; payment retries MUST NOT reserve or consume them twice. An unresolved required record, expired/cancelled occurrence, removed assignment, or known material conflict blocks the new event purchase. A product-only market tag never substitutes for an assignment.

Checkout MUST record an explicit `pickup`, `shipping`, or `digital` choice. Pickup requires that assignment's available allocation (or untracked merchant acceptance), physical format, and valid organizer handoff terms. Shipping requires ordinary available stock and an explicitly selected product-authorized non-pickup shipping option. Digital fulfillment requires digital format and ordinary available stock when tracked. If pickup is exhausted while ordinary shipping stock remains, the client may offer shipping for buyer selection; it MUST NOT silently switch method, charge shipping, or borrow another occurrence's allocation. After expiry/removal, an ordinary shop purchase may still proceed under product terms, but it is a separate purchase without current event-assignment authority.

Compatible products for one market, merchant, selected occurrence, fulfillment method, and payment terms may share a purchase. Products for different occurrences or fulfillment methods MUST NOT merge into one order in this profile. Products with incompatible shipping options or other order terms also separate. A booth rename or roster revision alone does not create a second purchase. Material handler, handoff label, occurrence date or venue, assignment state/fulfillment, product identity or commercial terms, price, shipping charge, or payee changes before payment require buyer review; quantity updates alone require revalidation of availability, not an automatic method change.

### Encrypted order extension

This profile uses the existing Open Markets kind-`16`, `type=1` order through NIP-17, with unchanged `p`, `order`, `amount`, and `item` tags. Each `item` references the purchased simple product or variation, never a new event product. The following profile tags are added inside the encrypted order:

```text
["openmarkets", "event-market-order", "1"]
["event_market", "<market-coordinate>", "<market-event-id>"]
["event_occurrence", "<occurrence-coordinate>", "<occurrence-event-id>"]
["event_schedule", "<schedule-coordinate>", "<schedule-event-id>"]  // series only
["event_auth", "<observed-active-3841-tip-id>"]
["fulfillment", "pickup|shipping|digital"]
["event_assignment", "<item-product-coordinate>", "<30410-coordinate>", "<assignment-event-id>"]
// One event_assignment per distinct item coordinate
["evidence", "<event-id>", "<JSON string of complete signed public event>"]
// Repeated for the exact signed evidence needed below
["shipping", "<product-authorized-30406-coordinate>"]  // shipping only, existing tag
```

The profile marker, market, occurrence, authorization tip, fulfillment, and series schedule are singletons. A series order requires exactly one schedule tag; a one-date order has none. Every distinct item coordinate requires exactly one matching assignment tag; extra, duplicate, wrong-merchant, wrong-tuple, or mismatched event-ID references are invalid. Shipping requires the existing `shipping` tag and applicable address/contact terms; event pickup and digital fulfillment do not include a shipping-option tag. Fulfillment text alone cannot grant an unsupported method.

Each `evidence` tag contains the public event envelope including `id`, `pubkey`, `created_at`, `kind`, `tags`, `content`, and `sig`. Its declared ID MUST match the recomputed NIP-01 ID and valid signature. Exactly one payload is included for each referenced evidence ID. Required evidence includes the market revision (and thus merchant row), authorization tip and ancestry needed to validate it, product and any variation parent, each assignment revision, selected occurrence, series schedule if applicable, relevant observed deletion/conflict-resolution evidence, and any selected shipping option and product-referenced collection used to authorize it. Assignment/market parents needed to resolve an observed material divergence are retained too. Evidence tags are inside NIP-17, not a new public order event. Clients MUST NOT discard the signed payloads and depend on relays retaining old addressable revisions.

A created order retains this exact evidence, chosen fulfillment, inventory pool, quantities, payee, and accepted terms. A verifier checks `30409 → 31924 → selected occurrence` membership for a series, or the direct occurrence link for one date, plus `30410 → market + occurrence + product`, same-organizer provenance, merchant authorship, and causal admission. Coordinates or unsourced claims alone cannot substitute for signed payloads. The retained evidence is a historical snapshot of bounded relay observation, not proof that no unobserved event existed or that inventory was atomically reserved. A later roster edit, assignment removal, allocation expiry, schedule edit, date removal, or occurrence replacement does not reinterpret a created or paid order or restore its consumed stock. Current checks still apply to a new payment attempt; changed accepted terms require explicit buyer agreement. A material handoff change for an existing order needs an explicit per-order update or transfer with appropriate merchant and organizer authority and buyer notice. This proposal does not define that private update format.

The order remains directed to the product merchant. Organizer handoff does not authorize the organizer to receive the full buyer order, set product/payment terms, confirm payment, or release merchandise without merchant authorization. Private ready receipt, release, delivery, and recovery protocols are separate from this public record.

## Interoperability example

The excerpts omit the standard event envelope, signatures, and unrelated product tags. `O`, `M1`, and `M2` stand for full lowercase hexadecimal pubkeys. Each `<tuple-hash>` is recomputed from its three full coordinates. The first market uses one date. The alternative series keeps market-wide admission but needs separate merchant assignments for each date. Both use the same ordinary soap product.

```text
31923:O:fair-2027
  ["d", "fair-2027"]
  ["title", "Community Fair"]
  ["start", "<Unix timestamp>"]
  ["end", "<Unix timestamp>"]
  ["D", "<required UTC day bucket>"]
  ["location", "Public Hall"]

31923:O:fair-2027-week-2
  ["d", "fair-2027-week-2"]
  ["title", "Community Fair, week 2"]
  ["start", "<second Unix timestamp>"]
  ["end", "<second Unix timestamp>"]
  ["D", "<required UTC day bucket>"]

31924:O:fair-2027-series, current signed revision <schedule-event-id>
  ["d", "fair-2027-series"]
  ["title", "Community Fair dates"]
  ["a", "31923:O:fair-2027"]
  ["a", "31923:O:fair-2027-week-2"]

10002:O
  ["r", "wss://organizer-events.example/", "write"]

30409:O:fair-2027-market
  ["d", "fair-2027-market"]
  ["a", "31923:O:fair-2027"]
  ["event_market", "2", "open"]
  ["merchant", "M1", "merchant_present", "Booth 12"]
  ["merchant", "M2", "organizer_handoff", "North pickup desk"]

3841 by O, id <M1-grant-id>
  ["openmarkets", "event-market-auth", "1"]
  ["a", "30409:O:fair-2027-market"]
  ["p", "M1"]
  ["state", "active"]
  ["seq", "0"]
  ["alt", "Open Markets event merchant authorization"]

3841 by O, id <M2-grant-id>
  ["openmarkets", "event-market-auth", "1"]
  ["a", "30409:O:fair-2027-market"]
  ["p", "M2"]
  ["state", "active"]
  ["seq", "0"]
  ["alt", "Open Markets event merchant authorization"]

30402:M1:soap
  ["d", "soap"]
  ["title", "Handmade soap"]
  ["price", "12", "USD"]
  ["type", "simple", "physical"]
  ["stock", "20"]
  ["shipping_option", "30406:M1:standard"]

30410:M1:<one-date-tuple-hash>, id <soap-assignment-id>
  ["d", "<one-date-tuple-hash>"]
  ["openmarkets", "event-market-assignment", "1"]
  ["a", "30409:O:fair-2027-market"]
  ["a", "31923:O:fair-2027"]
  ["a", "30402:M1:soap"]
  ["state", "active"]
  ["inventory", "tracked", "6"]
  ["fulfillment", "pickup"]
  ["fulfillment", "shipping"]
  ["alt", "Open Markets occurrence product assignment"]

// standard is an ordinary merchant-authorized 30406 shipping option;
// its complete signed fields and geographic/package constraints must validate.

// Alternative series market uses exactly one schedule link:
30409:O:fair-2027-series-market
  ["d", "fair-2027-series-market"]
  ["a", "31924:O:fair-2027-series"]
  ["event_market", "2", "open"]
  ["merchant", "M1", "merchant_present", "Booth 12"]

3841 by O, id <M1-series-grant-id>
  ["openmarkets", "event-market-auth", "1"]
  ["a", "30409:O:fair-2027-series-market"]
  ["p", "M1"]
  ["state", "active"]
  ["seq", "0"]
  ["alt", "Open Markets event merchant authorization"]

30410:M1:<series-week-1-tuple-hash>, id <week-1-assignment-id>
  ["d", "<series-week-1-tuple-hash>"]
  ["openmarkets", "event-market-assignment", "1"]
  ["a", "30409:O:fair-2027-series-market"]
  ["a", "31923:O:fair-2027"]
  ["a", "30402:M1:soap"]
  ["state", "active"]
  ["inventory", "tracked", "6"]
  ["fulfillment", "pickup"]
  ["fulfillment", "shipping"]
  ["alt", "Open Markets occurrence product assignment"]

30410:M1:<series-week-2-tuple-hash>, id <week-2-assignment-id>
  ["d", "<series-week-2-tuple-hash>"]
  ["openmarkets", "event-market-assignment", "1"]
  ["a", "30409:O:fair-2027-series-market"]
  ["a", "31923:O:fair-2027-week-2"]
  ["a", "30402:M1:soap"]
  ["state", "active"]
  ["inventory", "tracked", "4"]
  ["fulfillment", "pickup"]
  ["fulfillment", "shipping"]
  ["alt", "Open Markets occurrence product assignment"]

// Merchant removes week 2 early: same tuple and d, newer signed revision.
30410:M1:<series-week-2-tuple-hash>, id <removed-week-2-id>
  ["d", "<series-week-2-tuple-hash>"]
  ["openmarkets", "event-market-assignment", "1"]
  ["a", "30409:O:fair-2027-series-market"]
  ["a", "31923:O:fair-2027-week-2"]
  ["a", "30402:M1:soap"]
  ["state", "removed"]
  ["inventory", "tracked", "0"]
  ["prev", "<week-2-assignment-id>"]
  ["alt", "Open Markets occurrence product assignment"]

// Organizer cancellation: a replacement of the complete week-2 occurrence
// retains its d/title/start/end/D and adds this profile tag:
  ["event_occurrence", "1", "cancelled"]
```

`M1` may assign a second existing product without an organizer product update. `M2` remains the payee despite organizer handoff. If `O` removes `M1`'s row or signs a descendant revoke, `M1` leaves the event catalog while its shop remains unchanged. Reapproval requires a descendant active grant and a current row; only still-valid active assignments at eligible occurrences return. Merchant removal of week 2 releases its unused allocation and remains effective despite a stale active revision. Removing week 2 from the schedule alone disables its new series purchases but does not establish stock release.

In the series example, the schedule admits only its two listed organizer-authored occurrences. A third occurrence becomes selectable only after a newer signed schedule adds it and the merchant publishes a new assignment. A child-authored calendar request alone cannot add it. A week-2 pickup order pins `<schedule-event-id>`, the exact week-2 occurrence ID, `<week-2-assignment-id>` and its coordinate, market and grant evidence, product revision, fulfillment, quantities, payee, and accepted terms. Subsequent removal/cancellation preserves that historical order.

### Worked inventory cases

Each row is an independent scenario; `S` and `q` exclude accepted order commitments.

| Case | Signed remaining inventory | Result |
| --- | --- | --- |
| One in-person event | Soap `S=20`, occurrence A `q=6` | Pickup A offers 6; ordinary shipping offers 14. Accepting 2 pickups yields `S=18, q=4`, still 14 ordinary units. |
| Two future occurrences | Soap `S=20`, A `q=6`, B `q=4` | 10 ordinary units; A cannot borrow B's 4. Accepting 3 shipping units yields `S=17`, allocations unchanged, ordinary stock 7. |
| Recurring rollover | A ends with `S=18, q=4`; merchant assigns 4 to new B | A counts 0 after end; a different tuple/d reserves 4 at B. No product or shipping edit is needed merely to roll unused allocation. |
| Variation stock | Existing red variation `S=8, q=3`; blue `S=5, q=2` | Independent assignment coordinates and ordinary stock 5 red / 3 blue; no parent-level double subtraction. |
| Untracked stock | Product has no `stock`; assignment `["inventory","untracked"]` | No fake quantity; enabled pickup or ordinary fulfillment requires merchant acceptance. |
| Ended/cancelled/removed | Soap `S=20`, A unused `q=6` becomes ineffective | A reserves 0; ordinary stock is 20 if no other allocation remains. Existing commitments stay excluded from `S`. |
| Pickup exhausted | Soap `S=14`, active A `q=0`, pickup and shipping enabled | No tracked pickup; buyer may explicitly choose valid ordinary shipping for up to 14. |
| Remote/digital event | Digital product `S=9`, active A `q=0`, digital enabled | Digital uses ordinary stock; the assignment creates no pickup, shipping mutation, or separate event product. |

## Compatibility and migration

This profile is an experimental new contract. Earlier experimental version-1 `30409` records remain historical evidence and MUST NOT synthesize an active grant or current version-2 admission. An organizer updating an existing coordinate to version 2 cites the signed revision it edited from with `prev`. A product with only a stable market `a` tag is discovery-only: even a valid version-2 market and active merchant grant require a merchant-signed `30410` for the chosen occurrence. Existing standard products and their shipping need no republication to create these assignments. Existing kind `30405` collection catalogs, their exact product references, and kind `30406` event pickup options are not reinterpreted as kind `30409` records or `30410` allocations. Existing events and created orders may continue under their original signed terms. New clients may maintain named legacy readers for those records, but they MUST NOT treat an old collection as a current merchant whitelist or infer assignments from previous products.

The earlier collection-based proposal used a `conduit_event_market` lifecycle declaration and contemplated migration to a neutral `event_market` collection tag. That lifecycle alias is legacy collection evidence only. New kind `30409` records use the versioned `event_market` tag directly. A client MUST NOT dual-write a `30405` collection as if it were the same authority as a `30409` roster, or use historical product search and mass product republication to establish participation.

A client that does not implement this experimental profile may ignore kinds `30409` and `30410`; it may still show ordinary merchant products. Such a reader may not subtract allocations and therefore cannot establish event-aware ordinary availability; the merchant still enforces all commitments at acceptance. Clients that cannot validate the assignment or order extension MUST NOT silently offer event checkout under the older product-tag model. A failed version-2 authorization or assignment read MUST NOT fall back to older roster/product-tag authority. The `30409` version remains `2` because its organizer wire schema and causal authorization are unchanged; this revised experimental profile requires assignment/order version `1` for new occurrence commerce. Earlier created orders retain their original accepted terms. Upstream review, independent implementations, and cross-client fixtures are needed before treating this profile as normative Open Markets text.

## Conformance cases

Implementations should cover at least:

1. empty date-based and timed Event Markets, valid and invalid organizer provenance, open/closed/reopen;
2. merchant-level request or invitation, approval with one mode and assignment, later edit, and duplicate/conflicting row rejection;
3. unapproved assignment spam, approved merchant assignment publishing, ordinary product edit/replacement, hide, and author-scoped product or assignment deletion;
4. roster removal and reapproval, including only still-valid active occurrence assignments returning and organizer preview of that consequence;
5. finite author plus kind-`30410` `#a` discovery with stale, divergent, partial, unavailable, and deletion evidence; multi-value `#a` is not an intersection;
6. a direct product link applying the same current admission, occurrence, assignment, product-revision, and explicit fulfillment checks as the catalog;
7. stale organizer edit rejection and known divergent parent references;
8. compatible same-occurrence, same-fulfillment products forming one purchase despite a booth rename or roster revision, while different dates, methods, or incompatible shipping/payment terms separate;
9. buyer review after material changes to an unpaid cart, and created or paid order continuity after later roster changes;
10. organizer handoff without organizer payment or full-order authority, with no separate buyer event fee;
11. ordinary `30405` collections and historical `30406` event pickups as negative controls for the new profile;
12. active grant plus current row, row-only and grant-only denial, revoke, descendant regrant, stale sibling, identical-state fork, and multi-parent reconciliation;
13. roster removal accompanied by causal revoke, including interrupted publication, followed by deliberate descendant reapproval;
14. observed deletion of a revoke tip, missing target payload, and a later stale relay response: retained negative evidence must not restore an older grant; unseen deletions remain unknowable;
15. NIP-65 write-relay discovery, hints and fallbacks, unioned observations, retained stronger evidence, and relay unavailability without fabricated absence;
16. version-1 `30409`, unknown organizer, wrong market scope, and missing grant as negative controls;
17. one-date and `31924` series markets each with exactly one market `a` link; wrong schedule or member author, duplicate or malformed member coordinates, and child-only calendar requests as negative controls;
18. bounded series reads with a missing sibling, missing master, missing selected occurrence, stale or divergent master, observed deletion, and a current revision that removes a future date; only adequate positive signed evidence for the selected member permits its new purchase;
19. exclusive-end expiry for both one-date and series occurrences, timed missing-end denial, date-based omitted-end and UTC boundary, cancellation and occurrence deletion; other dates remain usable and an open market cannot restore expired/cancelled allocations;
20. one standard product and market-wide grant with distinct deterministic assignments for two series dates; a new schedule member without its own assignment is insufficient;
21. exact market, schedule, occurrence, authorization, product, variation parent, assignment, shipping, payee, and accepted-term order evidence; forged, wrong-tuple, duplicate, or coordinate-only claims fail verification, while old orders remain intact after later edits/removal;
22. tuple hashing with colon-containing and Unicode d values, wrong hash, wrong product author, variable-parent allocation denial, existing variation references, and independent per-variation stock;
23. tracked, zero, and untracked inventory shapes, mode mismatches, duplicate/unknown fulfillment methods, malformed/unsupported assignment profiles, and bare product tags as negative controls;
24. single and simultaneous occurrence calculations, over-allocation denial, hidden products or revoked merchants retaining reservations until explicit release, and incomplete cross-market reads not proving ordinary stock;
25. pickup exhaustion with an explicit shipping choice, valid product-owned shipping/collection merge and constraints, shipping-only zero allocation, and digital fulfillment without physical methods;
26. exactly-once total plus pickup consumption, shipping consumption without pickup decrement, replayed order IDs, concurrent acceptance, and partial two-record publication requiring reconciliation;
27. natural expiry, terminal cancellation, and explicit removed revisions releasing only unused allocation; stale relay responses cannot restore it and outstanding commitments are not returned to stock;
28. recurring rollover with a new tuple/d, transfer before expiry removing/reducing the old allocation first, and no series-wide stock or movement of existing order commitments; and
29. byte-preserved standard product shipping through assignment creation/removal/rollover, legacy event-order continuity, and refusal to infer new assignment authority from older product-tag participation.
