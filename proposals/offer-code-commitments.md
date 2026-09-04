# Opaque Offer-Code Commitments for Product Listings

Status: experimental product proposal.

This proposal defines a minimal convention for reusable, self-describing
percentage offer codes authorized by a merchant's signed kind `30402` product
listing.

It does not change the current normative specification until accepted and
transposed into [../SPEC.md](../SPEC.md). The requirements below are normative
only within this proposal.

## Problem

A merchant may want to distribute product-specific offer codes through
promoters, communities, or campaigns without publishing the codes or their
meaning directly.

Keeping these offers entirely outside the product listing requires
application-specific conventions or online authorization services. Publishing
the plaintext codes makes every offer immediately discoverable.

A product listing can instead carry an opaque SHA-256 commitment. A shopper
demonstrates knowledge of the corresponding code, while the merchant's signed
listing authorizes the promotion encoded by that code.

## Goals

- Represent reusable product-specific percentage offers directly in kind
  `30402`.
- Keep the promoter label, discount percentage, and secret code out of the
  public event.
- Make offer verification deterministic across compatible clients.
- Require no promoter registry, online authorization service, encryption, or
  redemption database.
- Preserve the standard product price for clients that do not support offer
  commitments.
- Allow merchants to revoke an offer by replacing the product listing without
  its commitment.
- Carry verified promotional pricing safely through ordering and payment.

## Non-goals

This proposal does not define:

- Fixed-currency discounts.
- Cart-wide shipping discounts.
- Offer stacking.
- Automatic redemption limits.
- Single-use offers.
- Buyer-specific eligibility.
- Promoter identities or accounts.
- Redemption ledgers.
- Online offer authorization.
- Encryption or additional secret-management infrastructure.
- Automatic padding of offer commitments.

## Offer commitment

A product listing MAY contain one or more offer commitments:

```text
["offer", "1", "<commitment>"]
```

For version `1`, `commitment` is the lowercase hexadecimal representation of:

```text
SHA256(UTF8(canonical_offer_code))
```

The hash input contains exactly the canonical offer code. It contains no salt,
product coordinate, domain prefix, terminator, or additional context.

A canonical version `1` tag contains exactly three fields:

```text
["offer", "1", "<64 lowercase hexadecimal characters>"]
```

Multiple `offer` tags MAY appear in one product listing. Readers MUST ignore
malformed tags and unsupported versions without invalidating the underlying
product. Duplicate commitments have the same meaning as one commitment and
MUST NOT apply the discount more than once.

The event exposes the presence and number of commitments, not their plaintext
meaning. Cross-product linkability is described under privacy and security
considerations.

## Canonical code grammar

Version `1` codes use this structure:

```text
<promoter>-<percentage>-<word>-<word>-<word>-<word>-<word>-<word>
```

Example:

```text
conduit-15p-apple-drift-fossil-lunar-cactus-velvet
```

This code describes:

- Promoter label: `conduit`
- Product discount: 15%
- Secret: `apple-drift-fossil-lunar-cactus-velvet`

The following ABNF applies after normalization:

```abnf
offer-code-v1 = promoter "-" percent-offer 6("-" bip39-word)

promoter      = promoter-part *("-" promoter-part)
promoter-part = lower *(lower / digit)

percent-offer = percentage %x70
percentage    = nonzero-digit
              / nonzero-digit digit
              / "100"

bip39-word    = 3*8lower
lower         = %x61-7A
digit         = %x30-39
nonzero-digit = %x31-39
```

Additional requirements:

- `promoter` MUST contain between 1 and 32 characters, including internal
  hyphens.
- Every promoter part MUST begin with an ASCII letter.
- `percentage` MUST be an integer from 1 through 100.
- Percentages MUST NOT contain leading zeroes.
- Each `bip39-word` MUST exactly match an entry in the English BIP-39 word list.
  The lexical ABNF alone is insufficient to validate a word.
- A canonical code MUST contain exactly six secret words.
- A canonical code is at most 91 ASCII bytes.

Parsers MUST work from the right:

1. The final six components are the secret words.
2. The preceding component is the percentage offer.
3. All preceding components form the promoter label.

This keeps multi-part promoter labels deterministic:

```text
john-doe-20p-legal-winner-thrive-river-frozen-canvas
```

The promoter is a merchant-chosen attribution label, not a verified identity or
an account in a registry.

## Normalization

Before parsing or hashing a shopper-supplied code, a client MUST:

1. Apply Unicode NFKC normalization.
2. Remove leading and trailing ASCII whitespace: U+0009 through U+000D and
   U+0020.
3. Map ASCII `A` through `Z` to `a` through `z`.
4. Apply no other substitutions.
5. Validate the resulting value against the version `1` grammar.
6. Rejoin the parsed components using exactly one ASCII hyphen-minus, U+002D.

Clients MUST NOT silently:

- Replace underscores with hyphens.
- Replace internal spaces with hyphens.
- Treat remaining Unicode dash characters as ASCII `-`.
- Remove or collapse hyphens.
- Correct misspelled secret words.
- Accept additional or missing secret words.

