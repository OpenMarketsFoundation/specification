# Commerce Settings Examples and Conduit Mapping

Status: **experimental, explanatory** companion to the
[portable commerce settings proposal](../proposals/commerce-settings.md).
These examples are synthetic plaintext envelopes, not signed Nostr events,
cryptographic test vectors or proof of implemented interoperability. In private
events the entire envelope is encrypted; it is never the public event content.
The repeated hexadecimal owner is a placeholder, not a user identifier.

## Private shopper record

Proposed address: `(PRIVATE_COMMERCE_SETTINGS, owner, "shopper")`, after numeric
kind allocation. Contact, delivery and preference sections are independent.

```json
{
  "schema": "org.openmarkets.commerce-settings",
  "version": 1,
  "owner": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "visibility": "private",
  "section": "shopper",
  "previous": null,
  "data": {
    "contact": {
      "email": "shopper@example.invalid"
    },
    "delivery_address": {
      "recipient_name": "Example Shopper",
      "line1": "123 Example Street",
      "city": "Example City",
      "region": "CA",
      "postal_code": "90001",
      "country": "US"
    },
    "display": {
      "currency": "USD",
      "bitcoin_unit": "sat"
    },
    "payment": {
      "preferred_interface": "nip47"
    }
  }
}
```

The following is also valid: a user saves their price display before providing
any contact or shipping information. No delivery address is inferred.

```json
{
  "schema": "org.openmarkets.commerce-settings",
  "version": 1,
  "owner": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "visibility": "private",
  "section": "shopper",
  "previous": null,
  "data": {
    "display": {
      "currency": "BTC",
      "bitcoin_unit": "sat"
    }
  }
}
```

## Private merchant record

The preferred entry unit does not change stored product weights or prices.

```json
{
  "schema": "org.openmarkets.commerce-settings",
  "version": 1,
  "owner": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "visibility": "private",
  "section": "merchant",
  "previous": null,
  "data": {
    "authoring": {
      "weight_unit": "kg"
    }
  }
}
```

## Public merchant record

Proposed address: `(PUBLIC_COMMERCE_SETTINGS, owner, "merchant")`, after numeric
kind allocation. This is a public authoring template, not checkout eligibility.
The optional destination template reuses the grammar proposed in #13; it cannot
be applied without supporting and agreeing on that grammar.

```json
{
  "schema": "org.openmarkets.commerce-settings",
  "version": 1,
  "owner": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "visibility": "public",
  "section": "merchant",
  "previous": null,
  "data": {
    "delivery_defaults": {
      "ships_from": {
        "label": "Example shipping area",
        "geohash": "9q8y"
      },
      "shipping_options": [
        "30406:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:standard"
      ],
      "destination_template": {
        "tags": [
          ["country", "US"],
          ["destination_schema", "1"],
          ["destination", "include", "country", "US"],
          ["destination", "exclude", "postal", "US", "prefix", "967"]
        ]
      }
    }
  }
}
```

A client also reads the merchant's kind-0 `payment_preference` and the existing
NIP-89 recommendations through their canonical owners. Those values are not
copied into this document. The shipping option must be independently validated;
its presence here does not prove that a particular product accepts it.

## Clearing a section

This example clears a previously observed private shopper record. The event ID
is synthetic. The outer signed replacement must have a newer revision at the
same address. Private `previous` and `data` remain inside the ciphertext.

```json
{
  "schema": "org.openmarkets.commerce-settings",
  "version": 1,
  "owner": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "visibility": "private",
  "section": "shopper",
  "previous": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "data": {}
}
```

Clearing this section does not clear merchant preferences, wallet recovery,
profile or network records. It cannot guarantee erasure of historical copies.

## Inspected Conduit implementation and proposed migration

