# Merchant Shipping Tables and Combined Basket Pricing

Status: experimental delivery proposal.

This proposal adds a calculated shipping mode to kind `30406`. It defines
merchant-authored shipping terms that independent clients can evaluate for a
bundle of products. It does not change the current normative specification
until accepted and transposed into [../SPEC.md](../SPEC.md). Requirements below
are normative only within this proposal.

## Problem and approach

A shipping charge depends on the destination and the bundle being purchased.
A fixed price on an option cannot, by itself, express combined basket weight,
packing adjustments, handling, or free shipping above a merchandise threshold.
Charging the same shipping price for every item also repeats costs that the
merchant intended to charge once for the bundle.

Merchants instead publish reusable destination and weight-band tables. Products
explicitly reference a table and supply their own weight and optional packing
and handling adjustments. A client calculates one shipping charge for the
eligible bundle. No hosted calculator or carrier API is required.

The protocol defines portable merchant terms and their calculation. Clients
own address forms, input normalization, country-specific validation, currency
conversion, merchant guidance, and shopping UI. A simple editor and an advanced
editor can publish the same policy.

## Scope

This profile supports physical shipping with:

- merchant-owned reusable policies and explicit product references;
- destination-specific bands of combined weight;
- optional packing weight and handling per product, multiplied by quantity;
- separate domestic and international free-shipping thresholds; and
- one agreed shipping charge per compatible bundle.

Dimensions remain optional product metadata. Clients may use them to suggest
packing or handling adjustments. This profile does not calculate dimensional
weight, optimize packages, prescribe carriers, or claim that a fee schedule is
a carrier quotation. Those capabilities can be developed independently.

## Calculated kind-30406 mode

A table option retains human-readable `content` and these tags:

```text
["d", "<merchant-chosen-policy-id>"]
["title", "<shipping-method-title>"]
["country", "<country-code>", "..."]
["service", "<standard|express|overnight>"]
["shipping_table", "1", "<JSON-policy>"]
```

There MUST be exactly one `shipping_table` tag with the supported version and
one JSON policy whose `version` matches the tag. The policy author MUST be the
merchant whose products use it.
The `country` tag is a discovery summary: it MUST contain exactly the distinct
countries in the policy's rules. It does not independently establish eligibility.

**A calculated option MUST NOT contain a fixed `price` tag.** Its price is the
result of evaluating the bundle, not a first-band price or a placeholder zero.
This proposal changes the current requirement for `price` to apply only to
fixed-price options. A `shipping_table` option is a separate calculated mode.
Existing fixed-price options remain available.

Version 1 does not combine a table with legacy `region`, weight/dimension limits,
or `price-weight`, `price-volume`, or `price-distance` calculations. Their
composition is undefined in this profile and MUST NOT be guessed. All table
destination and weight terms are expressed in its JSON policy.

### Policy document

```json
{
  "version": 1,
  "originCountry": "US",
  "currency": "USD",
  "domestic": {
    "rules": [
      {
        "country": "US",
        "bands": [
          { "maxWeightGrams": 1000, "priceMinor": 600 },
          { "maxWeightGrams": 2000, "priceMinor": 900 }
        ]
      },
      {
        "country": "US",
        "subdivision": "US-AK",
        "bands": [
          { "maxWeightGrams": 1000, "priceMinor": 1200 },
          { "maxWeightGrams": 2000, "priceMinor": 1800 }
        ]
      }
    ],
    "freeShippingThresholdMinor": 7500
  },
  "international": {
    "rules": [
      {
        "country": "CA",
        "bands": [
          { "maxWeightGrams": 1000, "priceMinor": 1800 },
          { "maxWeightGrams": 2000, "priceMinor": 2500 }
        ]
      }
    ],
    "freeShippingThresholdMinor": 15000
  }
}
```

Required fields are `version`, `originCountry`, `currency`, `domestic`, and
`international`. Each table is either `null` (no service) or an object containing
a nonempty `rules` array and an optional `freeShippingThresholdMinor`. At least
one table MUST be present. Each rule contains `country`, optional `subdivision`
and `postalPrefix`, and a nonempty `bands` array. Each band contains
`maxWeightGrams` and `priceMinor`. Unknown fields or unsupported versions make
the policy unsupported for automatic calculation; clients MUST NOT ignore
potential price or eligibility terms.

