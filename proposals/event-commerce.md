# NIP-52-backed Event Markets

Status: experimental proposal. This page is not current normative Open Markets text.

This proposal adds a dedicated, organizer-signed Event Market record and per-merchant causal authorization. A market may link one concrete NIP-52 occurrence or one organizer-authored finite kind `31924` calendar whose current signed revision lists concrete occurrences. Client-side weekly generation publishes ordinary NIP-52 events and a finite calendar list; this profile defines no RRULE or recurring scheduler. The organizer controls merchant admission, commerce state, and public handoff assignments. Approved merchants control their own products, inventory, prices, and payment destinations. A merchant's event-tagged products need no individual organizer approval. Signed parent relationships make observed stale or concurrent approval edits detectable; relay observation never proves that no unseen event exists.

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

Kinds `30409` and `3841` are proposed for this experimental profile. At the checked public registry revision they are unassigned; they are not registered kinds. `30409` is addressable, and `3841` is a regular immutable event. Current Open Markets text uses `30405` for collections and `30406` for shipping options. Those existing kinds retain their current meaning.

## Scope and coordinates

```text
occurrence = 31922:<organizer-pubkey>:<occurrence-d>
           | 31923:<organizer-pubkey>:<occurrence-d>
schedule   = 31924:<organizer-pubkey>:<schedule-d>  // series only
market     = 30409:<organizer-pubkey>:<market-d>
auth       = (market coordinate, merchant pubkey)
product    = 30402:<merchant-pubkey>:<product-d>
```

The full kind, author, and `d` value identify each addressable record. A `d` value alone is insufficient. The linked `31922` or `31923` gives one advertised occurrence and venue. Alternatively, the linked `31924` is a finite schedule container; its current signed revision lists concrete `31922` and `31923` occurrences. The `30409` remains the sole commerce authority in either case. The organizer MUST author the market, its linked schedule, and every commerce-relevant member occurrence. Only exact full coordinates in the current signed `31924` revision establish series membership. A child event's `a` tag requesting calendar inclusion does not establish membership, nor does an RSVP. A current market roster row and a valid active per-merchant grant are both required for admission. NIP-52 participant tags do not grant merchant admission.

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

Each merchant pubkey is 64 lowercase hexadecimal characters. The assignment is a public booth or pickup label of at most 120 UTF-8 bytes, with no control characters. The serialized signed event MUST fit within 64 KiB. The `merchant` row is a multi-letter tag; clients fetch the known market coordinate and read its finite roster rather than assuming relays index that tag. A duplicate merchant row, unknown mode, malformed row, over-limit record, wrong occurrence or schedule author, multiple calendar links, or duplicate lifecycle tag is unusable admission evidence. Clients MUST NOT choose one of two conflicting rows.

`merchant_present` means the merchant handles physical handoff at the public assignment. It does not itself prove that a buyer or merchant is currently present. `organizer_handoff` means the organizer performs physical handoff at the public assignment under a separate order-specific release authorization. Neither mode transfers product, inventory, price, payment, or full-order authority from the merchant. The organizer may change the mode or assignment in a later signed roster revision.

Approval requires both a current roster row and an active causal grant for the same market and merchant. There is no separate approval boolean or list of product coordinates. A market with zero merchants is valid before enrollment. Removing a row or signing a descendant revoke removes that merchant's products from the event catalog without modifying the shop. Reapproval requires a new descendant grant and a current row; it makes every still-valid, still-tagged product eligible again. Organizer clients SHOULD disclose that effect before reapproval. A grant without a row has no event mode or assignment and cannot authorize event participation; a row without a grant cannot authorize it either.

## Merchant enrollment and product participation

A request or invitation concerns a merchant pubkey and one market coordinate, not particular products. The request transport is outside this public profile; a client using one MUST authenticate the requesting merchant or inviting organizer. A request or invitation does not grant admission. Only a valid current organizer-signed roster row together with an active causal grant does.