NFKC compatibility forms are handled only by step 1. For example, fullwidth
Latin letters and fullwidth hyphen-minus normalize to their ASCII forms; an en
dash or em dash does not become a valid separator.

For example:

```text
 CONDUIT-15P-APPLE-DRIFT-FOSSIL-LUNAR-CACTUS-VELVET
```

normalizes to:

```text
conduit-15p-apple-drift-fossil-lunar-cactus-velvet
```

## Code generation

An authoring client generating a version `1` code MUST:

1. Validate and normalize the promoter label.
2. Encode the percentage as its canonical decimal integer followed by `p`.
3. Select six independent uniform indexes from `0` through `2047` using a
   cryptographically secure random generator.
4. Resolve each index through the English BIP-39 word list.
5. Join every component with ASCII `-`.
6. Generate a new secret if its commitment duplicates another active offer
   known to the authoring client.

Repeated words are valid because each selection is independent.

The secret words provide 66 bits of entropy. The promoter and percentage are
assumed to be observable or guessable and contribute no security.

Offer-code generation MUST NOT use `Math.random()` or a BIP-39 mnemonic
generator. These codes use the BIP-39 vocabulary for readability but are not
wallet mnemonics, recovery phrases, or seed material.

The reference vocabulary is the official 2,048-word
[English BIP-39 word list](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt).
Version `1` uses the list whose UTF-8 file, with one word per line and a final LF,
has this SHA-256:

```text
2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda
```

## Validation

When a shopper submits an offer code, a supporting client MUST:

1. Normalize and parse the complete code.
2. Extract the proposed promoter label and percentage.
3. Hash the complete canonical code.
4. Resolve the merchant's current signed kind `30402` for the product.
5. Require an exact matching version `1` offer commitment.
6. Apply the percentage only after that match succeeds.

The commitment authenticates the complete code. Changing any component,
including the promoter or percentage, produces a different commitment.

A malformed code and a well-formed but unauthorized code SHOULD produce the
same shopper-facing result. Clients should not reveal which portion of an
unsuccessful code was meaningful.

## Percentage semantics

`Np` means `N` whole percent off the unit price of the product carrying the
matching commitment.

For settlement in integer satoshis:

```text
basis_points = N * 100

discounted_unit_sats =
  ceil(base_unit_sats * (10000 - basis_points) / 10000)
```

The discount:

- Applies independently to every unit of the matched product.
- Applies before multiplying by quantity.
- Does not change any shipping cost.
- Does not stack with another offer.
- May reduce the product unit price to zero when the code contains `100p`.
- Applies to multiple products only when each current product listing contains
  the matching commitment.

When a product price requires conversion into satoshis, the client MUST first
establish the canonical base unit price in satoshis and then apply the
percentage. This fixes the conversion and rounding order; it does not define
an exchange-rate source or replace the checkout's existing quote agreement.
Calculations MUST preserve exact integer arithmetic without overflow.

## Order and payment integrity

A promotion MUST NOT exist only as a modified interface total.

Before submitting an order or initiating payment, a client MUST refresh its
normal addressable-event resolution for the product, revalidate the commitment,
and recompute the price. A bounded relay read is not proof that no newer event
exists anywhere on the network. Unavailable listing evidence MUST NOT be
reported as proof that the merchant revoked the code.

The encrypted order evidence SHOULD include:

- The canonical offer code.
- The matched commitment.
- The product coordinate and exact product event identifier.
- The base unit price.
- The percentage.
- The discounted unit price.
- The resulting item subtotal.

When carried as order evidence, the code and the commitment's association with
that order MUST remain inside the encrypted order. Clients MUST NOT add this
redemption evidence to public zap requests, public order metadata, analytics,
logs, or URLs. The product listing's standalone commitment remains public. The
final payment amount may remain public according to the chosen payment method.

A merchant client SHOULD independently normalize the code, recompute its
commitment, verify the referenced product listing, and reproduce the discounted
price before accepting a promotional order or issuing its invoice.

A service preparing an anonymous zap or other automatic payment authorization
MUST perform the same validation independently. It MUST NOT trust a
shopper-supplied discounted total. This requirement applies to existing payment
services; it does not require a separate offer-authorization service.

If current offer or pricing evidence cannot be established, a client MUST NOT
continue with automatic payment using the discounted amount. It MAY use an
order-first flow so the merchant can review the request. It MUST NOT silently
remove the discount to continue payment at the undiscounted amount.

If an offer has been revoked or the authorized price has changed, the client
MUST return the shopper to price review. It MUST NOT silently remove the
discount and charge the higher undiscounted total.

This proposal identifies verification evidence, not a new order-message kind
or envelope. Existing encrypted order transport remains in place.

## Revocation and rotation

A merchant revokes an offer by publishing a replacement kind `30402` without
the corresponding commitment.

Old signed product events may remain available from relays. Implementations
therefore MUST resolve the current addressable product event rather than
treating the existence of any historical matching event as authorization for a
new promotional order.

