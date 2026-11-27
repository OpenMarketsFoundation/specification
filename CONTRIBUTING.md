# Contributing to Open Markets

Open Markets is a commerce specification for Nostr. A proposal should give independent implementations enough information to exchange the same event and agree on what it means. Clients can then choose how to present it, store it, and act on it.

## Opening a proposal

Open a pull request against `main` and edit the relevant section of `README.md`. Keep each proposal focused on one change that can be reviewed and implemented on its own.

Use **`(Area) Change`** for the proposal and PR title. Inside the parentheses, name the part of commerce being changed. After the parentheses, start with a verb and say what the proposal does. If the change touches several areas, choose the one an implementer would look under first.

- `(Orders) Add merchant-signed payment receipts`
- `(Shipping) Define destination exclusions`
- `(Listings) Add product modifiers`

Use the PR description to explain the problem, link related work, and identify decisions that need review. Keep the proposed specification readable on its own after the PR discussion is gone.

## Writing the specification

Use [NIP-99](https://github.com/nostr-protocol/nips/blob/master/99.md) as a model for structure and scope.

### 1. State the scope and status

In the first sentence, identify the event kind or kinds and what the proposal defines or changes. For example, “A kind `30406` shipping option may exclude destinations by country, subdivision, or postal code.”

Put applicable status labels directly below the proposal title. `draft` describes work under discussion, `optional` means implementations may choose whether to support the feature, and `unrecommended` identifies an existing convention discouraged for new use. Apply the label to the feature or proposal it describes.

Before introducing a kind, check whether an existing event already represents the same thing. If a new kind is needed, choose its [NIP-01 range](https://github.com/nostr-protocol/nips/blob/master/01.md) according to how the event behaves.

| Event behavior | Typical use |
|---|---|
| Regular | A distinct record with its own event ID. |
| Replaceable | One current value per author and kind, such as a preference. |
| Ephemeral | A transient signal that relays need not retain. |
| Addressable | An author can update each named item independently using its `d` tag, as with a product listing or shipping option. |

### 2. Define the event format

State what belongs in `.content` and how another client interprets it. Specify whether it contains plain text, Markdown, serialized JSON, or an empty string. Keep structured fields that clients need to find or filter in tags when appropriate.

Reuse established NIPs, kinds, and tags wherever their meanings fit. Examples include `d` for an addressable identifier, `t` for a category, `g` for a geohash, `imeta` for media metadata, and `alt` for a human-readable fallback. Link to the existing definition and document what the commerce proposal adds.

Show each new tag as a positional array. **Every tag element is a string**, including quantities, prices, and timestamps. Document:

- What each position means, which positions may be omitted, and what omission means.
- Whether the tag is required or optional and whether it may repeat.
- Accepted values, units, precision, and applicable standards, such as ISO 4217 currency codes or Unix timestamps in seconds.
- How repeated tags or overlapping values combine when that affects the result.

For example, `["item", "30402:<merchant-pubkey>:<d-tag>", "<quantity>"]` tells a reader where the listing reference and quantity go. The accompanying text should also say whether quantity must be a positive whole number and how to represent an order containing several products.

### 3. Specify the rules needed for interoperability

Use `MUST` and `MUST NOT` for requirements, `SHOULD` and `SHOULD NOT` for recommendations with room for justified exceptions, and `MAY` for optional behavior. Use them sparingly.

Be precise where a different interpretation would change the outcome. For an order message, that may mean identifying who can send it and which order it refers to. For a shipping rate, it may mean saying whether a weight limit is inclusive or a charge applies once per shipment or once per item.

Leave UI, storage, deployment, and application policy to implementers. Introduce a required message sequence only when the order of messages matters to interoperability or cryptography. Keep commerce-specific validation, aggregation, and business rules off relays. Avoid nested payloads that duplicate tags or hide fields another client needs to interpret.

### 4. Include a complete example

Include a realistic, valid, copy-pasteable event in JSON or YAML. Show the required fields and common optional tags. Use an unsigned inner event when that is the object being specified. If an example is presented as signed, its ID and signature should verify.

Where the proposal defines a calculation or matching rule, give the expected result as well. A shipping example is more useful when a reviewer can tell exactly what two clients should charge for the same basket.

## Before merging

Early ideas are welcome as draft PRs. **Before merging new protocol behavior into `main`, we prefer to see it in use.** Link to a working implementation and show an event it produces or consumes. Ideally, one independent implementation produces the event and another interprets it correctly.

Be clear about what has been demonstrated. A fixture can establish an expected result. A working exchange can show that two implementations agree. Keep speculative fields and workflows in the PR discussion until there is a concrete use for them. Editorial corrections and clarifications can be reviewed on their own merits.
