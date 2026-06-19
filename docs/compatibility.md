# Compatibility

Status: explanatory guardrail for current normative material.

The current protocol behavior is preserved by [../SPEC.md](../SPEC.md). Split pillar and lane files are navigation/transposition views over the same current material.

## Compatibility Promise

Existing applications should be able to keep using the current specification without modification.

This structural refactor must not change:

- event kind numbers
- tag names
- tag array shapes
- field names
- JSON examples
- required/optional semantics
- order of tags shown in examples where implementers may have copied them
- status values
- `type` values
- payment preference values
- payment proof shapes
- merchant preference behavior
- NIP-17 order communication assumptions
- NIP-99 listing compatibility
- MUST, SHOULD, and MAY requirements

## Current Normative Inventory

Event kinds and kind references currently present:

- `30402`: Product Listing
- `30405`: Product Collection
- `30406`: Shipping Option
- `14`: Regular communication between parties
- `16`: Order processing and status
- `17`: Payment receipts and verification
- `31555`: Product Reviews
- `31989`: Merchant application recommendation
- `31990`: Recommended application event
- kind `0`: merchant profile payment preferences
- kind `10019`: preferred mint reference

Implementation-sensitive tag and field names include:

- `d`
- `title`
- `price`
- `type`
- `visibility`
- `stock`
- `summary`
- `spec`
- `image`
- `weight`
- `dim`
- `location`
- `g`
- `t`
- `a`
- `shipping_option`
- `p`
- `subject`
- `order`
- `amount`
- `item`
- `shipping`
- `address`
- `email`
- `phone`
- `payment`
- `expiration`
- `status`
- `tracking`
- `carrier`
- `eta`
- `rating`
- `payment_preference`

## Compatibility Checks For PRs

Before merging structural changes:

1. Compare [../SPEC.md](../SPEC.md) with the pre-refactor README snapshot.
2. Inventory all kind numbers before and after.
3. Inventory all tag names before and after.
4. Inventory all MUST, SHOULD, and MAY statements before and after.
5. Compare JSON examples against [../SPEC.md](../SPEC.md).
6. Confirm external links are exact.
7. Confirm escrow/proposal material is not presented as current normative behavior.

## Known Issues Not Fixed By This Refactor

The inherited text has issues that may deserve later cleanup, but this refactor intentionally does not fix them:

- relative NIP links such as `17.md`, `51.md`, `89.md`, and `10.md`
- duplicated note numbering
- minor grammar and spelling issues
- history mentioning `expires` while current text uses `expiration`
- lack of separate contribution and proposal workflow before this PR
