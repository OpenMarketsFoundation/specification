# Bookings: Time-Based Purchases

Status: experimental proposal. This page is not current normative Open Markets text.

## Problem

A customer who wants to book time with a business (a table at 7 pm, a room for three nights, an hour-long service, a seat at a scheduled event) has no Open Markets message for it. Orders buy goods against a listing; a booking buys the use of a resource for a period, the booking itself is often free, and may have no listing at all. This proposal defines that message flow. Booking messages are private `kind:1331` rumors, sealed and gift wrapped per [NIP-59](https://github.com/nostr-protocol/nips/blob/master/59.md); only the customer and the business know a booking exists.

Kind `1331` is unassigned at the checked revision of the [Nostr kind registry](https://github.com/nostr-protocol/registry-of-kinds/blob/master/schema.yaml) and is not a registered kind. It is a regular kind, only ever transmitted as a NIP-59 rumor.

## Non-goals

- Publishing open time slots or blocked dates as public events.
- Waitlists.

## Terms

- **Customer**: the party requesting a booking.
- **Business**: the party that accepts or declines bookings, identified by the public key the request is addressed to.
- **Booking id**: the event id of the `booking_request` rumor that opened the booking.
- **Bookable asset**: what a booking targets, named by an `a` tag. When no asset is named, the booking targets the business's default resource, for example a restaurant table.

## Message envelope

```jsonc
{
  "id": "<32-byte hex of the unsigned event hash>",
  "pubkey": "<sender pubkey>",
  "created_at": <unix timestamp in seconds>,
  "kind": 1331,
  "tags": [
    ["p", "<recipient pubkey>"],
    ["conversation", "<booking or exchange id>"],  // omitted on booking_request and availability_request
    ["a", "<kind>:<pubkey>:<d>"],                  // booking_request and availability_request only, optional
    ["type", "<message type>"],
    ["version", "1"]
  ],
  "content": "<JSON object for the message type>"
  // no sig: this is an unsigned rumor
}
```

- `p` (required): the recipient's public key.
- `conversation` (required on every type except `booking_request` and `availability_request`): the booking id, or for an `availability_response` the id of the `availability_request` it answers. An opening message MUST NOT carry it: its own id is the thread id.
- `a` (optional, opening messages only): the bookable asset.
- `type` (required): one of the message types below.
- `version` (required): `1`.
- `content` (required): a JSON object whose fields are defined by the message type.

Each of `p`, `type`, and `version` appears exactly once, and `conversation` and `a` at most once; a rumor that repeats one is invalid. Readers accept and ignore what this proposal does not define: further elements on a tag (such as a NIP-01 relay hint) and unknown content fields. Writers emit neither.

A recipient MUST check that the seal's signer equals the rumor's `pubkey`, and MUST validate `content` for the named type, before changing any booking state. A rumor with an unknown `type` or `version` MUST NOT be interpreted as another type. A rumor that fails any of these checks is ignored: it changes no booking state and is not answered.

The messages of a booking are ordered by the rumor's `created_at`; the gift wrap's is randomized and says nothing. A reader does not apply a message older than the last one it applied to that booking, so messages a relay replays out of order cannot undo a later one.

A `booking_request` that passes them but whose terms cannot be honoured (an `end` not after `start`, a `latestStart` before `earliestStart`, an unknown `tzid`, a malformed `phone` or `email`) is answered with `booking_declined`, `reason` `invalid_terms`.

## Booking terms

Field names and the `amount` shape follow the [Orders](https://github.com/OpenMarketsFoundation/specification/pull/10) draft.

| Field | Type | Meaning |
|---|---|---|
| `start` | string | Start of the booking. |
| `end` | string | Exclusive end, in the same form as `start`. Optional. |
| `tzid` | string | IANA time zone of the booked asset. Time-based bookings only. |
| `earliestStart` | string | Earliest start the customer would accept. Time-based only. Optional. |
| `latestStart` | string | Latest start the customer would accept. Time-based only. Optional. |
| `partySize` | integer | Number of people. Optional, default `1`; required when the asset is a bookable calendar event. |
| `quantity` | integer | Number of units of the asset, for example two rooms. Optional, default `1`. |
| `amount` | object | Total price: exactly `value` (decimal string), `denomination`, `decimals`. Set by the business. Optional. |
| `deposit` | object | The part of `amount` payable before confirmation, same shape as `amount`. MUST NOT exceed `amount`, in the same `denomination`. Set by the business. Optional. |
| `balanceDue` | string | When the rest is paid: `"at_venue"`, or an ISO 8601 date-time by which the business will request it. Required when `deposit` is present. |
| `name` | string | Booking holder. At most 200 characters. |
| `phone` | string | Holder's phone number, preferably E.164. |
| `email` | string | Holder's email address. |
| `reason` | string | `full`, `unavailable`, `not_bookable`, `invalid_terms`, `payment_not_received`, `business_cancelled`, `customer_cancelled`, or `other`. A reader treats a value it does not know as `other`. Optional. |
| `note` | string | Free text. Optional. |
| `options` | array | Available terms, in an `availability_response`. |
| `replyRelays` | array of strings | Relays for the `availability_response` when the requester has no `kind:10050`. |

A booking is **time-based** or **date-based**, fixed by its `booking_request`; every later message uses the same form.

- **Time-based**: `start`, `end`, `earliestStart`, and `latestStart` are ISO 8601 UTC date-times (`"2026-09-27T17:00:00Z"`); `tzid` is REQUIRED.
- **Date-based**: `start` and `end` are ISO 8601 calendar dates (`"2027-03-10"`), anchored in the time zone of the booked asset; `tzid`, `earliestStart`, and `latestStart` MUST be omitted. Clients MUST NOT encode a whole day as a midnight date-time.

`end` is exclusive, as in NIP-52, and MUST be after `start`: `"start": "2027-03-10", "end": "2027-03-13"` is three nights. Without `end`, a date-based booking covers the `start` day.

## Message types

| Type | Sent by | Purpose |
|---|---|---|
| `booking_request` | Customer | Initiates a booking request. |
| `booking_confirmed` | Business, or the initiator of a modification | Confirms the booking on the terms it carries. |
| `booking_declined` | Business | Declines a request that was never confirmed. |
| `booking_cancelled` | Either party | Cancels a confirmed booking, or withdraws a pending request. |
| `booking_modification_request` | Either party | Proposes replacement terms for a pending or confirmed booking. |
| `booking_modification_accepted` | Recipient of the modification | Accepts the proposed terms. |
| `booking_modification_declined` | Recipient of the modification | Rejects the proposed terms. |
| `availability_request` | Customer | Asks what is available. Opens an availability exchange, not a booking. |
| `availability_response` | Business | Offers non-binding options. |

Content per type:

- `booking_request`: `start`, `name`, and `phone` or `email` required; `tzid` if time-based; `partySize` required for a bookable calendar event; `end`, `earliestStart`, `latestStart`, `partySize`, `quantity`, `note` otherwise optional. The customer never sets `amount`.
- `booking_confirmed`: `start` required, `tzid` if time-based; `end`, `partySize`, `quantity`, `amount`, `deposit`, `balanceDue`, `note` optional. It states the whole confirmed period: an omitted `end` means the booking has none, not that it is unchanged. Omitted `partySize` and `quantity` are unchanged from the request. The terms MUST be the requested ones or inside the customer's `earliestStart`/`latestStart` window.
- `booking_declined`, `booking_cancelled`: `reason` and `note` optional. A confirmed booking ends with `booking_cancelled`, never `booking_declined`.
- `booking_modification_request`: as `booking_request`, with `name`, `phone`, `email` optional; `amount`, `deposit`, and `balanceDue` MAY be set only by the business. It describes the whole proposed booking. The asset cannot change.
- `booking_modification_accepted`, `booking_modification_declined`: `start` required, `tzid` if time-based; `end`, `note` optional.
- `availability_request`: `start` required, `tzid` if time-based; `end`, `earliestStart`, `latestStart`, `partySize`, `quantity`, `replyRelays` optional. MUST NOT carry `name`, `phone`, or `email`.
- `availability_response`: `options` required; `reason`, `note` optional. Each option carries `start`, `tzid` if time-based, and optionally `end`, `quantity`, `amount`, ordered by closeness to the requested `start`. An empty array means nothing matching is available.

Example `booking_request` for a seat at an event:

```jsonc
{
  "kind": 1331,
  "pubkey": "<customer>",
  "tags": [
    ["p", "<business>"],
    ["a", "31923:<business>:book-reading-0927"],
    ["type", "booking_request"],
    ["version", "1"]
  ],
  "content": "{\"start\":\"2026-09-27T17:00:00Z\",\"tzid\":\"America/Los_Angeles\",\"partySize\":3,\"name\":\"Maya Lopez\",\"phone\":\"+12065550100\",\"note\":\"Two of the three are four-year-olds.\"}"
}
```

## Availability

An availability exchange lets a customer ask what is free before committing to a booking: "a table for four around 7 pm" is answered with the times the business could confirm, say 6:45 or 7:30. Tables and listings publish no availability, so this is the only way to learn it, and a client MAY send the same `availability_request` to several businesses and compare the answers, which is how a search across businesses works without any central inventory.

- An `availability_response` message does not represent a booking. It only reports what options are available at the time the business sent the response. Other customers may take any of the listed options first, so a later `booking_request` for an option MAY be declined.
- To book an option, the customer sends a `booking_request` carrying that option's terms, signed with the key that will hold the booking (not a one-off key). This opens a new booking; the availability exchange is not part of it.
- A `booking_request` is a commitment. Clients MUST NOT send one to several businesses to discover availability.
- Answering is OPTIONAL for businesses. No answer within the client's timeout means unknown, not unavailable. A request whose terms cannot be honoured is answered with an empty `options` and `reason` `invalid_terms`.
- A client MAY sign an `availability_request` with a one-off key generated for that exchange. Businesses MUST address the `availability_response` to the key used to sign the `availability_request`.
- The business MUST send the `availability_response` to the relays listed in the requester's `kind:10050`. A requester with no published `kind:10050` (for example, a one-off key) MUST include `replyRelays` in the `availability_request`, and the business MUST send the response to the relays listed there. It MAY limit how many it uses and skip any it will not connect to. If both are missing, the business ignores the request.
- Businesses MAY ignore requests or answer them with delay.

## Protocol flows

Search, then book:

1. Customer sends `availability_request` to one or more businesses.
2. Each business that supports availability replies `availability_response`.
3. Customer sends `booking_request` with the chosen option's terms.
4. Business replies `booking_confirmed`, or `booking_declined` with `reason` `full` or `unavailable`.

Business counter-proposal:

1. Customer sends `booking_request`.
2. Business replies `booking_modification_request`.
3. Customer replies `booking_modification_accepted` or `booking_modification_declined`.
4. Business closes with `booking_confirmed` or `booking_declined`.

Modifying a confirmed booking:

1. The initiator (either party) sends `booking_modification_request`.
2. The recipient replies `booking_modification_accepted` or `booking_modification_declined`.
3. The initiator closes with `booking_confirmed` (the new terms if accepted, the original terms to keep the booking if declined) or `booking_cancelled`. Until then, the confirmed terms remain in force.

Cancellation: either party sends `booking_cancelled`.

## Relay routing

Booking messages are routed with the NIP-17 DM relay list, `kind:10050`.

- Clients MUST publish a `kind:10050` listing the relays where they receive gift wraps.
- To send, a client MUST look up the recipient's latest `kind:10050` and publish the gift wrap to every relay it lists.
- A recipient with no discoverable `kind:10050` is unroutable, except as Availability provides for `replyRelays`. A sender MAY then fall back to relays where the recipient is known to read: a customer to the business's NIP-65 read relays, a business answering a `booking_request` to the relays where it receives gift wraps.
- Senders of booking messages SHOULD also publish a gift wrap addressed to themselves. Availability messages need no copy.

## Bookable assets

The `a` tag on a `booking_request` names what is booked and applies to the whole booking.

| Asset | `a` tag | Example |
|---|---|---|
| A place at a scheduled event | `31923:<business>:<d>` (time-based) or `31922:<business>:<d>` (date-based) | A book reading, a tasting |
| A listed resource | `30402:<business>:<d>` | A hotel room, a massage |
| The business's default resource | omitted | A restaurant table |

A business SHOULD decline, with `reason` `not_bookable` or `invalid_terms`, a request that names an asset it did not author, an asset that is not bookable, or terms that do not fit the asset.

What a booking consumes depends on the asset:

| Asset | Consumes | Optional |
|---|---|---|
| Calendar event | `partySize` (places) | — |
| Listing | `quantity` (units, default 1) | `partySize`, for the business's information |
| Default resource | `partySize` | — |

A bookable asset declares its time zone with a `tzid` tag (`["tzid", "<IANA time zone>"]`); a `kind:31923` event uses its `start_tzid`. A business's `kind:0` profile MAY carry a `tzid` tag, which applies to its default resource and to any asset without one.

### Bookable calendar events

A NIP-52 calendar event (`kind:31922` or `kind:31923`) is bookable when it carries the `openmarkets` bookings tag. Its author receives the bookings. It MAY limit attendance with `capacity`:

```jsonc
["openmarkets", "bookings", "1"],
["capacity", "<positive integer>"],                 // optional; omitted means unlimited
["available", "<integer between 0 and capacity>"]   // optional; only with capacity
```

- `openmarkets`: marks the event as bookable through this proposal (`bookings`, version `1`). `booking_request` messages for the event are sent to its author. At most one per event. A client that does not implement the marker's version treats the event as not bookable.
- `capacity`: the maximum number of attendees. Omitted when attendance is unlimited. MUST NOT appear without the `openmarkets` bookings tag. A confirmed booking consumes `partySize` places.
- `available`: places still open, as last published by the business. Advisory; the `booking_confirmed` or `booking_declined` reply is authoritative.

```jsonc
{
  "kind": 31923,
  "pubkey": "<business>",
  "content": "Story time for ages 4 to 6.",
  "tags": [
    ["d", "book-reading-0927"],
    ["title", "Kindergarten Book Reading"],
    ["start", "1790528400"],
    ["end", "1790532000"],
    ["start_tzid", "America/Los_Angeles"],
    ["D", "20723"],
    ["openmarkets", "bookings", "1"],
    ["capacity", "25"],
    ["available", "7"]
  ]
}
```

Clients:

- MUST book the event with a `booking_request` to the event's author, with the event's coordinate in `a` and `start` naming the same instant as the event's start (`tzid` from `start_tzid`), or the same date for a `kind:31922` event;
- MUST NOT offer a `kind:31925` RSVP as the way to book it, and MUST NOT treat a `kind:31925` as a confirmed booking;
- SHOULD NOT send a request when `available` is smaller than the intended `partySize`.

The business:

- when `capacity` is present, MUST decline, with `reason` `full`, a request that would take confirmed attendance above it, and MUST NOT count `kind:31925` RSVPs toward it;
- MUST NOT lower `capacity` below the places already confirmed;
- MAY republish the event with an updated `available`; every publish of a bookable event SHOULD go through one publisher, and each republish MUST carry a strictly greater `created_at`;
- when cancelling the event, MUST send `booking_cancelled` with `reason` `business_cancelled` to every confirmed booking.

A recurring bookable event is a finite series: each date is its own `kind:31922` or `kind:31923` occurrence with its own `openmarkets` bookings tag, `capacity`, and `available`. The finite series may be grouped by a `kind:31924` calendar. A booking names one occurrence.

### Bookable listings

A NIP-99 `kind:30402` listing (a hotel room, a massage, a meeting room) is bookable when it carries the `openmarkets` bookings tag, as on a calendar event; its author receives the bookings. The listing describes the resource with the tags of the [Marketplace Listing Extension](https://github.com/OpenMarketsFoundation/specification/pull/9); they apply to bookings of it as follows:

- `quantity`: how many units of the resource exist. A booking's `quantity` MUST NOT exceed it.
- `minDuration`: the shortest booking the business accepts.
- `price` with a frequency (per night, per hour): the rate from which the business computes `amount`.
- `cancellationPolicy`: the refund rules used in Payments.
- `autoAccept` `true`: the business confirms valid requests without manual review.

`capacity` and `available` are defined for calendar events only: they count people at one occurrence, consumed by `partySize`. A listing's `quantity` and `stock` count units, consumed by a booking's `quantity`.

## Merchant preference

A business that accepts bookings for its default resource carries `["accepts_bookings", "true"]` in its `kind:0` profile. Clients SHOULD NOT offer a default-resource booking without it. Bookable events and listings are identified by their own `openmarkets` bookings tag.

## Payments

A booking that is free or paid at the venue needs no payment messages. When the business collects a deposit or the full price beforehand, payment comes before confirmation. Payments use the [Private Structured Messages](https://github.com/OpenMarketsFoundation/specification/pull/12) types unchanged (`payment_request`, `payment_proof`, `payment_confirmed`, `payment_rejected`, `refund_requested`, `refund_confirmed`), sent as `kind:1327` rumors whose `conversation` is the booking id.

1. Customer sends `booking_request`.
2. Business quotes: `booking_modification_request` with the same terms and the total `amount`, plus `deposit` and `balanceDue` when only a deposit is due now.
3. Customer replies `booking_modification_accepted`, or `booking_modification_declined`, which ends the request.
4. Business sends `payment_request` for `deposit` when quoted, otherwise for the full `amount`, with an expiration.
5. Customer pays and sends `payment_proof`.
6. Business sends `payment_confirmed`, then `booking_confirmed` with the agreed `amount`.

When the customer's `booking_request` carries the terms of a priced option from an `availability_response`, the business MAY skip steps 2 and 3.

- A `payment_request` before `booking_confirmed` means the booking is not yet confirmed. Clients MUST NOT present it as confirmed until `booking_confirmed` arrives.
- The business SHOULD keep the requested terms available until the `payment_request` expires.
- If it expires unpaid, the business sends `booking_declined` with `reason` `payment_not_received`.
- If the business confirms a payment but cannot confirm the booking, it MUST refund it and send `booking_declined`.
- When `deposit` was quoted, the balance (`amount` minus `deposit`) is paid as `balanceDue` says: at the venue, or through a later `payment_request` sent by that date-time.
- Refunds on cancellation follow the listing's `cancellationPolicy` when present. A no-show MAY forfeit a deposit only when the policy or the booking's `note` disclosed it before payment.

## Privacy

- Contact details, party size, times, and notes MUST NOT appear on the outer `kind:1059` gift wrap.
- Bookings are never published as public events; only a bookable event's aggregate `capacity` and `available` are public.