An eligible merchant MAY put `["a", "30409:<organizer>:<market-d>"]` on a kind `30402` product. For a series, the product keeps this one market association as dates are added, edited, or removed; it does not tag each occurrence. This tag expresses event participation and enables `#a` candidate discovery. It is an Event Market association, not a kind `30405` collection reference, and does not grant admission by itself. The product MUST remain merchant-authored and retain its ordinary Open Markets listing semantics. Its price, stock, visibility, payment destination, and ordinary shop shipping options remain merchant-controlled. The product MUST NOT supply an independent event booth, pickup, handler, or event fee through this profile. Ordinary `shipping_option` tags, if present for non-event sales, do not override the Event Market row for event handoff.

Once admitted, the merchant may publish, edit, replace, untag, hide, or delete products without a separate organizer product decision. A newer valid product revision that removes the market `a` tag supersedes an older tagged revision. A valid author-scoped NIP-09 deletion may remove the product. Other users may tag the market, but only current roster authors with active grants are eligible.

## Causal merchant authorization

The organizer's current `30409` row supplies the merchant's event mode and
public assignment. A separate organizer-authored causal history protects
merchant-level grants and revocations from **observed** stale or concurrent
writes. Both a current row and an active grant are required for new commerce.
Neither a product tag nor a relay response grants authority by itself.

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
also use organizer/market/merchant scope tags when present. Product deletion
evidence is sought from the merchant's publishing relays by known product
revision IDs and product coordinate. They union valid signed observations from the selected relays and
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
tip, and current valid merchant product. It MUST block a known unresolved
authorization conflict or deletion and MUST fail closed when it cannot
obtain adequate positive current evidence for the transaction. The client
chooses its relay coverage and freshness policy; any admission claim is
relative to the signed evidence it actually observed and retained.

## Commerce lifecycle

The NIP-52 `start` and `end` describe the advertised calendar schedule, not permission for new commerce. The versioned `event_market` state is authoritative for this profile:

- `open`: new event purchases may proceed only if the current organizer roster, active merchant grant, product, and payment terms are valid.
- `closed`: no new event purchases or new payment attempts may start. The organizer may reopen by signing a later valid revision.

For a series, calendar time does not close the whole market. A new series pickup purchase MUST explicitly select an occurrence that is current or future under its signed NIP-52 `start` and `end` values and belongs to the current signed schedule revision. A past occurrence cannot be selected for a new series pickup order, even while the market remains open. The existing one-date open-market behavior is unchanged; its calendar `start` or `end` does not independently close commerce. Closing or changing a market does not delete its history, cancel an existing order, invalidate a prior payment, or prevent independently authorized settlement inspection and fulfillment. A valid market lacking the required versioned state cannot authorize new commerce. An unsupported, malformed, deleted, or legacy version-1 current revision is not a fallback to an older version-2 revision or calendar time. Version-1 `30409` records never synthesize causal grants.

There is no separate buyer event-pickup fee. A merchant accounts for event costs in their product prices and remains the payee even when the organizer performs physical pickup.

## Resolution and discovery

Clients start from a known market coordinate, resolve its signed current version-2 revision and linked NIP-52 occurrence or schedule, then derive the finite roster author set. For a series, clients resolve the strongest observed current signed `31924` revision under NIP-01 ordering, then fetch its member coordinates in bounded batches. They validate each member's signature, exact coordinate, organizer author, NIP-52 fields, and applicable author-scoped NIP-09 evidence. Duplicate, malformed, or cross-author member references cannot authorize a selected occurrence. A member's request to join the schedule without a current schedule reference is insufficient. They MAY query kind `30402` by those authors and `#a` market coordinate as a bounded candidate plan. Neither a filter hit nor an incomplete filter result proves admission or absence. Authorization reads are scoped per merchant to the stable market coordinate.

Before showing a candidate as an event product, including at a direct product link, a client MUST resolve its current signed addressable revision and applicable NIP-09 deletion evidence, then validate its author, exact market `a` tag, product fields, and visibility against the current roster and active causal authorization. A product without both a current row and a valid active grant MUST NOT enter the official catalog. A newer revision that un-tags or hides a product wins over an older tagged revision. A newer signed roster removal wins over an older roster returned by a lagging relay.

