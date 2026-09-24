# NIP-52-backed Event Markets

Status: experimental proposal. This page is not current normative Open Markets text.

This proposal adds a dedicated, organizer-signed addressable Event Market record. The organizer controls event-specific merchant admission and public handoff assignments. Approved merchants control their own product listings, inventory, prices, and payment destinations. A merchant's event-tagged products need no individual organizer approval.

## Public sources and kind allocation

- [NIP-01 addressable events, tags, filters, and replacement](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [NIP-09 author-scoped deletion](https://github.com/nostr-protocol/nips/blob/master/09.md)
- [NIP-19 shareable addresses](https://github.com/nostr-protocol/nips/blob/master/19.md)
- [NIP-52 calendar events](https://github.com/nostr-protocol/nips/blob/master/52.md)
- [NIP-99 classified listings](https://github.com/nostr-protocol/nips/blob/master/99.md)
- [Nostr kind registry](https://github.com/nostr-protocol/registry-of-kinds/blob/master/schema.yaml)
- [Current Open Markets compatibility snapshot](../SPEC.md)

Kind `30409` is proposed for Event Markets. It is in NIP-01's addressable range. At the time of this proposal, the public kind registry lists `30402` and `30403` in the nearby range but does not assign `30409`; current Open Markets text uses `30405` for collections and `30406` for shipping options. This allocation is experimental and requires public review. Existing kind `30405` collections retain their current meaning.

## Scope and coordinates

```text
calendar = 31922:<organizer-pubkey>:<calendar-d>
         | 31923:<organizer-pubkey>:<calendar-d>
market   = 30409:<organizer-pubkey>:<market-d>
product  = 30402:<merchant-pubkey>:<product-d>
```

The full kind, author, and `d` value identify each addressable record. A `d` value alone is insufficient. The calendar gives the advertised schedule and venue; the market gives commerce state, merchant admission, and public handoff assignment. NIP-52 participant tags, calendar membership, and RSVPs do not grant merchant admission. A kind `31924` calendar may group calendar events but is not the Event Market.

This proposal does not define ticketing, check-in, global event discovery, payment custody, a new order envelope, or private handoff messages. It does not redefine ordinary kind `30405` collections or kind `30406` shipping options.

## Event Market record: kind `30409`

The market MUST be signed by the same pubkey that authored its linked NIP-52 calendar event. Its current signed revision contains:

- exactly one nonempty `d` tag, at most 128 UTF-8 bytes;
- exactly one `a` tag referencing an organizer-authored kind `31922` or `31923` calendar coordinate;
- exactly one `event_market` tag with version `1` and state `open` or `closed`;
- zero to 128 `merchant` rows, each with a unique merchant pubkey, one mode, and a nonempty public assignment;
- optional `prev` tag referencing the immediately preceding signed market revision's event ID on updates; and
- optional display tags such as `title`, `summary`, and `image`, without making them authority for schedule, admission, price, or payment.

```text
["d", "<market-id>"]
["a", "31922:<organizer>:<calendar-id>"]
["event_market", "1", "open|closed"]
["merchant", "<merchant-pubkey>", "merchant_present|organizer_handoff", "<public-assignment>"]
["prev", "<prior-market-event-id>"]  // updates only
```

Each merchant pubkey is 64 lowercase hexadecimal characters. The assignment is a public booth or pickup label of at most 120 UTF-8 bytes, with no control characters. The serialized signed event MUST fit within 64 KiB. The `merchant` row is a multi-letter tag; clients fetch the known market coordinate and read its finite roster rather than assuming relays index that tag. A duplicate merchant row, unknown mode, malformed row, over-limit record, wrong calendar author, multiple calendar links, or duplicate lifecycle tag is unusable admission evidence. Clients MUST NOT choose one of two conflicting rows.

`merchant_present` means the merchant handles physical handoff at the public assignment. It does not itself prove that a buyer or merchant is currently present. `organizer_handoff` means the organizer performs physical handoff at the public assignment under a separate order-specific release authorization. Neither mode transfers product, inventory, price, payment, or full-order authority from the merchant. The organizer may change the mode or assignment in a later signed roster revision.

Roster membership is approval. There is no separate approval boolean or list of product coordinates. A market with zero merchants is valid and useful before enrollment. Replacing the roster to remove a merchant removes their products from the event catalog; their shop listings remain theirs. Reapproving a merchant makes every still-valid, still-event-tagged product eligible again. Organizer clients SHOULD disclose this effect before reapproval.

## Merchant enrollment and product participation

A request or invitation concerns a merchant pubkey and one market coordinate, not particular products. The request transport is outside this public profile; a client using one MUST authenticate the requesting merchant or inviting organizer. A request or invitation does not grant admission. Only a valid current organizer-signed roster row does.

An eligible merchant MAY put ` ["a", "30409:<organizer>:<market-d>"] ` on a kind `30402` product. This tag expresses event participation and enables `#a` candidate discovery. It does not grant admission by itself. The product MUST remain merchant-authored and retain its ordinary Open Markets listing semantics. Its price, stock, visibility, payment destination, and ordinary shop shipping options remain merchant-controlled. The product MUST NOT supply an independent event booth, pickup, handler, or event fee through this profile. Ordinary `shipping_option` tags, if present for non-event sales, do not override the Event Market row for event handoff.

Once admitted, the merchant may publish, edit, replace, untag, hide, or delete products without a separate organizer product decision. A newer valid product revision that removes the market `a` tag supersedes an older tagged revision. A valid author-scoped NIP-09 deletion may remove the product. Other users may tag the market, but only current roster authors are eligible.

## Commerce lifecycle

The NIP-52 `start` and `end` describe the advertised calendar schedule, not permission for new commerce. The versioned `event_market` state is authoritative for this profile:

- `open`: new event purchases may proceed only if the current organizer roster, merchant product, and payment terms are valid.
- `closed`: no new event purchases or new payment attempts may start. The organizer may reopen by signing a later valid revision.

Closing or changing a market does not delete its history, cancel an existing order, invalidate a prior payment, or prevent independently authorized settlement inspection and fulfillment. A valid market lacking the required versioned state cannot authorize new commerce. An unsupported version or malformed state is not a fallback to calendar time.

There is no separate buyer event-pickup fee. A merchant accounts for event costs in their product prices and remains the payee even when the organizer performs physical pickup.

## Resolution and discovery

Clients start from a known market coordinate, resolve its signed current revision and NIP-52 calendar, then derive the finite approved author set. They MAY query kind `30402` by approved authors and `#a` market coordinate as a bounded candidate plan. Neither a filter hit nor an incomplete filter result proves membership or absence.

Before showing a candidate as an event product, including at a direct product link, a client MUST resolve its current signed addressable revision and applicable NIP-09 deletion evidence, then validate its author, exact market `a` tag, product fields, and visibility against the current roster. An unapproved author's product MUST NOT enter the official catalog. A newer revision that un-tags or hides a product wins over an older tagged revision. A newer signed roster removal wins over an older roster returned by a lagging relay.

NIP-01 orders addressable revisions by `created_at`, then lowest event ID at the same timestamp. NIP-09 deletion is author-scoped; a third party cannot remove a merchant listing or organizer market. Readers MUST retain stronger valid signed revision or deletion evidence they already hold instead of treating a partial or empty relay response as reversal. Clients SHOULD expose partial, unavailable, stale, conflicting, malformed, and deleted observations where those distinctions affect a purchase. Relay `OK` means relay acceptance, not recipient observation or network-wide convergence.

Before signing a roster update, a writer MUST read and compare the strongest observed current market revision, preserve unaffected rows, and reject an edit based on an older known revision. A `prev` reference exposes the parent used for an update and helps detect divergent edits when both branches are observed. NIP-01 does not provide a global compare-and-swap; a client cannot prove that no unseen concurrent revision exists. Known divergent ancestry MUST be surfaced for organizer review rather than silently used to restore a removed merchant. New purchases require adequate positive current evidence; incomplete reads do not prove admission or removal by themselves.

## Checkout and historical orders

For an unpaid cart, clients resolve the current market row and current product/payment terms. The participation identity is market coordinate plus merchant pubkey. Compatible products from that merchant at that event may share one purchase unless payment or order terms require separation. A booth rename or roster event ID change alone does not create a second purchase. Material mode, assignment, calendar date, price, product, or payee changes before payment require buyer review.

A created order retains the exact signed market revision, merchant row, calendar and product revisions, payee, and terms under which it was created. A later roster change does not reinterpret a created or paid order. A material handoff change for an existing order needs an explicit per-order update or transfer with the appropriate merchant and organizer authority and buyer notice. This proposal does not define that private message format.

The order remains directed to the product merchant. Organizer handoff does not authorize the organizer to receive the full buyer order, set product/payment terms, confirm payment, or release merchandise without merchant authorization. Private ready receipt, release, delivery, and recovery protocols are separate from this public record.

## Interoperability example

The excerpts omit the standard event envelope, signatures, and unrelated product tags. `O`, `M1`, and `M2` stand for full lowercase hexadecimal pubkeys.

```text
31923:O:fair-2027
  ["d", "fair-2027"]
  ["title", "Community Fair"]
  ["start", "<Unix timestamp>"]
  ["end", "<Unix timestamp>"]
  ["D", "<required UTC day bucket>"]
  ["location", "Public Hall"]

30409:O:fair-2027-market
  ["d", "fair-2027-market"]
  ["a", "31923:O:fair-2027"]
  ["event_market", "1", "open"]
  ["merchant", "M1", "merchant_present", "Booth 12"]
  ["merchant", "M2", "organizer_handoff", "North pickup desk"]

30402:M1:soap
  ["d", "soap"]
  ["title", "Handmade soap"]
  ["price", "12", "USD"]
  ["type", "simple", "physical"]
  ["a", "30409:O:fair-2027-market"]
```

`M1` may publish a second tagged product without an organizer update. `M2` remains the payee for its products despite organizer handoff. If `O` signs a newer market revision without `M1`'s row, all `M1` products leave the event catalog while remaining in `M1`'s shop. If `O` later restores `M1`, every current valid `M1` product still tagged for this market becomes eligible again. If `M1` replaces `soap` without the market tag, the older tagged version cannot keep it in the event catalog.

## Compatibility and migration

This profile is an experimental new contract. Existing kind `30405` collection catalogs, their exact product references, and kind `30406` event pickup options are not reinterpreted as kind `30409` records. Existing events and created orders may continue under their original signed terms. New clients may maintain named legacy readers for those records, but they MUST NOT treat an old collection as a current merchant whitelist or infer a new roster from previous products.

The earlier collection-based proposal used a `conduit_event_market` lifecycle declaration and contemplated migration to a neutral `event_market` collection tag. That lifecycle alias is legacy collection evidence only. New kind `30409` records use the versioned `event_market` tag directly. A client MUST NOT dual-write a `30405` collection as if it were the same authority as a `30409` roster, or use historical product search and mass product republication to establish participation.

A client that does not implement this experimental profile may ignore kind `30409`; it may still show ordinary merchant products. Upstream review, independent implementations, and cross-client fixtures are needed before treating this profile as normative Open Markets text.

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
10. organizer handoff without organizer payment or full-order authority, with no separate buyer event fee; and
11. ordinary `30405` collections and historical `30406` event pickups as negative controls for the new profile.
