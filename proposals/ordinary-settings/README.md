# Ordinary settings documents (experimental proposal)

Revision: OS-1, 2026-10-24. This is a new proposal, not an accepted allocation or
an amendment to the shipping proposal. It replaces neither wallet records nor
shipping options. Earlier proposal #18 is a separate, unimplemented design.

## Identity and transport

| Document | Experimental kind | Required `d` tag / JSON `format` | Content |
| --- | --- | --- | --- |
| PublicSettingsDocument | 10420 | `openmarkets.public-settings` | JSON |
| PrivateSettingsDocument | 10421 | `openmarkets.private-settings` | Self-encrypted JSON |

Both kinds are NIP-01 replaceable: one complete snapshot per author and kind.
The sole tag is `["d", "<format>"]`; it binds the document identifier but does
not create additional addresses. `version: 1` is the wire major. `settings` is
required, may be empty, and contains optional sections. `extensions` is optional.
No visibility field, section/role selector, ancestry/revision counter or generic
public/private publishing operation is defined. Public and private readers,
schemas and writers must be separate. Validate kind, exact tags, format, version,
size, signature and author before use. Validate private outer signatures before
asking the signer to decrypt. Verify the signer returned the exact requested
event. Private writers encrypt the entire document to the author's public key
through the connected signer using public NIP-44 v2, then sign. No plaintext
fallback, password envelope or account-key custody.

The numbers were checked against the NIPs kind table, the registry-of-kinds
schema and open proposals on 2026-10-24; no collision was found. This bounded
search is not a reservation or proof of global non-use. Allocation remains a
review question before interoperable deployment. NIP-78 is deliberately not the
interchange format. No upstream acceptance is claimed.

## Ownership

Private: display currency/Bitcoin units, language/locale, personal appearance,
saved shipping addresses/default address, notifications, working preferences
and preferred payment method. Public: storefront presentation, general merchant
location, hours, service languages and notices. An optional same-author 30406
coordinate selects an existing policy for new authoring only.

Wallet identity, complete encrypted recovery records, names, receiving addresses,
lifecycle and pay/receive selections remain wallet-owned. Shipping calculations,
destinations, origin-country inputs, rates, product references and order evidence
remain policy/product/order-owned. Settings never override these records and
never require listing republication. Existing Nostr standards retain profile,
relay, inbox, media-server and app-recommendation authority. Sessions, credentials,
browser permissions, analytics consent, drafts, carts and operational records
are outside these documents.

## Fields and defaults

The adjacent JSON schemas define field shapes and limits. Length limits count
Unicode code points. Currency is `BTC` or an uppercase ISO 4217 code; country is
an assigned uppercase ISO 3166-1 alpha-2 code. Language and locale use BCP-47.
Timezones use IANA names. Clients validate those registries, not only spelling.

- `display`: currency (default USD), bitcoinUnit (`bitcoin`/`sats`, default
  bitcoin), language and locale (default device). Prices retain their signed units.
- `appearance`: theme (`system`, `day-market`, `night-market`; default system),
  optional reducedMotion boolean. System resolves locally, never writes back.
- `shipping`: savedAddresses keyed by random UUID, defaultAddressId UUID or null.
  The pointer must resolve in the same map. Address-book and pointer edits are
  atomic. Postal completeness is checked again by checkout for the destination.
- `notifications`: optional orders/messages booleans (default true), optional
  quietHours with start/end local HH:MM and timezone. Equal endpoints disable
  quiet hours; end before start crosses midnight. No browser permission grants.
- `working`: optional weightUnit (`g` default, kg/lb/oz), orderSort
  (`newest` default or `oldest`). Display choices never rescale domain data.
- `payments.preferredMethod`: automatic (default), nwc, webln or manual. This
  suggests an interface only: no spending permission, wallet selection or payment.
- `storefront`: optional theme and layout (`grid` default or `list`); optional
  tokens `{accent: "#RRGGBB"}`. Declarative values only; no CSS, scripts or URLs.
- `merchant`: nullable generalLocation `{location, geohash?}`, businessHours,
  serviceLanguages (default empty), notice (nullable, default absent).
  General location is public display only. Business hours have timezone,
  weekly days `mon` through `sun` (missing means closed) with arrays of
  non-overlapping `{start,end}` intervals, end strictly after start; overnight
  opening splits at midnight using end `24:00`. Date exceptions are a map of
  YYYY-MM-DD to intervals, replacing that local day's weekly hours.
- Public `shipping.defaultPolicy`: null or `30406:<author>:<nonempty d>`.
  Validate same-author binding and resolve the actual policy before use.