Baseline: [Conduit main `9431a2a`](https://github.com/Conduit-BTC/conduit-mono/commit/9431a2abea1d43eccd8d69e683e860a67d20dc13),
inspected 12 October 2026. This is a source snapshot, not device or production
acceptance. It deliberately excludes unmerged and local work.

| Current field / responsibility | Current owner and storage | Proposed treatment |
| --- | --- | --- |
| Shopper recipient, address lines, city, state/region, postal code, country, email, phone | [shopper-presets.ts][presets], password-encrypted kind `30078`, `d=conduit/shopper-presets` | Shared private shopper owner; map contact separately from address, preserve values; use signer self-encryption on the selected application/adopted contract |
| Shopper `preferredRail` (`automatic`, `manual`, `nwc`, `webln`) | Same preset document | Private `preferred_interface`; map `nwc` to `nip47`; no wallet credential or payment authorization |
| Shopper `display.currency`, `display.bitcoinUnit` | Preset plus [useShopperPricePreference][price] account-local override, which currently takes precedence | Private display fields; map `BITCOIN` to `BTC`, `bitcoin`/`sats` to `btc`/`sat`; remove stale override precedence after explicit reconciliation |
| Preset `enabled`, password and unlock policy | [shopper-presets store][preset-store] and provider; remembered password may be in local/session storage | Remove password/remember lifecycle when its callers migrate; clearing becomes empty encrypted replacement; do not convert unlock policy into a portable preference |
| Merchant `countries[].code/name/restrictTo/exclude`, `shipsFrom.location/geohash` | [merchant-shipping-settings.ts][shipping-settings], signed public kind `30078`, `d=conduit/merchant-shipping-settings` | Public merchant defaults; country display names remain presentation data; do not silently drop or reinterpret postal restrictions |
| Merchant local shipping copy and fallback | [readiness.ts][readiness], account-local `shipping_config`; Shipping route also hydrates from older kind-30406 options | One public owner decides current/legacy precedence; remove app-local fallback and authoritative local-copy logic after migration |
| Merchant weight unit (`g`, `kg`, `lb`, `oz`) | [shippingWeightUnits.ts][weight], per-account local storage; used by product measurements and policy editor | Private merchant authoring preference; remove competing storage ownership after restoration works |
| Shipping-policy title, origin, currency, domestic/international tables, postal/subdivision rules, bands and thresholds | [shipping-policy.ts][shipping-policy], kind `30406`, `d=conduit-shipping-policy`, explicit Conduit extension | Retain delivery owner and versioned extension. Expose through a shared public projection as needed; do not copy price tables into settings or call the extension already standardized |
| Product-scoped fixed delivery option, service, price and countries | [shipping.ts][shipping], kind `30406` referenced by product | Retain explicit delivery authority; account defaults cannot override it |
| Profile name/display name/about/picture/banner/NIP-05/website/receiving address | [profiles.ts][profiles], kind `0`, shared profile hooks used by both apps | Retain canonical profile writer and preservation of unrelated fields; expose only needed commerce projections |
| Open Markets merchant `payment_preference` | Defined by current Open Markets; no matching named parser/writer was found in this source baseline | Preserve the standard's kind-0 authority. Do not describe it as an already implemented Conduit settings feature; assess missing support separately from moving existing callers |
| General/inbox relay lists and per-device source eligibility | [network-preferences.ts][network], signed kinds `10002`/`10050` plus local operational state | Retain existing network owner, not commerce records |
| Ordered Blossom servers | [media-server-preferences.ts][media], kind `10063` plus cache/pending state | Retain BUD-03 owner, not commerce records |
| Theme (`system`, named light/dark themes) | [shared theme runtime][theme], device-local preference | Separate general-purpose preference/appearance contract; no public mirror |
| Signer connection, active account and session restoration | [auth-session.ts][auth], local connection/session state | Retain auth ownership and signer permissions; never sync connection secrets as commerce preferences |
| Wallet registry/default intents, recovery/primary pointers and NWC credentials | [wallet storage][wallet-storage], [signer recovery][wallet-recovery], wallet kind-30078 addresses; Merchant has a legacy NWC retirement path | Retain wallet ownership and separate recovery guarantees; generic settings may reuse primitives, never these secrets or device wallet IDs |
| Cart, drafts, stock decisions, payment/order sessions, delivery queues and caches | Workflow-specific persistence | Retain operational ownership. They are not saved account settings and do not migrate into the private record |

The shopper provider currently serves Preferences, Checkout, Cart, browse
location and merchant-checkout capability; display preference feeds price
rendering across product, cart, order, message and event surfaces. Merchant
Shipping and Products read the shipping settings; readiness has a separate
local/fallback path. Weight preferences have two direct editor callers. These
paths must migrate together with their shared owner, rather than adding a new
record while leaving the old route-level lookup rules active.

Current postal rules use exact matching or a trailing `**` prefix and strip
whitespace; #13's normalization also removes hyphens. Migration is not a blind
string rename. Preserve the current format behind its adapter until the owner
reviews equivalent destination behavior, or publish an explicitly reviewed new
template. Never broaden checkout eligibility during conversion.

The Conduit-only cleanup can keep approved application addresses while review
continues. This mapping is not a request for other clients to adopt a Conduit
namespace or a claim that the new dedicated kinds exist. Independent clients
must agree on the public proposal and numeric allocations before interoperable
wire adoption. Appearance, wallet recovery and delivery-pricing changes remain
separate concerns.

## Conformance scenarios for implementers

| Scenario | Required observation |
| --- | --- |
| Display-only record | Restores without requiring shipping or contact |
| Wrong author/address/domain binding | Rejected before application; no cross-account decryption/application |
| Sign-only extension or denied decryption | Recoverable capability state; no password/weak-encryption fallback |
| Account changes during signer prompt | Response cannot hydrate or stage a write for the new account |
| One relay unavailable, older data returned elsewhere | Retain stronger known revision and report partial coverage |
| Newer unsupported version | Surface unsupported state; do not overwrite it with the older supported record |
| Concurrent edits to same field | Observed conflict requires review; do not claim unseen edits can always be recovered |
| Retry after reload | Publish identical staged bytes; distinguish ACK from read-back and restoration |
| Unknown field while editing display | Preserve it or make the record read-only; never silently strip it |
| Private clear followed by an older cached record | Remain cleared after seeing the newer empty replacement |
| Public defaults changed | Existing product/order/payment terms remain unchanged |
| Destination template unsupported | No application to a new offer or inference of checkout eligibility |

[presets]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/protocol/shopper-presets.ts
[price]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/apps/market/src/hooks/useShopperPricePreference.ts
[preset-store]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/apps/market/src/lib/shopper-presets-store.ts
[shipping-settings]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/protocol/merchant-shipping-settings.ts
[readiness]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/apps/merchant/src/lib/readiness.ts
[weight]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/apps/merchant/src/lib/shippingWeightUnits.ts
[shipping-policy]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/protocol/shipping-policy.ts
[shipping]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/protocol/shipping.ts
[profiles]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/protocol/profiles.ts
[network]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/protocol/network-preferences.ts
[media]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/protocol/media-server-preferences.ts
[theme]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/ui/src/theme/runtime.ts
[auth]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/protocol/auth-session.ts
[wallet-storage]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/wallets/wallet-storage.ts
[wallet-recovery]: https://github.com/Conduit-BTC/conduit-mono/blob/9431a2abea1d43eccd8d69e683e860a67d20dc13/packages/core/src/wallets/signer-spark-recovery.ts