Revocation prevents new cooperating clients from applying the removed
commitment. It does not erase previously distributed codes or historical events
and does not retroactively change an already accepted order's agreed price.

Merchants MAY rotate leaked or overused codes at any time by removing their
commitments and generating replacements. Version `1` defines no independent
code-expiration field or atomic redemption limit.

## Privacy and security considerations

The six-word secret provides 66 bits of entropy when generated uniformly. This
is intended for reusable, economically bounded promotional offers, not for
identity keys, financial custody, or account authentication. Public commitments
permit offline guessing; the random words, not hashing alone, provide the
resistance to that attack.

Codes are transferable. Anyone who receives a valid code can use or
redistribute it. This is an accepted property of the model.

A merchant that uses the same complete code across multiple products publishes
the same commitment on each product, making those commitments linkable.
Merchants SHOULD generate separate codes when cross-product linkability is
undesirable.

The number of published commitments is observable. A merchant MAY add randomly
generated, unissued commitments as padding. An observer without the codes
cannot distinguish a padding commitment from a distributed offer commitment
from the digest alone. Automatic padding behavior is outside version `1`.

## Compatibility

Clients that do not implement this proposal continue to use the standard
product price and ignore the unknown `offer` tags.

Clients implementing this proposal MUST ignore unsupported offer versions
rather than guessing their grammar or pricing semantics.

This proposal does not alter kind `30402` addressability, base-price tags,
shipping-option references, or encrypted order transport.

[NIP-99](https://github.com/nostr-protocol/nips/blob/master/99.md) permits
additional structured tags. The current
[Open Markets product-listing definition](../SPEC.md#product-listing-kind-30402)
does not define an equivalent offer-code commitment.

If accepted, the commitment, code grammar, normalization, price semantics, and
private verification evidence should be incorporated together. Publishing only
the tag shape would leave clients unable to agree on what its preimage
authorizes.

## Future extensions and open design questions

None of the following questions block percentage offers in version `1`.

### Fixed-currency discounts

A fixed-value offer requires an unambiguous amount and currency representation.
A shorthand such as `5d` does not identify a standard currency and cannot
safely describe whether the value means dollars, the product currency, or a
settlement-currency amount.

A future grammar may define fixed-value offers using explicit currency
abbreviations. That proposal must specify:

- Currency identifiers.
- Decimal or minor-unit representation.
- Conversion timing.
- Rounding.
- Behavior when the offer currency differs from the product or settlement
  currency.

This can be defined without changing the commitment model, but it is not needed
for version `1`.

### Cart-wide shipping offers

Shipping is calculated for a cart, selected shipping options, and potentially
multiple products. A shipping commitment attached to one product cannot
unambiguously authorize the removal of every shipping charge in a multi-item
cart.

A future shipping offer should therefore be checkout- or cart-scoped. A
successfully validated code would waive the complete selected shipping total
rather than modifying one product's shipping contribution. For a cart spanning
multiple merchants, that extension must preserve each merchant's authority over
their own shipping charges.

That extension must define where the merchant publishes the commitment, which
shipping components it covers, and how it behaves when shipping is manual,
unavailable, or repriced. It should not overload the product-level percentage
grammar.

### Redemption or stock limits

Merchants may want an offer to remain valid for a fixed number of redemptions.

A static public commitment cannot provide atomic redemption counts across
concurrent decentralized clients. Defining automated offer inventory would
require authoritative counting, reservation, race, and recovery semantics.

Merchants can already manage practical limits by monitoring accepted orders
and removing the commitment when their chosen threshold is reached. This is a
merchant-managed policy, not a strict concurrent-redemption guarantee. A
standardized automatic stock mechanism may be added later if implementation
experience justifies the additional state.

Fixed-currency and shipping tokens are unsupported in version `1`. Any future
extension must specify an explicit version and MUST NOT reinterpret existing
version `1` codes. Useful reusable percentage offers do not depend on resolving
these extensions first.

## Reference vector

```text
Input:
conduit-15p-apple-drift-fossil-lunar-cactus-velvet

Canonical code:
conduit-15p-apple-drift-fossil-lunar-cactus-velvet

SHA-256:
6b124b674d946a2ce783e70053d681ebb4854f8fcfa85a023f895b49106aa611

Product tag:
["offer", "1", "6b124b674d946a2ce783e70053d681ebb4854f8fcfa85a023f895b49106aa611"]
```

For a base unit price of 101 sats, this 15% offer produces a discounted unit
price of 86 sats. A quantity of three produces an item subtotal of 258 sats;
shipping remains unchanged. A `100p` offer produces a zero-sat unit price.

## References

- [NIP-01: Basic protocol flow](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [NIP-17: Private direct messages](https://github.com/nostr-protocol/nips/blob/master/17.md)
- [NIP-99: Classified listings](https://github.com/nostr-protocol/nips/blob/master/99.md)
- [Open Markets specification](../SPEC.md)
- [BIP-39 English word list](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt)
- [Unicode normalization forms](https://www.unicode.org/reports/tr15/)
