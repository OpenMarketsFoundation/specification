# Portable Commerce Settings

Status: **experimental proposal**, not an adopted Open Markets standard.

This proposal gives an identity a portable private commerce view and a public
commerce view. It does not change [SPEC.md](../SPEC.md), existing merchant
payment preferences, or any current event kind. Requirements using MUST, SHOULD
and MAY apply only within this proposal. Numeric kind allocation and adoption
require protocol review before interoperable publication.

## Problem and intended result

Buyer and merchant clients currently keep preferences in application records,
local storage, profiles and domain-specific events. An application should not
need a new collection of discovery, encryption and precedence rules for every
settings screen. A user should be able to connect their Nostr signer and restore
supported private commerce preferences without another application password.

The proposed boundary is two logical views, not a new authority over everything
associated with an account:

```text
Buyer and merchant clients
  |-- Private commerce view --> account signer --> encrypted domain records
  |-- Public commerce view  --> verified public records and existing owners
  |                              |-- public merchant authoring defaults
  |                              |-- kind 0 merchant payment preferences
  |                              |-- NIP-89 application recommendations
  |                              `-- kind 30406 delivery options
  `-- Separate owners: wallet recovery, profile, network, appearance, orders
```

Public views can be read without connecting the owner's signer. Private reads
and all writes require the appropriate owner capability. A signer connection or
a signature alone is not decryption: NIP-44 is optional in NIP-07, and remote
signers can require separate permissions. Clients MUST distinguish unsupported,
denied, unavailable and successful operations; manual commerce remains usable.

## Ownership and visibility

| Setting | Canonical authority | Treatment |
| --- | --- | --- |
| Saved shopper contact and delivery address | Private shopper record | Self-encrypted; revealed to a seller only through the reviewed order flow |
| Shopper price-display currency, bitcoin unit and preferred payment interface | Private shopper record | Preferences, not payment authorization or wallet selection |
| Merchant authoring weight unit | Private merchant record | Private preference; canonical product weights remain unchanged |
| Merchant coarse shipping origin and reusable delivery defaults | Public merchant record | Explicit public authoring defaults; never an independent checkout quote |
| Merchant `payment_preference` | Existing kind `0` tag | Retain `manual`, `ecash`, `lud16` and existing default/handling rules |
| Application recommendations | Existing kinds `31989`/`31990` | Retain NIP-89 ownership |
| Actual delivery services, prices and eligibility | Existing kind `30406` and explicit supported extensions | Product/collection references and signed order terms remain authoritative |
| Public profile and receiving address | Existing profile owner | Do not duplicate into the settings record |
| Relays, inbox relays and media servers | Existing NIP-65/NIP-17/BUD-03 owners | Do not duplicate or override their authority |
| Theme/appearance | Separate general-purpose preference contract | No automatic public mirror of a private preference |
| Wallet secrets, primary wallet, credentials, payment recovery | Wallet protocol/provider owners | Never ordinary commerce settings |
| Cart, order, stock, drafts, publication recovery and device permission state | Their respective workflows | Operational state, not portable account preferences |

The public view MAY compose existing owners, but MUST preserve their source,
revision, freshness and authority. Updating a composed field invokes that
field's existing writer. It MUST NOT write a second authoritative copy into the
new public record. The same public key may be both buyer and merchant; roles do
not create different identities.

## Record addressing and allocation request

Recommend **two dedicated addressable event kinds**, one public and one
self-encrypted. The symbols below are protocol-design names, not wire values:

| Symbol | Address `(kind, author, d)` | Content |
| --- | --- | --- |
| `PUBLIC_COMMERCE_SETTINGS` | `(allocated public kind, owner, "merchant")` | Public JSON envelope |
| `PRIVATE_COMMERCE_SETTINGS` | `(allocated private kind, owner, "shopper")` | NIP-44 ciphertext containing a shopper JSON envelope |
| `PRIVATE_COMMERCE_SETTINGS` | `(allocated private kind, owner, "merchant")` | NIP-44 ciphertext containing a merchant JSON envelope |

The two kind numbers must be assigned through review in the NIP-01 addressable
range before interoperable deployment. This document does not reserve numbers.
Clients MUST NOT put these symbols in a Nostr event or repurpose an allocated
kind. Existing application-specific experiments can continue at their existing
addresses while the allocation and migration contract are reviewed.

NIP-78 explicitly says its kinds are not a generic interchange format for public
or cross-application data. We therefore do not propose making kind `30078` the
Open Markets interoperability standard. Its existing application records remain
compatibility inputs, not a permanent parallel standard.

