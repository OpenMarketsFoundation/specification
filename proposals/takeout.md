# Takeout: Pickup Orders on the Private Commerce Envelope

Status: experimental proposal. This page is not current normative Open Markets text.

## Problem

A café takes an order for pickup. To make it work at the counter, the two sides need to say a few things the base messages of the [private commerce envelope](https://github.com/OpenMarketsFoundation/specification/pull/12) do not carry:

- the café needs to know whose bag it is: the customer's name and a telephone number to reach them;
- the customer may ask for a pickup time;
- the café answers with when the order will be ready and a short code the customer says at the counter;
- when the café turns an order down because something ran out, it says which items.

The envelope keeps its base messages thin on purpose and gives implementers one place to add what a kind of business needs: a named entry in `extensions`. This proposal defines that entry for takeout. It is one name, `openmarkets:takeout`, with a small content on each of the three messages it appears on.

Synvya runs takeout on this design for restaurants today. The example below is a real order.

## Non-goals

- Delivery, table service, or anything other than the customer collecting the order.
- Payment. The envelope's payment messages cover it; see *Paying at the counter* for the one rule this proposal adds.
- Scheduling rules: how far ahead a pickup time may be, in what steps. A merchant decides those and declines what it cannot honour.

## Terms

- **Customer**: the party that sends the order; the author of the `order` rumor.
- **Merchant**: the party that answers; the recipient of the `order`.
- **Pickup option**: the merchant's `kind:30406` shipping option with `service` = `pickup`, which the order's delivery selection names with method `pickup`.

## The `openmarkets:takeout` entry

The entry appears inside `extensions` on four message types.

| Message | Author | Fields in `openmarkets:takeout` | In `requires`? |
|---|---|---|---|
| `order` | customer | `name`, `tel`, `pickup_at` | Always |
| `order_accepted` | merchant | `ready_at`, `tzid`, `code`, `pay_at_pickup` | Only if the order required the entry |
| `order_cancelled` | merchant | `unavailable` | Only if the order required the entry |
| `fulfillment_update` | merchant | `ready_at`, `tzid`, `code` (a revised time) | Only if the order required the entry |

**When the entry is required, and when it is not.** The envelope's rule is that `requires` names only what a reader needs to understand the action, and that a reader refuses a message whose `requires` names something it does not know. An order for pickup is no use to a merchant that cannot read who to hand the bag to, and a customer who asks for a pickup time needs the merchant to honour it or decline, so the entry is always required on the `order`. An acceptance is understood without a ready time, and a decline without the line list, so on the merchant's messages the entry is optional unless the customer's order itself required it; then the customer's client has shown it knows the entry, and the merchant may require it back. A merchant also writes the ready time and the code into the message's `note` as prose, so a plain client that ignores the entry still shows a usable acceptance.

Every time is a whole number of seconds since the Unix epoch. `tzid` is an IANA timezone name, so a client can show the time as the merchant's wall clock.

### On the order

```jsonc
"extensions": { "openmarkets:takeout": { "name": "Carlos", "tel": "+12065550101", "pickup_at": 1791640800 } },
"requires": ["openmarkets:takeout"]
```

`name` is what staff call out when they hand over the bag, and `tel` is a telephone number to reach the customer about the order. Both are required and are personal data: a client sends them only to the merchant the customer is ordering from, and a merchant does not put them in a URL, a log line or an error report. They live in this entry, not in the delivery selection's `contact`, because that object has no field for a name and a client should not have to look in two places for who the order is for.

`pickup_at` is when the customer would like to collect. When it is absent, the customer wants the order as soon as possible. An order for pickup carries one delivery selection with `method` = `pickup` naming the merchant's pickup option; the entry adds the customer and the time.

Accepting an order that carries `pickup_at` means the order will be ready by that time: `ready_at` is not later than `pickup_at`. A merchant that cannot honour the time (too soon, too far ahead, outside its hours) declines the order with the reason `pickup_time`; it does not accept with a later time.

### On the acceptance

```jsonc
"note": "Ready at 6:15 AM. Say JQE7 at the counter. Pay when you collect.",
"extensions": { "openmarkets:takeout": { "ready_at": 1791638100, "tzid": "America/Los_Angeles", "code": "JQE7", "pay_at_pickup": true } }
```

`ready_at` is when the order will be ready to collect. `code` is a string of 3 to 8 letters and digits that the customer says at the counter so staff can match them to the bag; it is not a secret and proves nothing. A client shows the code large and the time in the merchant's zone.

`pay_at_pickup` says whether the customer pays when collecting. `true` means no payment message will follow. `false` means the merchant wants payment first and will send a `payment_request`; the customer's client waits for it. The field exists so that a client never has to guess from silence whether a request is still coming.

### On a decline

```jsonc
"reason": "out_of_stock",
"refund_required": false,
"note": "Oat milk and vanilla syrup are sold out today.",
"extensions": { "openmarkets:takeout": { "unavailable": ["b2…", "c3…"] } }
```

The envelope leaves `reason` as a free lowercase string. This proposal defines two values: `out_of_stock`, which goes with `unavailable`, and `pickup_time`, for a requested time the merchant cannot honour. `unavailable` lists the `line_id`s of the lines the merchant could not fill, so a client can let the customer fix the order and send it again instead of guessing. It appears only with the reason `out_of_stock`.

### On a progress update

A café running late revises the time on a `fulfillment_update` with state `processing`, carrying `ready_at`, `tzid` and `code` in the same entry. A client replaces the time it shows; the code is repeated so the message stands on its own. This is also how a merchant gives the code on an order that had no acceptance of its own, such as a repeat delivery of a standing order.

## Referring to the order

Every reply names the order it answers in `order_operation`, the envelope's reference to an operation. It is the `operation` value of the `order` message: 32 lowercase hex characters, the pattern the envelope's schema gives the field. It is not the order rumor's event id, which is 64 characters and does not fit the pattern.

## Paying at the counter

The envelope's rule is that a merchant that wants payment sends a `payment_request`. For takeout paid at collection, the merchant sends none and says so with `pay_at_pickup: true` on the acceptance. A merchant that wants prepayment sets it to `false` and sends the request; the customer's client knows to wait for it. The payment messages themselves are unchanged.

## Advertising support

A merchant that accepts takeout orders lists the entry in its capability object. Under the envelope's rule that is a statement about what the merchant will receive: a client that sees it knows it may send a takeout `order`, with the customer's `name` and `tel` and an optional `pickup_at`. It says nothing about what the customer's client can read, which is why a merchant requires the entry on its answer only when the order required it.

```json
"versions": [{ "version": "1", "receive": ["order", "order_cancel_requested"], "extensions": ["openmarkets:takeout"] }]
```

## Worked example

A customer, Carlos, orders a 12 oz latte with oat milk and two pumps of vanilla, as soon as possible, from a café that closes at 22:00. It is 23:13, so the café, which accepts orders while closed for its next opening, answers with a time tomorrow morning.

```jsonc
// order (customer → café), content
{
  "buyer": "<customer>", "merchant": "<café>",
  "items": [
    { "line_id": "a1…", "listing": { "coordinate": "30402:<café>:latte-12-oz",   "event_id": "…" }, "quantity": "1", "unit": "item", "amount": { "value": "4.5", "unit": "USD" } },
    { "line_id": "b2…", "listing": { "coordinate": "30402:<café>:oat-milk",      "event_id": "…" }, "quantity": "1", "unit": "item", "amount": { "value": "0.6", "unit": "USD" } },
    { "line_id": "c3…", "listing": { "coordinate": "30402:<café>:syrup-vanilla", "event_id": "…" }, "quantity": "2", "unit": "item", "amount": { "value": "1", "unit": "USD" } }
  ],
  "total": { "value": "6.1", "unit": "USD" },
  "deliveries": [{ "delivery_id": "d4…", "line_ids": ["a1…", "b2…", "c3…"], "method": "pickup", "shipping_option": { "coordinate": "30406:<café>:pickup", "event_id": "…" } }],
  "extensions": {
    "openmarkets:modifiers": { "b2…": "a1…", "c3…": "a1…" },
    "openmarkets:takeout": { "name": "Carlos", "tel": "+12065550101" }
  },
  "requires": ["openmarkets:modifiers", "openmarkets:takeout"]
}

// order_accepted (café → customer), content
{
  "order_operation": "<the order's operation, 32 hex>",
  "note": "Ready at 6:15 AM tomorrow. Say JQE7 at the counter. Pay when you collect.",
  "extensions": { "openmarkets:takeout": { "ready_at": 1791638100, "tzid": "America/Los_Angeles", "code": "JQE7", "pay_at_pickup": true } }
}
```

The customer's screen shows "Ready at 6:15 AM tomorrow", the code JQE7, and "pay at the counter"; the café's screen shows Carlos and his number. A client that does not know the entry shows the note, which says the same. Amounts are written as the envelope's money type requires, with no trailing zeros: `"4.5"`, not `"4.50"`.

## Compatibility

- The entry is an `extensions` entry under the envelope's own rules; nothing in the base messages changes.
- A merchant that does not list `openmarkets:takeout` in its capabilities is not sent a takeout order, and a client never sends the entry to it.
- A client that does not know the entry still shows an acceptance, a decline or a progress update, because the merchant does not require the entry on them unless the order did, and the `note` carries the time and the code as prose.

## Open questions

- Whether `code` should be optional for merchants that match orders by name alone.
- Whether the customer's `name` and `tel` belong here or in a general contact entry that other kinds of order would share. They are here so a takeout client reads one entry; a later proposal can move them without changing the messages that carry them.
- Whether `pay_at_pickup` belongs here or in a general payment-terms entry that other kinds of order would share.
- Whether a merchant should be able to answer a `pickup_at` it cannot honour with a counter-proposal, instead of a decline. This proposal keeps accept or decline only.