NIP-01 orders addressable revisions by `created_at`, then lowest event ID at the same timestamp. NIP-09 deletion is author-scoped; a third party cannot remove a merchant listing or organizer market. Readers MUST retain stronger valid signed revision or deletion evidence they already hold instead of treating a partial or empty relay response as reversal. A partial sibling read does not prove another occurrence absent and need not invalidate an otherwise verified selected member. A missing, stale, divergent, or unresolved current schedule, or missing selected member payload, cannot authorize a new series pickup. An observed newer schedule that removes a date defeats an older schedule returned by a lagging relay; an empty response alone does not prove removal. A signed kind-`5` request is evaluated against its author's exact known target, and an unresolved observed deletion targeting the schedule or selected occurrence blocks new commerce on that evidence. Clients SHOULD expose partial, unavailable, stale, conflicting, malformed, and deleted observations where those distinctions affect a purchase. Relay `OK` means relay acceptance, not recipient observation or network-wide convergence.

Before signing a roster update, a writer MUST read and compare the strongest observed current market revision, preserve unaffected rows, and reject an edit based on an older known revision. The required `prev` reference on market updates exposes the parent used and helps detect divergent edits when both branches are observed. Multiple observed roots for one market coordinate are divergent too. NIP-01 does not provide a global compare-and-swap; a client cannot prove that no unseen concurrent revision exists. Known divergent market ancestry MUST be surfaced for organizer review. An unresolved material state or assignment conflict blocks new commerce until the organizer signs a reviewed revision based on the strongest observed winner. A stale market revision cannot restore a merchant whose known grant is revoked. New purchases require positive current market, product, and authorization evidence; incomplete reads do not prove admission or removal by themselves. The same check applies to direct product links.

A schedule writer MUST compare the strongest observed current `31924` revision before replacing it, preserve unaffected member references, and surface an observed newer or conflicting revision instead of silently overwriting it. To extend a series, publish new signed occurrences before the schedule revision that references them. Removing a future date changes schedule membership; it does not require deleting its standalone NIP-52 event. Organizers SHOULD retain past members for timeline history. NIP-52 does not define a schedule `prev` tag or a global compare-and-swap; the writer cannot prove that no unseen concurrent revision exists.

## Checkout and historical orders

For an unpaid cart, clients resolve the current open market, the merchant's current row and observed causal grant, and current product/payment terms. For a series they also refresh the strongest observed schedule revision and selected occurrence before payment, verify current membership and organizer provenance, and require buyer review if the date or other material signed terms changed. An unresolved schedule or selected occurrence blocks the new purchase. Participation identity is market coordinate plus merchant pubkey; a series purchase additionally includes the selected occurrence coordinate. Compatible products for one market, merchant, selected occurrence, and payment terms may share a purchase. Products selected for different dates MUST NOT merge into one purchase. A booth rename or roster event ID change alone does not create a second purchase. Material mode, assignment, calendar date, price, product, or payee changes before payment require buyer review.

A created order retains the exact signed market revision, merchant row, observed authorization tip and required ancestry, relevant observed deletion evidence, product revision, assignment, payee, and accepted terms under which it was created. A one-date order retains its exact occurrence revision. A series order additionally retains the exact signed `31924` revision and selected `31922` or `31923` revision, including full coordinates and event IDs, so a verifier can authenticate `30409 → 31924 → selected occurrence` membership and same-organizer provenance against the observed authorization and product evidence. Coordinates or unsourced claims alone cannot substitute for those signed payloads. The retained evidence is a historical snapshot of the merchant's bounded relay observation, not independent proof that no unobserved event existed. A later roster edit, schedule edit, date removal, or occurrence replacement does not reinterpret a created or paid order. A material handoff change for an existing order needs an explicit per-order update or transfer with the appropriate merchant and organizer authority and buyer notice. This proposal does not define that private message format.

The order remains directed to the product merchant. Organizer handoff does not authorize the organizer to receive the full buyer order, set product/payment terms, confirm payment, or release merchandise without merchant authorization. Private ready receipt, release, delivery, and recovery protocols are separate from this public record.