Each event has exactly one two-element `d` tag using the value in the table.
Private records MUST NOT contain contact, address, payment preference, wallet
identifiers, revision ancestry or other private fields in public tags. Clients
MUST NOT add a recipient `p` tag: the recipient is the event's own author.
Private writers SHOULD use only the `d` tag; any additional tag needs explicit
privacy review. Signatures, author, kind, `d`, timestamps and ciphertext length
remain visible to any party able to read the event.

Separate private shopper and merchant addresses avoid rewriting one domain to
save another and allow clients to request only the needed plaintext. Neither
record embeds appearance or wallet recovery. This limits update coupling; it
does not create cryptographic field-level permissions within the same identity.

## Envelope and bounds

Public `content` is UTF-8 JSON. Private `content` is the NIP-44 v2 payload string
obtained by encrypting UTF-8 JSON to the author's own public key. Do not add a
second password, derive a key from a public signature, or implement new crypto.
Future encryption versions require explicit capability and protocol review;
unknown versions are unsupported, not a reason to fall back to plaintext.

Every plaintext envelope has these fields:

| Field | Required value / meaning |
| --- | --- |
| `schema` | `"org.openmarkets.commerce-settings"` |
| `version` | Integer `1` for this proposal |
| `owner` | Event author, 64 lowercase hexadecimal characters |
| `visibility` | `"public"` or `"private"`, matching the allocated kind |
| `section` | `"shopper"` or `"merchant"`, matching the exact `d` tag; public shopper records are not defined |
| `previous` | Prior observed event ID at the same address, or `null` for an initial record |
| `data` | Object containing the fields for that section; `{}` explicitly clears the section |

`previous` is an ancestry hint for detecting observed concurrent edits, not a
compare-and-swap condition enforced by a relay. An unavailable predecessor is
not proof of corruption. When a predecessor is available, its author/address
must match; a reference to another address cannot establish revision authority.

All envelope fields are required. JSON duplicate keys, malformed UTF-8,
non-finite numbers and nesting deeper than 12 are invalid. A plaintext envelope
MUST be at most 16,384 UTF-8 bytes; private ciphertext MUST be at most 32,768
ASCII bytes before decryption. These are this proposal's resource limits, not
claims about NIP-44's maximum supported message size. Strings below are bounded
in Unicode code points after decoding; the overall byte limit also applies.

Readers validate the signed outer event, exact address, limits, encryption
version and decrypted envelope binding before exposing settings. A valid
signature proves authorship of those bytes, not global freshness or delivery.
Do not decrypt arbitrary relay records while searching for a supported address.

### Private shopper data

All members are optional and independently editable. Saving display or payment
preferences MUST NOT require a delivery address. An omitted member means no
saved value in this record; it does not import a stale local preference.

| Member | Shape and semantics |
| --- | --- |
| `contact` | Object with optional `email` (320 characters) and `phone` (80); no tracking identifiers |
| `delivery_address` | Object with `recipient_name` (100), `line1` (200), `country` (uppercase ISO 3166-1 alpha-2); optional `line2` (200), `city` (100), `region` (100), `postal_code` (32) |
| `display` | Object with optional `currency` (`BTC` or uppercase ISO 4217 code) and `bitcoin_unit` (`btc` or `sat`) |
| `payment` | Object with optional `preferred_interface`: `automatic`, `manual`, `nip47`, or `webln` |

Required address strings are nonempty. Country-specific checkout must request
the additional fields needed by the selected delivery option; this storage
schema does not impose a universal postal-address form. A stored address is a
reusable input, not proof of deliverability or checkout completeness.
Omitting the whole address is valid. Optional strings are nonempty when present.

`automatic` expresses no preferred interface. A payment interface preference is
not a payment medium, an instruction to pay, a spending permission, or a stable
wallet reference. A client unable to support a preference keeps it intact and
offers supported choices; it MUST NOT silently authorize a substitute payment.
Price-display choices never change the signed denomination of an offer.

### Private merchant data

`authoring` is an optional object containing `weight_unit`: `g`, `kg`, `lb`, or
`oz`. This controls entry/display only. The unit or its absence MUST NOT rescale
an existing product or shipping table. More merchant preferences require a
documented extension or new schema version, not arbitrary secret storage.

### Public merchant data

`delivery_defaults` is an optional object with these optional members:

- `ships_from`: `{ "label": string, "geohash": string }`. Label is 1–240
  characters; geohash is exactly four characters from the geohash alphabet
  `0123456789bcdefghjkmnpqrstuvwxyz`. This is an explicitly public coarse area,
  never a private return address or buyer destination.