Weights are positive integer grams. Band limits MUST strictly increase. Prices
and thresholds are nonnegative integer minor units of the declared currency.
For example, USD `600` means USD 6.00. Clients determine the supported currency's
precision and perform exact arithmetic; a client that cannot represent the
declared terms cannot calculate that policy.

Countries use uppercase ISO 3166-1 alpha-2 codes. Subdivisions use complete
uppercase ISO 3166-2 codes, such as `US-AK`, belonging to the rule's country.
Postal prefixes contain nonempty uppercase ASCII letters and digits and are
country-scoped. Clients prepare canonical destination values from user input;
this proposal does not prescribe an address form or address-validation service.

Domestic rules MUST use `originCountry`; international rules MUST use other
countries. Duplicate `(country, subdivision, postalPrefix)` selectors are
invalid. A missing country rule means that the table does not serve that country.

### Destination and band selection

Select the domestic table when the buyer's country equals `originCountry`, or
the international table otherwise. A rule matches when its country matches and
every supplied subdivision and postal-prefix selector matches. Subdivision
comparison is exact; a postal prefix matches the start of the canonical postal
value. A rule with both selectors requires both to match.

Among matching rules, the longest postal prefix wins; at equal prefix length,
a subdivision-specific rule wins over a country-only rule. This ordering
defines merchant terms, independently of how a client collects the address.
Clients MUST obtain the destination components necessary to distinguish the
applicable rules; missing subdivision or postal information MUST NOT silently
select a cheaper country fallback. No matching rule means no automatic quote.

After combining weight, select the first band whose `maxWeightGrams` is greater
than or equal to that weight. Upper boundaries are inclusive. Weight above the
last band is ineligible for an automatic quote.

