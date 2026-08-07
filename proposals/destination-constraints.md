# Composable Shipping Destination Constraints

Status: experimental delivery proposal.

This proposal defines deterministic destination eligibility for kind `30406`
shipping options. It does not change the current normative specification until
accepted and transposed into [../SPEC.md](../SPEC.md).

The requirements below are normative only within this proposal.

## Problem

The current shipping option shape provides a required `country` tag and an
optional `region` tag. Those tags are useful geographic identifiers, but they do
not define how country and subdivision values combine, express exclusions, or
represent postal delivery zones.

Administrative subdivisions are not carrier service areas. Common policies such
as “all of the United States except Alaska and Hawaii,” postal-prefix surcharges,
and country-specific remote-area exclusions cannot be represented without
private tags or out-of-band interpretation. Silently ignoring such constraints
can offer a fixed price to a destination the merchant did not agree to serve.

## Goals

- Keep ISO country and subdivision codes as interoperable geographic primitives.
- Express country-specific postal eligibility without arbitrary regular
  expressions.
- Support multiple disjoint fixed-price zones for one product.
- Make unsupported, incomplete, and ambiguous eligibility fail closed for
  automatic checkout.
- Preserve an order-first path when a client cannot safely evaluate an option.
- Leave room for country-specific authoring and validation without giving each
  client different matching semantics.

## Non-goals

- Defining one universal postal address form.
- Replacing carrier rate APIs, customs rules, or address validation services.
- Treating administrative subdivisions as postal delivery zones.
- Using a precise buyer location as public marketplace metadata.
- Defining arbitrary polygons, distance pricing, or local-delivery geofences in
  this first destination grammar.

## Destination schema

A shipping option using this proposal includes:

```text
["destination_schema", "1"]
```

It then includes one or more `destination` tags with one of these shapes:

```text
["destination", "<include|exclude>", "country", "<ISO 3166-1 alpha-2>"]
["destination", "<include|exclude>", "subdivision", "<ISO 3166-2>"]
["destination", "<include|exclude>", "postal", "<country>", "<exact|prefix>", "<value>"]
```

Examples:

```text
["destination", "include", "country", "US"]
["destination", "exclude", "subdivision", "US-AK"]
["destination", "exclude", "subdivision", "US-HI"]
["destination", "exclude", "postal", "US", "prefix", "967"]
```

`country` values MUST use uppercase ISO 3166-1 alpha-2 codes.
`subdivision` values MUST use complete uppercase ISO 3166-2 codes, including the
country prefix. A postal selector MUST carry its country explicitly; postal
values MUST NOT be interpreted without that country context.

The current required `country` tag remains as a derived discovery and
compatibility summary. It MUST contain every country permitted by the include
selectors and no other country. A missing or inconsistent summary is invalid.
When `destination_schema` is present, `country` MUST NOT be used by itself to
authorize destination eligibility.

## Postal normalization and matching

Postal selector values MUST contain only uppercase ASCII letters and digits.
Authoring and evaluating clients normalize postal values by:

1. trimming leading and trailing whitespace;
2. converting ASCII letters to uppercase; and
3. removing ASCII spaces and hyphens.

`exact` matches the complete normalized buyer postal value. `prefix` matches
from the beginning of that value. Empty match values are invalid.

This intentionally excludes arbitrary regular expressions and globs. They are
difficult to implement consistently across clients, invite pathological inputs,
and make interoperability depend on a particular regular-expression engine.
Country-specific clients MAY apply stricter validation before matching, but
they MUST NOT change these comparison semantics.

Numeric postal ranges may be proposed as a later match type with explicit
fixed-width and ordering rules. Clients MUST treat an unknown match type as
unsupported rather than guessing.

## Eligibility semantics

An option MUST contain at least one valid `include` selector.

For a complete buyer destination:

```text
eligible = matches at least one include AND matches no excludes
```

Include selectors form a union. Exclusions always win. There is no implicit
specificity or ordering precedence between tags.

A subdivision selector matches only when both the country and complete
subdivision code match. A postal selector matches only within its declared
country.

Before declaring an option eligible, a client MUST have every address component
needed to evaluate possible includes and applicable exclusions. For example, a
US-wide option with a US postal exclusion remains unresolved until the buyer
supplies a postal value.

An evaluating client MUST NOT offer automatic checkout when:

- `destination_schema` is unknown;
- any destination selector, effect, or match mode is unknown or malformed;
- a required buyer destination component is absent or invalid; or
- the client cannot apply the required country-specific validation safely.

The client MAY continue through an order-first flow so the merchant can confirm
availability and price.

## Multiple prices and services

Each distinct combination of service, price, currency, and destination policy
is represented by a separate kind `30406` event. A product or collection MAY
reference multiple options.

Clients evaluate every referenced option against the buyer destination. They
MUST NOT silently choose between multiple matching options. Distinct services
may be shown as explicit buyer choices. Authoring clients that intend one price
per service SHOULD produce disjoint destination policies; overlapping options
that cannot be presented as meaningful choices fall back to order-first.

### Mainland and non-contiguous United States

```jsonc
{
  "kind": 30406,
  "content": "Mainland standard shipping",
  "tags": [
    ["d", "standard-us-mainland"],
    ["title", "Standard Shipping"],
    ["price", "5.99", "USD"],
    ["country", "US"],
    ["service", "standard"],
    ["destination_schema", "1"],
    ["destination", "include", "country", "US"],
    ["destination", "exclude", "subdivision", "US-AK"],
    ["destination", "exclude", "subdivision", "US-HI"]
  ]
}
```

```jsonc
{
  "kind": 30406,
  "content": "Alaska and Hawaii standard shipping",
  "tags": [
    ["d", "standard-us-ak-hi"],
    ["title", "Standard Shipping"],
    ["price", "12.99", "USD"],
    ["country", "US"],
    ["service", "standard"],
    ["destination_schema", "1"],
    ["destination", "include", "subdivision", "US-AK"],
    ["destination", "include", "subdivision", "US-HI"]
  ]
}
```

### Country-scoped postal area

```jsonc
{
  "kind": 30406,
  "content": "Northern Ireland standard shipping",
  "tags": [
    ["d", "standard-gb-bt"],
    ["title", "Standard Shipping"],
    ["price", "8.50", "GBP"],
    ["country", "GB"],
    ["service", "standard"],
    ["destination_schema", "1"],
    ["destination", "include", "postal", "GB", "prefix", "BT"]
  ]
}
```

## Country-specific implementation

The protocol defines portable selectors and deterministic matching. Merchant
interfaces remain country-aware: they may offer states, provinces, postal
prefixes, or other appropriate controls only where the application can validate
them. A client does not need to claim support for every country's authoring
rules. It does need to fail closed whenever it cannot evaluate the published
rules for automatic checkout.

This separation avoids both extremes: ISO subdivisions are not presented as a
complete global shipping model, and country-specific behavior does not become
an undocumented client extension.

## Plus Codes and precise locations

Open Location Codes (commonly called Plus Codes) identify geographic grid cells
and can locate destinations where conventional street addressing is incomplete.
They do not model postal or carrier service areas and are not destination
selectors in schema version `1`.

A future encrypted order-address proposal MAY carry a full Open Location Code as
an optional delivery locator. Short codes require a reference locality and MUST
NOT be used without an unambiguous recovery context. Buyer location data is
sensitive and MUST NOT be published in public product or shipping-option events.

Future local-delivery work may define explicit geospatial coverage selectors.
That work should specify cell, polygon, or distance semantics independently of
postal eligibility instead of overloading the current `g` pickup-location tag.

## Compatibility and migration

- A legacy option containing only `country` remains readable under the current
  specification but does not express exclusions.
- A legacy `region` value may be migrated to an included `subdivision` only when
  the author confirms that allowlist interpretation.
- Existing country-scoped postal include and exclude rules can map to `postal`
  selectors without discarding merchant intent.
- Implementations SHOULD keep order-first handling for options they cannot
  migrate or evaluate.

If this proposal is accepted, the normative specification should define
`destination_schema` and `destination` together and update kind `30406` examples.
It should not introduce destination tags piecemeal, because partial clients must
recognize when country metadata is insufficient for automatic checkout.

## References

- [ISO 3166 country and subdivision codes](https://www.iso.org/iso-3166-country-codes.html)
- [Universal Postal Union addressing work](https://www.upu.int/en/Universal-Postal-Union/Activities/Physical-Services/Addressing)
- [Open Location Code](https://github.com/google/open-location-code)
