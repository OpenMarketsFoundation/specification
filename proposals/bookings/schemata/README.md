# Bookings schemata

JSON Schema (draft-07, authored as YAML) for the Bookings proposal (`../../bookings.md`). Implementation reference; updated as the implementation teaches us.

## Layout

```text
kind-1331/envelope.schema.yaml   the kind:1331 rumor: kind, tags (p, conversation, a, type, version), no sig
content/terms.schema.yaml        shared definitions: time-based vs date-based terms, amount, balanceDue, reason, contact, option
content/<type>.schema.yaml       the JSON object carried in content, one per message type (nine)
tag/<name>.schema.yaml           openmarkets, capacity, available, tzid, accepts_bookings
```

## Validating a message

1. Unwrap the NIP-59 gift wrap and seal; check the seal's signer equals the rumor's `pubkey`.
2. Validate the rumor against `kind-1331/envelope.schema.yaml`.
3. Read the `type` tag, `JSON.parse` the `content`, and validate the object against `content/<type>.schema.yaml`.
4. Apply the rules the schemas cannot express:
   - each of `p`, `type`, `version` appears exactly once, and `conversation`, `a` at most once (a repeat makes the rumor invalid);
   - `start`, `end`, `earliestStart`, `latestStart` are real dates or date-times (a pattern passes `2026-02-30`);
   - `partySize` is required when the `a` tag names a calendar event;
   - `amount`, `deposit` and `balanceDue` in a `booking_modification_request` are valid only when the sender is the business;
   - every message of a booking uses the form (time-based or date-based) of its `booking_request`;
   - an unrecognized `reason` is read as `other`;
   - on public events, `available` MUST NOT exceed `capacity`.

A rumor that fails step 2, step 3, or one of these rules is **invalid**: ignore it, change no state, send no answer. A `booking_request` that is valid but whose terms cannot be honoured (`end` not after `start`, `latestStart` before `earliestStart`, unknown `tzid`, malformed `phone` or `email`, a `tel:`/`mailto:` prefix) is **declined** with `invalid_terms`. The capabilities parser returns these as `issues`.

**Readers are lenient, writers are strict.** The schemas describe what a reader accepts: unknown content fields pass (no `additionalProperties: false`), and extra elements after the value of a `p` or `a` tag (a NIP-01 relay hint, or anything else) are accepted and ignored. Writers emit the canonical form only: `["p", "<pubkey>"]` and `["a", "<coordinate>"]`, with no hint.

## Validating public tags

Each `tag/<name>.schema.yaml` validates one tag array. Cross-tag rules stay in the proposal text: `capacity` and `available` need the `openmarkets` bookings tag on the same event, which appears at most once; the recipient of bookings is always the event's author.