## Evolution, bounds and egress

Documents are at most 32768 UTF-8 JSON bytes, at most 12 nested containers,
128 members per object, 128 items per array, 4096 code points per unknown string.
Private NIP-44 base64 content is at most 44000 ASCII characters; real signer and
relay limits may be smaller. Reject oversize drafts before signing; never truncate.
Reject non-JSON values, duplicate object keys and prototype-mutating keys.

Optional additive fields keep major 1. Preserve unknown bounded fields at every
nesting level and optional namespaced extensions in their original document.
Extensions map reverse-DNS names to `{version: positive integer, data: JSON}`;
at most 16 extensions, 4096 UTF-8 bytes of data each. They are optional, never
executed, and cannot reinterpret core fields or permissions. New required
semantics require a reviewed major revision. Newer unsupported majors and newer
invalid documents block downgrade writes, retaining prior usable display state.

Public authors can edit only explicit public schema fields. Opaque unknown
public fields may round-trip only from a validated public baseline; clients
must not accept arbitrary unknown input into public edits. Private discriminators,
private section names, address/contact fields and wallet/credential keys must
fail public validation, including inside extensions. Wallet recovery/authority
and authoritative shipping terms fail both ordinary-settings boundaries.
Arbitrary human-authored public text cannot be proven secret-free: show the
public scope when editing. No private-to-public copy/conversion helper.

## Ordering, edits and durability

Apply NIP-01 newest created_at, then lexicographically lowest event ID on ties,
independently for the two kinds. Serialize local writes per author/document
across tabs. Retain the actual editing baseline and explicit changes. Before
signing, perform a bounded read and reconcile retained signed evidence. Rebase
only disjoint edits onto newer observed state; overlapping changes retain the
draft and require review. Units are ordinary scalar fields, the complete address
book/default pointer, business-hours object, layout and individual extensions.
Preserve unknown nested fields from the newest baseline during known-field edits.

Stage exact signed bytes atomically before publication. Private persistent data
is ciphertext only. Keep bounded encrypted baseline/edit intent when restart
reconciliation is supported; if unavailable, stop a superseded candidate for
review rather than guessing its edits. Retry the same signed bytes only while
current; never bump timestamps to defeat a known successor. New explicit saves
advance beyond observed timestamps with a maximum 60-second future-clock bound.
Distinguish locally retained, relay acknowledged and exact-event readback states.
Empty, partial and unavailable reads do not erase stronger evidence, prove global
absence or authorize automatic blank writes. Explicit first saves may proceed
with disclosed bounded coverage. Storage failure must prevent publication.

Unseen concurrent/offline whole-document replacements can lose even disjoint
changes; removed addresses can reappear. Local stale checks cannot prevent that
race. Relays may discard losers permanently. No CRDT, per-field clocks, permanent
tombstones, history-event system or guaranteed lossless offline merge is proposed.

## Automatic experience and clean start

Approved sign-in starts bounded reads; reconnect/focus retries eligible work.
Signer refusal pauses background prompts. Account replacement clears decrypted
state and fences every asynchronous operation. Private drafts remain in memory
unless signer-encrypted; refusal can therefore leave a draft without restart
durability. Public browsing never decrypts private settings. Failures in settings
must not gate wallet restoration or any other domain coordinator. No manual sync
or per-document restore controls are required.

An ordinary-settings clean start may ignore old preferences without conversion,
legacy readers or dual writes. Old bytes can remain untouched. This never deletes,
migrates or reimports wallets, shipping policies or operational records.

## Conformance

Fixtures include supported older/minimal major-1 documents, nested unknown data,
wrong privacy discriminators, unsupported major and domain-authority injection.
Implementation evidence must additionally cover real signatures and NIP-44,
public egress, signer refusal, account replacement, stale edits, offline/restart,
atomic storage failure, bounded discovery and same-byte retry. Fixture tests do
not establish live signer/device/relay interoperability or funded payment safety.
Two independent implementations and actual signer/relay qualification are needed
before claiming interoperable deployment.

## Sources checked

- https://github.com/nostr-protocol/nips/blob/master/01.md
- https://github.com/nostr-protocol/nips/blob/master/44.md (public v2; future v3 remains source/capability-gated)
- https://github.com/nostr-protocol/nips/blob/master/78.md
- https://github.com/nostr-protocol/registry-of-kinds/blob/master/schema.yaml
- https://github.com/OpenMarketsFoundation/specification/blob/24313d75bb6ebf3ba37266a504980340308b4dc8/README.md