Destination exclusions are separate from price overrides. For example, the
Alaska rule above charges a different rate; it does not exclude Alaska. The
existing [destination-constraints proposal](https://github.com/OpenMarketsFoundation/specification/pull/13)
addresses explicit include/exclude eligibility. If used together, its eligibility
check precedes table pricing, and an exclusion cannot be overridden by a matching
rate row or a free-shipping threshold. That proposal remains experimental and
is not required to use the country/subdivision/prefix rules defined here.

## Product terms

Each shipped physical kind-30402 product explicitly references the merchant's
policy and supplies its own positive weight in grams:

```text
["shipping_option", "30406:<merchant-pubkey>:<policy-id>"]
["weight", "400", "g"]
["dim", "20x15x10", "cm"]
["shipping_adjustments", "1", "{\"weightAllowanceGrams\":100,\"handling\":{\"amount\":\"1.00\",\"currency\":\"USD\"}}"]
```

The `dim` and `shipping_adjustments` tags are optional. The adjustments document
has only optional `weightAllowanceGrams` and `handling` fields; omitted values
mean zero. Packing allowance is a nonnegative integer in grams. Handling is an
object with a nonnegative decimal-string `amount` and a `currency` equal to the
product's price currency. There MUST NOT be multiple adjustment tags or unknown
adjustment fields. The tag version and document shape MUST be supported before an
automatic quote can be offered.

Table references MUST omit the legacy `shipping_option` extra-cost element;
per-product fees use `handling` so they cannot be counted twice. Every physical
variation supplies its own terms. A client may offer a control to copy conservative
measurements across variations, but the published terms remain explicit on each
product. Digital products and pickup items do not enter a shipping bundle.

## Bundle calculation

A compatible bundle shares the merchant, selected policy coordinate, exact
signed policy revision, and delivery destination. All shipped physical lines
using that selected coordinate and destination MUST participate in the same
bundle. A client MUST NOT split the bundle to select different policy revisions
or apply the charge or threshold more than once. Other merchants, destinations,
policies, digital items, and pickup items are outside that bundle.

For positive integer item quantities:

```text
combined grams = sum((item grams + packing allowance grams) × quantity)
handling = sum(item handling × quantity)
shipping charge = selected band price + handling
```

The band price is the total for the bundle's weight, not a per-item fee. Handling
is expressed in policy currency for addition. Qualifying merchandise subtotal
is the agreed merchandise value of shipped items in that bundle, expressed in
policy currency. It excludes shipping, tax, digital items, and pickup items.
Agreed discounts affect that merchandise value; this proposal introduces no
discount or offer-code mechanism.

If the table has a threshold and the qualifying subtotal is greater than or
equal to it, **the entire shipping charge, including handling, is zero**.
Merchants choose rates and thresholds accordingly. Eligibility and a matching
weight band MUST be established before applying the threshold. A zero threshold
means free shipping for every eligible bundle; an absent threshold means no
threshold waiver. Neither unsupported destinations nor overweight bundles become
eligible because their merchandise value exceeds a threshold.

Product and policy currencies may differ. Exchange-rate sources, freshness,
conversion and rounding strategies, settlement conversion, and UI disclosure
are client implementation responsibilities. This profile does not mandate a
provider or shared conversion snapshot format. Clients remain responsible for
obtaining agreement to the resulting order amount. Identical policy-currency
inputs MUST yield the same table result; different conversion inputs need not
yield identical amounts.

## Order agreement and client responsibilities

Clients MUST bind the agreed shipping charge to the selected policy revision,
product revisions, quantities, destination, and bundle. Retries MUST preserve
the agreed terms rather than silently reprice an existing order against a newer
table. How clients retain evidence, allocate the charge across lines, and encode
it in their supported private order flow is implementation work; this proposal
does not define a new order envelope or payment protocol.

Clients own:

- simple or advanced table editors, presets, previews, and merchant guidance;
- address entry, normalization, country-specific validation, and error repair;
- display units and conversion of authored weights into signed integer grams;
- dimensional warnings and suggestions for packing or handling adjustments;
- currency conversion and settlement; and
- explaining coverage, thresholds, and the final combined charge to buyers.

These choices MUST preserve the published policy's meaning. Buyer address data
MUST NOT be published in public shipping policies or product events.

Missing required weight or destination data, unknown versions, malformed terms,
unresolved required evidence, and ineligible bundles mean no automatic quote.
They never imply zero shipping. Clients may let the buyer contact the merchant
or place an order for coordination instead.

## Compatibility and adoption

The current fixed-price kind-30406 representation remains useful for fixed
options. This proposal adds the missing bundle-dependent mode; preserving the
old required fixed price is not a design constraint on that mode.

Fixed-only readers that require `price` will reject a table option rather than
mistake its first band for a quote. Table-aware readers MUST detect and evaluate
the complete supported table before offering a calculated charge. This does
not claim that every deployed client validates the current specification.

Conduit has implemented the model using application-specific
`conduit_shipping_table` version 2 and `conduit_shipping_adjustments` version 1
tags. The neutral tag names and version 1 policy in this proposal are proposed
wire semantics, not claims about existing emission or cross-client adoption.
The implemented model supplies practical experience; adoption of this proposal
requires explicit authoring and reader support.

If accepted, update the normative shipping-option required-field rules, product
adjustments, bundle calculation, examples, and unsupported-mode behavior together.
This PR does not transpose those semantics into the compatibility snapshot.

## Examples and validation

The policy above and [calculation fixtures](fixtures/merchant-shipping-tables.json)
exercise the shared calculation without prescribing a client implementation:

| Case | Combined weight | Merchandise subtotal | Result |
| --- | ---: | ---: | ---: |
| Two 400 g items, each with 100 g packing and USD 1 handling, US | 1000 g | USD 40 | USD 8 |
| Same basket at the domestic threshold | 1000 g | USD 75 | USD 0, including handling |
| Same basket to Alaska | 1000 g | USD 40 | USD 14 |
| Same basket to Canada, below its separate threshold | 1000 g | USD 100 | USD 20 |
| Same basket to Canada at its threshold | 1000 g | USD 150 | USD 0 |
| 2500 g basket above the domestic threshold | 2500 g | USD 100 | No automatic quote: overweight |

The fixtures additionally cover the next weight band, missing weight, unsupported
destinations, absent destination detail, specificity, and exclusion of digital
and pickup value. They are calculation examples, not proof of deployed
cross-client interoperability or carrier pricing.

## References

- [Current compatibility snapshot](../SPEC.md)
- [NIP-99 classified listings](https://github.com/nostr-protocol/nips/blob/master/99.md)
- [NIP-01 event identity and addressable events](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [Conduit shipping-table implementation notes](https://github.com/Conduit-BTC/conduit-mono/blob/main/docs/knowledge/merchant-shipping-tables.md)
- [Conduit shipping calculation and signed-term helpers](https://github.com/Conduit-BTC/conduit-mono/blob/main/packages/core/src/protocol/shipping-policy.ts)