- `shipping_options`: at most 32 distinct kind-30406 coordinates authored by
  the same merchant, with nonempty `d` values and a maximum of 512 characters
  per coordinate. They are authoring suggestions. Clients independently fetch
  and validate the referenced options. Omission/empty does not delete options.
- `destination_template`: an optional object with `tags`, at most 128 tag
  arrays, each at most 6 strings of at most 128 characters. It carries only a
  complete `country` summary, `destination_schema` marker and `destination`
  selectors from the existing [destination-constraints proposal (#13)](https://github.com/OpenMarketsFoundation/specification/pull/13).
  Their spelling, normalization and eligibility grammar are defined there,
  not redefined here. There must be exactly one `country` and one
  `destination_schema` tag. Unknown schema/selectors make the template
  unsupported and prevent its application; they do not make the rest of this
  record authoritative for eligibility. Adoption of this optional member is
  conditional on agreement on that proposal's grammar.

These are reusable inputs when authoring an offer. A client MUST show the
resulting delivery terms before publishing that offer. A product's actual
shipping references, delivery option, negotiated order and payment contract
outrank defaults. Changing defaults MUST NOT rewrite existing products, alter
existing orders or make an unsupported destination eligible for payment.

The public record intentionally contains neither `payment_preference` nor a
copy of `lud16`, NIP-89 recommendations or shipping price tables. Their existing
owners are exposed through the public view. A clearing record clears only these
new defaults, not a merchant's kind-0 profile or kind-30406 offers.

### Unknown fields and evolution

Unknown versions and required values are unsupported. Readers MAY display
understood optional fields of version 1 but MUST NOT apply unknown semantics.
Writers MUST preserve uninterpreted JSON members and any known but locally
unsupported values when editing another field. If they cannot do so within the
bounds, the record is read-only until a compatible client is used. Do not turn
an unsupported record into an empty record or strip unknown private fields.

A version-1 writer modifies only fields it understands. Extensions MUST NOT
reuse defined names with different meanings. New required semantics require a
new version; this proposal does not allocate an arbitrary vendor-key namespace.
An explicit user request to clear the entire section may replace `data` with
`{}` after explaining that unsupported fields in that section are also cleared.

## Discovery, editing and recovery

1. Resolve the owner to its hexadecimal public key and capture the active
   account/session revision. `npub` is a presentation encoding of that identity.
2. Query the exact supported address on the user's applicable relay plan.
   Private clients SHOULD use owner-selected storage relays and support NIP-42
   AUTH where required. Public merchant discovery must not require the merchant
   to authenticate on behalf of a buyer. No new relay-list record is introduced.
3. Validate candidates and apply NIP-01 addressable ordering: newest
   `created_at`, then lowest event ID lexicographically on a timestamp tie.
   Preserve stronger known signed evidence when a partial read omits it. A
   newer unsupported, undecryptable or malformed candidate must be surfaced;
   it MUST NOT authorize silently overwriting it with an older supported value.
4. Decrypt only the selected supported private records with the connected
   owner's signer. Check the session again after every awaited operation.
   Account switch, disconnect, cancellation or a superseded local edit prevents
   stale results from changing the active view or entering its publication queue.
5. Preserve the base revision and user's unsaved field edits. Re-read before
   saving. If the observed head changed, preserve unrelated changes and use a
   three-way comparison of base/current/edit. Merge only edits proven disjoint;
   same-field differences or missing base evidence require review. Never choose
   a winner by an untrusted wall-clock value inside the plaintext.
6. Set `previous` to the observed head being extended. Choose `created_at`
   greater than the observed head for a new revision, within the client's
   disclosed clock-skew policy. Surface clock skew instead of repeatedly
   publishing far-future events. Encrypt with a fresh NIP-44 nonce through the
   signer, sign once, validate the returned bytes/address, and durably stage
   those signed bytes before network delivery. Persist no private plaintext.
7. Retry the exact staged event. Keep ACK, rejection, timeout and read-back
   distinct. If a newer head is known, stop blind repair of superseded bytes
   and reconcile; transport success alone is not cross-device restoration.

Relays do not provide atomic compare-and-swap across devices and may discard
older addressable events. The ancestry hint and read-before-write procedure
detect only conflicts actually observed. They cannot guarantee recovery of an
unseen losing edit. Clients SHOULD retain bounded encrypted evidence for known
conflicts, never silently claim lossless multi-device merging, and offer an
explicit repair path. No global history service or new CRDT is required here.

A view exposes usable data separately from evidence: current/retained revision,
source coverage, pending delivery and conflict/capability errors. Empty complete
bounded discovery, partial discovery and unavailable sources are different;
none proves global absence. Unsaved local edits are not silently overwritten by
restoration. Guest/manual entry remains available without private sync.

Disconnect and account switch MUST remove decrypted snapshots from active
consumers and invalidate outstanding work. Cache keys and durable queues are
owner-scoped; resuming an old account's pending work requires that account's
current authority. A decrypted draft must not remain visible to a new account.

Clearing publishes a newer, correctly bound record with `data: {}` (encrypted
for private records). Clients must not resurrect older data from caches after
observing that revision. NIP-09 requests may supplement cleanup, but neither
replacement nor deletion guarantees erasure from relays, old devices or backups.

## Privacy and signer trust

NIP-44 self-encryption is not forward-secret. Compromise of the identity key can
expose historical ciphertext. The selected signer handles plaintext during
encryption/decryption, and the active client session can access restored data.
Owner-only relay access is an additional transport policy, not a substitute for
encryption. Metadata remains linkable to the owner.

Private plaintext MUST NOT enter public tags, persistent browser storage,
analytics, logs, support exports or public feed/index projections. Encrypted
signed records can be cached for recovery. A private setting MUST NOT become
public through a mirror, migration or schema default. Sharing contact/address
data with a seller requires the normal reviewed order flow; it never involves
giving the seller access to the self-encrypted settings record.

Signer capability probes must use disposable non-sensitive material. Implementers
must test actual encrypt/decrypt/sign operations, not infer support from method
names alone. NIP-07 and NIP-46 behavior, denial, locked signers and account switch
need independent device evidence. This proposal does not permit account-key
custody, move wallet secrets into preferences, or weaken wallet recovery gates.

## Migration and implementation status

The [Conduit mapping and examples](../examples/commerce-settings.md) distinguish
inspected implementation from this proposal. Conduit already uses signer-based
wallet encryption; its shopper preferences at the inspected main still use a
separate password format. This document does not claim portable commerce
settings have shipped or that wallet recovery proves settings interoperability.

Implementation can first consolidate existing application formats behind shared
owners and delete competing callers. Interoperable wire adoption is a later
explicit step after kind allocation and contract review. An adopting client
must inventory old readers/writers and account for existing data before removal.
Never silently publish previously private fields or perform lossy conversion of
delivery restrictions. A client that cannot migrate safely retains a named,
bounded compatibility reader and makes the required owner review explicit.

After a new canonical record is observed and migration accepted, old formats
must not silently regain precedence if the new record is temporarily unavailable
or cleared. Do not dual-write forever. Define the compatibility reader's removal
condition and preserve known stronger evidence through outages. Old clients can
continue their existing format, but their writes are not automatically merged
into the new one. Cross-format change detection and user review are necessary
where such clients remain in use.

## Review and acceptance

Review is requested on: (1) allocating two dedicated addressable kinds;
(2) the private shopper/merchant section split and initial fields; (3) retaining
kind-0/NIP-89/30406 authority; and (4) the optional destination-template reuse
of #13. These are explicit proposal decisions, not assertions of upstream
agreement. The recommended design above is concrete enough to review without
requiring clients to deploy an unallocated kind.

Before claiming interoperability, two independent implementations must show:

- signed public discovery and editing without changing existing owner semantics;
- real-signer self-encryption and restoration on another device/origin;
- optional display/payment-only records, supported and denied capabilities;
- account-switch/stale-result fencing, reload and exact-byte retry;
- observed concurrent-edit handling and truthful partial/unavailable states;
- non-destructive editing of unknown fields and refusal of unknown versions;
- clearing without stale-data resurrection or claims of historical erasure;
- no private fields in public events, durable plaintext, logs or telemetry;
- an explicit compatibility cutover and removal of competing writers.

Documentation checks and synthetic examples establish internal consistency,
not cryptographic, device, relay or production conformance.

## References

- [NIP-01: signed events and addressable replacement](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [NIP-07: optional signer encryption capabilities](https://github.com/nostr-protocol/nips/blob/master/07.md)
- [NIP-09: event deletion requests](https://github.com/nostr-protocol/nips/blob/master/09.md)
- [NIP-42: relay authentication](https://github.com/nostr-protocol/nips/blob/master/42.md)
- [NIP-44: versioned encryption](https://github.com/nostr-protocol/nips/blob/master/44.md)
- [NIP-46: remote signing and encryption permissions](https://github.com/nostr-protocol/nips/blob/master/46.md)
- [NIP-78: application data and the interoperability boundary](https://github.com/nostr-protocol/nips/blob/master/78.md)
- [Current Open Markets merchant preferences](../SPEC.md#merchant-preferences)
- [Destination-constraints proposal](https://github.com/OpenMarketsFoundation/specification/pull/13)