## Interoperability example

The excerpts omit the standard event envelope, signatures, and unrelated product tags. `O`, `M1`, and `M2` stand for full lowercase hexadecimal pubkeys. The first market uses one date. The second uses a finite organizer-authored series. Its separate grant and product association remain market-wide across all listed dates.

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
  ["a", "30409:O:fair-2027-market"]

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

30402:M1:soap-series
  ["d", "soap-series"]
  ["title", "Handmade soap"]
  ["price", "12", "USD"]
  ["type", "simple", "physical"]
  ["a", "30409:O:fair-2027-series-market"]
```

`M1` may publish a second tagged product without an organizer product update. `M2` remains the payee for its products despite organizer handoff. If `O` removes `M1`'s row or signs a descendant revoke, `M1` leaves the event catalog while its shop remains unchanged. Reapproval requires a descendant active grant and a current row; then all still-valid, still-tagged `M1` products are eligible again. A replacement `soap-series` revision without the market tag supersedes the older tagged revision. In the series example, the schedule's signed `a` tags admit only its two listed organizer-authored occurrences. An organizer-authored third occurrence becomes selectable only after a newer signed schedule adds it. A child-authored calendar request alone cannot add it. A series order for week 2 retains `<schedule-event-id>`, the exact week-2 event ID, the market and grant evidence, product revision, assignment, payee, and accepted terms; removing week 2 later prevents its selection for new purchases while preserving that order.

## Compatibility and migration

This profile is an experimental new contract. Earlier experimental version-1 `30409` records remain historical evidence and MUST NOT synthesize an active grant or current version-2 admission. An organizer updating an existing coordinate to version 2 cites the signed revision it edited from with `prev`. A product published against a version-1 market with only the stable market `a` tag is discovery-only under this profile until a valid version-2 market and active merchant grant exist; the merchant does not need to republish it solely for the new authorization model. Existing kind `30405` collection catalogs, their exact product references, and kind `30406` event pickup options are not reinterpreted as kind `30409` records. Existing events and created orders may continue under their original signed terms. New clients may maintain named legacy readers for those records, but they MUST NOT treat an old collection as a current merchant whitelist or infer a new roster from previous products.

The earlier collection-based proposal used a `conduit_event_market` lifecycle declaration and contemplated migration to a neutral `event_market` collection tag. That lifecycle alias is legacy collection evidence only. New kind `30409` records use the versioned `event_market` tag directly. A client MUST NOT dual-write a `30405` collection as if it were the same authority as a `30409` roster, or use historical product search and mass product republication to establish participation.

A client that does not implement this experimental profile may ignore kind `30409`; it may still show ordinary merchant products. A failed version-2 authorization read MUST NOT fall back to version-1 roster authority. Upstream review, independent implementations, and cross-client fixtures are needed before treating this profile as normative Open Markets text.

## Conformance cases

Implementations should cover at least:

1. empty date-based and timed Event Markets, valid and invalid organizer provenance, open/closed/reopen;
2. merchant-level request or invitation, approval with one mode and assignment, later edit, and duplicate/conflicting row rejection;
3. unapproved product spam, approved automatic publishing, product edit/replacement, untag, hide, and author-scoped deletion;
4. roster removal and reapproval, including all still-valid tagged products returning and organizer preview of that consequence;
5. finite author plus `#a` discovery with stale, divergent, partial, unavailable, and deletion evidence;
6. a direct product link applying the same current admission and product-revision checks as the catalog;
7. stale organizer edit rejection and known divergent parent references;
8. two compatible products forming one purchase despite a booth rename or roster revision, while genuinely different payment/order terms separate;
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
19. selection of current or future series occurrences, denial of past occurrences, market-wide open/closed state independent of calendar time, and unchanged one-date open-market behavior;
20. one tagged merchant product and one valid grant serving multiple series dates, with distinct dates kept separate in cart and orders and compatible same-date products grouped; and
21. exact market, schedule, selected occurrence, authorization, product, assignment, payee, and accepted-term order evidence; forged or coordinate-only claims fail verification, while old orders remain valid after schedule edits or date removal.
