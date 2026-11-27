<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/open-markets-horizontal-dark.png">
    <img src="assets/open-markets-horizontal.png" width="460" alt="Open Markets Foundation">
  </picture>
</p>

<h1 align="center">Marketplace Protocol</h1>

<p align="center">A Nostr specification for product listings, orders, payments, and shipping.</p>

<br>

## Table of Contents
1. Protocol Requirements
2. Core Protocol Components
3. Events and Kinds
4. Order Communication Flow and Payment Processing
5. Product Reviews
6. Implementation Guidelines

<br>

## 1. Protocol Requirements

The protocol defines both required core components and optional features to support diverse marketplace needs.

### Required Components
Implementations MUST support the following core features:

- Product listing events (Kind: 30402)
- Product collection events (Kind: 30405) for product-to-collection references
- Merchant's preferences
- Order communication and processing via [NIP-17](17.md) encrypted messages

### Optional Components
These features MAY be implemented based on specific marketplace needs:

- Extended product metadata
- Shipping options (Kind: 30406)
- Product collections (Kind: 30405) 
- Drafts following [NIP-37](37.md)
- Product reviews (Kind: 31555)
- Service assisted order and payment processing

#### Watch-only clients
Watch-only clients are applications that allow users to display products without implementing full e-commerce capabilities. These clients don't need to support all required components - product rendering alone can be sufficient. However, ideally, they should also handle logic for looking up collections, reviews, and shipping options. Support for order communication using [NIP-17](17.md) is optional.

<br>

## 2. Core Protocol Components

### Core Flows
1. Merchant Preferences
   - Application preferences via [NIP-89](89.md)
   - Payment method preferences via kind `0` tags

2. Order Processing
   - Encrypted buyer-seller communication
   - Status updates and confirmations
   
3. Shipping
   - Option definition and pricing
   - Geographic restrictions
   
4. Payment
   - Multiple payment methods
   - Verification and receipts

Standard e-commerce flow:
1. Product discovery
2. Cart addition
3. Merchant preference verification
4. Shipping calculation
5. Payment processing
6. Order confirmation
7. Encrypted message follow-up

### Merchant Preferences
Merchants MAY specify preferences for how they want users to interact with them, including which applications to use and payment methods to accept. These preferences ensure a consistent experience and streamline operations. Merchants indicate their preferences through two mechanisms:

1. Application Preferences ([NIP-89](89.md)):
- The recommended application MUST publish a kind `31990` event
- The merchant MUST publish a kind `31989` event recommending that application

2. Payment Preferences:
- Set via `payment_preference` tag in the merchant's kind `0` event
- Valid values: `manual | ecash | lud16` 
- Defaults to `manual` if not specified

Applications implementing this NIP MUST handle preferences as follows:

1. When `payment_preference` is `manual`:
- If merchant recommends an app: MUST direct users to that app
- If no app recommendation: Use traditional interactive flow (buyer places order and waits for merchant's payment request)

2. When `payment_preference` is `ecash` or `lud16`:
- If merchant recommends an app: SHOULD direct users there first, but they MAY also offer to continue if compatible with the payment preference
- If no recommendations: Use specified payment method directly

3. When no preferences are set:
- Use traditional interactive flow
   - Buyer sends order
   - Wait for merchant's payment request

Buyers can verify merchant preferences by:
- Checking kind `31990` events for recommended applications
- Checking kind `0` events for payment preferences

This verification helps buyers follow merchant-approved paths and avoid potential scams or poor experiences.

<br>

## 3. Events and Kinds

### Product Listing (Kind: 30402)

Products are the core element in a marketplace. Each product listing MUST contain basic metadata and MAY contain additional details. Their configuration is the source of truth, overriding other possible configurations of other market elements such as collections, no configuration is cascaded to products, they MUST explicitly reference an attribute to inherit it.

**Content**: Product description, markdown is allowed
**Required tags**:
- `d`: Unique product identifier for referencing the listing
- `title`: Product name/title for display
- `price`: Price information array `[<amount>, <currency>, <optional frequency>]`
  - amount: Decimal number (e.g., "10.99")
  - currency: ISO 4217 code (e.g., "USD", "EUR")
  - frequency: Optional subscription interval using ISO 8601 duration units (e.g. 'D' for daily, 'W' for weekly, 'Y' for yearly).

**Optional tags**:
- Product Details:
  - `type`: Product classification `[<type>, <format>]`
    - type: "simple", "variable", or "variation"
    - format: "digital" or "physical"
    - Default/if not present: type: "simple", format: "digital"
  - `visibility`: Display status ("hidden", "on-sale", "pre-order"). Default/if not present: "on-sale"
  - `stock`: Available quantity as integer
  - `summary`: Short product description
  - `spec`: Product specifications `[<key>, <value>]`, can appear multiple times

- Media:
  - `image`: Product images `[<url>, <dimensions>, <sorting-order>]`, MAY appear multiple times
    - url: Direct image URL
    - dimensions: Optional, in pixels, "<width>x<height>" format, if not present the place in the array should be respected by using an empty string `""`
    - sorting order: Optional integer for order sorting. Values are sorted from lowest to highest, independent of starting value (not restricted to start with 0 or 1)

- Physical Properties:
  - `weight`: Product weight `[<value>, <unit>]` using ISO 80000-1
  - `dim`: Dimensions `[<l>x<w>x<h>, <unit>]` using ISO 80000-1

- Location:
  - `location`: Human-readable location string or collection coordinates
  - `g`: Geohash for precise location lookup or collection coordinates

- Organization:
  - `t`: Product categories/tags, MAY appear multiple times
  - `a`: Product reference "30402:<pubkey>:<d-tag>", MUST appear only once to reference parent products in a variable/variation configuration
  - `a`: Collection reference "30405:<pubkey>:<d-tag>", MAY appear multiple times
  - `shipping_option`: Shipping options, MAY appear multiple times
    - Format: "30406:<pubkey>:<d-tag>" for direct options
    - Format: "30405:<pubkey>:<d-tag>" for collection shipping
    - `extra-cost`: Optional third element in the array, to add extra cost (in the product's currency) for the shipping method. In case of reference a collection the extra cost should be applied to all shipping options from the collection.

```jsonc
{
  "kind": 30402,
  "created_at": <unix timestamp>,
  "content": "<product description in markdown>",
  "tags": [
    // Required tags
    ["d", "<product identifier>"],
    ["title", "<product title>"],
    ["price", "<amount>", "<currency>", "<optional frequency>"],

    // Product details
    ["type", "<simple|variable|variation>", "<digital|physical>"],  // Defaults: simple, digital
    ["visibility", "<hidden|on-sale|pre-order>"],  // Default: on-sale
    ["stock", "<integer>"],  // Available quantity
    ["summary", "<short description>"],
    
    // Media and specs
    ["image", "<url>", "<dimensions>", "<sorting-order>"],
    ["spec", "<key>", "<value>"],  // Product specifications (e.g., "screen-size", "21 inch"). MAY appear multiple times
    
    // Physical properties (for shipping)
    ["weight", "<value>", "<unit>"],  // ISO 80000-1 units (g, kg, etc)
    ["dim", "<l>x<w>x<h>", "<unit>"], // ISO 80000-1 units (mm, cm, m)
    
    // Location
    ["location", "<address string>"],
    ["g", "<geohash>"],
    
    // Classifications
    ["t", "<category>"],
    
    // References
    ["shipping_option", "<30406|30405>:<pubkey>:<d-tag>", "<extra-cost>"],  // Shipping options or collection, MAY appear multiple times
    ["a", "30405:<pubkey>:<d-tag>"]  // Product collection
  ]
}
```

#### Notes
1. Product Configuration:
   - Products can be simple, variable (with options), or variations of variable products
   - Digital products skip shipping requirements
   - Visibility controls product display status

2. Variable products: 
   - The parent or "root" product should use `variable` as value for `type`
   - The variations of the parent product should use `variation` as value for `type`. 
   - Variations MUST include an `a` tag pointing to the `variable` parent product.
 
2. Shipping Rules:
   - Shipping options can be defined directly by pointing to a shipping event, or inherited from collections
   - If the product specifies product-specific shipping, and also from a collection, shipping options MUST be merged.

3. Collections and Categories:
   - Products can refer to one o multiple collections using `a` tags, whether or not they are part of it, for discoverability purposes.
   - Categories ("t" tags) aid in discovery and organization

4. Location Support:
   - Optional location data aids in local marketplace features, they can point to a collection event to inherit it's value
   - Geohash enables precise location-based searches, they can point to a collection event to inherit it's value

### Product Collection (Kind: 30405)
A specialized event type using [NIP-51](51.md) like list format to organize related products into groups. Collections allow merchants or any user to create meaningful product groupings and share common attributes that products can also reference, establishing one-to-many relationships.

**Content**: Optional collection description

**Required tags**:
- `d`: Unique collection identifier
- `title`: Collection display name/title
- `a`: Product references `["a", "30402:<pubkey>:<d-tag>"]`
  - Multiple product references allowed
  - References must point to valid product listings

**Optional tags**:
- Display:
  - `image`: Collection banner/thumbnail URL
  - `summary`: Brief collection description

- Location:
  - `location`: Human-readable location string
  - `g`: Geohash for precise location lookup

- Reference Options:
  - `shipping_option`: Available shipping options `["shipping_option", "30406:<pubkey>:<d-tag>"]`, MAY appear multiple times

```jsonc
{
  "kind": 30405,
  "created_at": <unix timestamp>,
  "content": "<optional collection description>",
  "tags": [
    // Required tags
    ["d", "<collection identifier>"],
    ["title", "<collection name>"],
    ["a", "30402:<pubkey>:<d-tag>"],  // Product reference
    
    // Optional tags
    ["image", "<collection image URL>"],
    ["summary", "<collection description>"],
    
    // Location
    ["location", "<location string>"],
    ["g", "<geohash>"],
    
    // Reference Options
    ["shipping_option", "30406:<pubkey>:<d-tag>"],  // Available shipping options, MAY appear multiple times
  ]
}
```

#### Notes
1. Collection Management:
   - Collections can contain any number of products
   - Products can belong to multiple collections

2. Reference Model:
   - Collection settings (shipping, location, geohash) serve as references only
   - Products MUST explicitly reference collection resources to inherit collection attributes (e.g. shipping, location, geohash).
   - No automatic cascading of settings to products

3. Location Support:
   - Optional location data helps with marketplace organization
   - Enables geographic grouping of related products

### (Events) Define event markets and occurrence-specific offers

`draft` · `optional`

A proposed kind `30409` event market admits merchants, kind `31925` RSVPs record their participation, and kind `30402` listings offer stock and prices for individual NIP-52 occurrences. Buyers order those offers through existing private kind `16` messages.

An **event market** is an organized occasion where merchants offer goods or services to shoppers. It can take place in person, online, or both. At a craft fair, a shopper might collect a mug at a booth. During a livestream, a viewer might order the mug for shipping or buy a pattern for download.

#### Market and occurrences

The organizer publishes an addressable market record (proposed kind `30409`). Its `content` is a plain-text description. Include exactly one `["d", "<market identifier>"]`, one `["title", "<market name>"]`, one schedule reference and one market state. Each merchant on the current roster has one `merchant` tag. Use the shorter form for a merchant without event pickup and the longer form when the roster specifies a handoff. An empty roster admits nobody.

```text
["a", "<schedule address>"]
["event_market", "3", "<open|closed>"]
["merchant", "<merchant pubkey>"]
["merchant", "<merchant pubkey>", "<handoff>", "<pickup label>"]
```

Addresses use the NIP-01 `kind:pubkey:d` form. Public keys and event IDs are 64 lowercase hexadecimal characters. The `event_market` tag carries the profile version (`3`) and state (`open` or `closed`). The market identifier stays stable when the organizer updates the market. A collection (kind `30405`) groups products. The market record carries a roster and terms that the organizer can update independently of the calendar and listings.

A one-off market references a [NIP-52 occurrence](https://github.com/nostr-protocol/nips/blob/master/52.md#calendar-events): kind `31922` for an all-day event or `31923` for a timed event. For a series, reference a [kind 31924 calendar](https://github.com/nostr-protocol/nips/blob/master/52.md#calendar) and list each occurrence in it. The organizer signs the market, calendar, and occurrences. Use the current calendar list to establish membership. A timed occurrence MUST have an explicit NIP-52 `end` in Unix seconds, exclusive. A weekly stream can keep one calendar and give each episode its own address, even when every episode airs at the same URL.

When the merchant offers event pickup, handoff is `merchant_present` or `organizer_handoff` and the label identifies the booth or collection point. Shipping and digital delivery require no pickup details. The organizer may admit its own merchant key.

#### Merchant participation

Use a merchant-signed [NIP-52 RSVP](https://github.com/nostr-protocol/nips/blob/master/52.md#calendar-event-rsvp), kind `31925`. The RSVP `content` is an optional free-form note (use `""` when omitted). The merchant uses one stable `d` per market and occurrence pair and reuses it for updates. Include exactly one of each tag below, in addition to `d`.

```text
["a", "<occurrence address>"]
["e", "<occurrence event ID>"]
["market", "<market address>"]
["status", "accepted"]
```

The `e` tag identifies the exact occurrence revision the merchant acknowledged. Status `tentative` or `declined` makes the RSVP inactive. The organizer’s current roster and the merchant’s accepted RSVP together establish participation. The merchant can withdraw by replacing the RSVP with `declined`. A merchant accepting event pickup also includes one `["handoff", "<handoff>", "<pickup label>"]` matching the roster entry.

When the organizer edits the occurrence, compare the start, end, and event venue (including a published stream location) with the acknowledged revision. A changed schedule or venue calls for one fresh RSVP. A title correction or an edit to another episode leaves the acknowledgement usable. If the referenced revision is unavailable for comparison, the merchant must acknowledge the current revision before taking new event orders. Changed booth or handoff details require renewed acknowledgement for pickup only. A closed market, missing admission, ended or cancelled occurrence, or removal from the calendar makes the offer ineligible for new orders in that market. The organizer signals cancellation with `["status", "cancelled"]` on the occurrence.

#### Offers on product listings

On the merchant’s [kind 30402 product listing](#product-listing-kind-30402), `stock` and `price` describe the ordinary shop offer. The listing’s `content` remains its product description, with Markdown allowed. A sellable product or variation MAY add one offer row per occurrence in any of these forms.

```text
["a", "<occurrence address>", "", "offer", "<quantity>"]
["a", "<occurrence address>", "", "offer", "<quantity>", "<amount>", "<currency>"]
["a", "<occurrence address>", "", "offer", "<quantity>", "<amount>", "<currency>", "<frequency>"]
```

The [NIP-01 address reference](https://github.com/nostr-protocol/nips/blob/master/01.md#tags) identifies a particular NIP-52 occurrence by kind, organizer public key, and identifier. Clients can find candidate listings with a `#a` filter for that address. The third position holds a relay hint or the empty string. Keep that position when omitting the hint. Only a NIP-52 occurrence reference marked `offer` has these stock and price semantics.

- **Quantity.** Use a nonnegative integer string. Zero means sold out. An empty string offers the item subject to merchant confirmation without promising a number. Ordinary stock excludes event quantities. The occurrence quantity covers event orders across all supported fulfillment methods.
- **Price.** Omit the entire price suffix to inherit the listing’s full `price` tag. When supplied, the suffix replaces the full price using a decimal amount, an ISO 4217 currency code and the listing’s optional billing frequency format. An explicit zero amount means free. Shipping charges still follow the selected shipping option.
- **Scope.** One listing has one offer per occurrence, even if two market catalogs feature that same occurrence. A listing can have up to 32 occurrence rows. A missing offer means the product has no event offer for that occurrence. Duplicate rows or malformed quantities or prices make the affected offer unusable. An incomplete override cannot fall back to the ordinary price.

#### Orders and organizer collection

Use the existing [private order and payment messages](#4-order-communication-flow-and-payment-processing). An event order groups items from one merchant at one occurrence under one market. The buyer includes one `event` and one `fulfillment` tag in the order creation message (`type` `1`). Use the existing kind `16` content and required tags.

```text
["event", "<market address>", "<occurrence address>", "<occurrence event ID>"]
["fulfillment", "<pickup|shipping|digital>"]
```

The event ID identifies the occurrence revision used for this order. The occurrence selects the offer’s stock and unit price. The market identifies the participation and payment terms. For `shipping`, select a product-authorized [shipping option](#shipping-option-kind-30406) and supply the delivery details in the private order. For `digital`, use the listing’s digital delivery terms. For `pickup`, include the agreed `handoff` tag from the RSVP. The selected method must be available for the product.

The merchant confirms the event context and fulfillment by including the agreed `event` and `fulfillment` tags in the private payment request (`type` `2`), with `handoff` for pickup. A change to the buyer’s price, total, payment recipient, or agreed delivery or pickup terms needs buyer agreement before payment. Later edits do not rewrite accepted orders. An ordinary shop order uses ordinary stock and price, including when it ships exactly the same product.

Direct payment to the merchant is the default. An organizer offering collection publishes one `["collection", "<policy>", "<rate_bps>", "<terms>"]` tag on the market. Without this tag, payment goes directly to the merchant. Policy is `optional` or `required`. The rate is a whole number of basis points encoded as a decimal string (1000 means 10%). The terms state the basis, rounding, and refund treatment. A merchant opts in by including the same tag once on its RSVP. Under `optional` policy, a merchant who omits it receives payment directly. The collector must be the market author and the terms must match. Changed standing terms require fresh consent. The parties may agree on a smaller fee for one sale. Where collection is required, missing consent blocks the event order.

For a routed sale the merchant’s private payment request includes one `["collector", "<organizer pubkey>", "<fee_sats>"]` tag, giving the exact agreed deduction as a nonnegative whole number of satoshis in a decimal string, alongside the existing order ID, buyer total in sats, and payment instructions. Paying the authorized recipient completes the buyer’s agreed payment. An online organizer should forward a pre-approved merchant’s balance when receipt is confirmed. A payout failure remains between organizer and merchant.

#### Example of a shipped mug sold on a livestream

Clay Studio sells stoneware mugs for **USD 30** in its shop. For **River Live, episode 12**, it offers **20 mugs at USD 24 each**. Its listing references the organizer’s specific timed occurrence, identified by `river-live-episode-12`. Episode 13 could stream at the same URL and would have its own occurrence address.

```json
{
  "kind": 30402,
  "created_at": 1795651200,
  "content": "Hand-thrown stoneware mug. Ships from Clay Studio.",
  "tags": [
    ["d", "stoneware-mug"],
    ["title", "Stoneware mug"],
    ["type", "simple", "physical"],
    ["price", "30.00", "USD"],
    ["stock", "70"],
    ["shipping_option", "30406:9d8ef33e16e9ed756c78683c9831a2f9c823d54a3bb82bea6a4cb9e3aa507853:standard", "0"],
    ["a", "31923:583544a33ac1067232ecba1d1dde16538e0eeaaff10a80544427b8a7dd51ae1f:river-live-episode-12", "", "offer", "20", "24.00", "USD"]
  ],
  "pubkey": "9d8ef33e16e9ed756c78683c9831a2f9c823d54a3bb82bea6a4cb9e3aa507853",
  "id": "bcf9b7637442fc06d8d877020600d26a3bbfe32c367095b3f8eec9b096895852",
  "sig": "68746258caa6c253c130acf3c10f1a684e3f66ca290ce58c7a5fa8df369a564f8c871aa64dc24116309118f40c7b6e2f7db51c4221769bbec51034591f0ad2c9"
}
```

A viewer orders one mug during episode 12 and selects `shipping`. The event reference in the order points to the same episode as the listing’s offer row. If the selected standard shipping option costs USD 5, the quote is **USD 24 + USD 5 = USD 29** before any applicable taxes. After the sale the merchant’s listing can show **19** for episode 12 and **70** for the ordinary shop.

**Same episode, inherited price.** If the merchant ends that same offer row immediately after `"20"`, the viewer still orders from the 20 episode mugs. The unit price is then the listing’s USD 30 and the same shipping option brings the quote to **USD 35**. A shop customer ordering outside the episode also sees USD 30, with availability taken from the 70 ordinary mugs.

### Drafts
Products and collections can be saved as private drafts while being prepared for publication. This allows merchants to work on listings before making them publicly visible. Implementation MUST follow [NIP-37](https://github.com/nostr-protocol/nips/blob/master/37.md) for draft management.

### Shipping Option (Kind: 30406)
A specialized event type for defining shipping methods, costs, and constraints. Shipping options can be published by merchants or third-party providers (delivery companies, DVMs, etc.) and referenced by product listings or collections.

**Content**: Optional human-friendly shipping description

**Required tags**:
- `d`: Unique shipping option identifier
- `title`: Display title for the shipping method
- `price`: Base cost array `[<base_cost>, <currency>]`
- `country`: Array of ISO 3166-1 alpha-2 country codes `[<code1>, <code2>, ...]`
- `service`: Service type ("standard", "express", "overnight", "pickup")

**Optional tags**:
- Extra details:
  - `carrier`: The name of the carrier that will be used for the delivery
- Time and Location:
  - `region`: Array of ISO 3166-2 region codes for which shipping method is available `[<code1>, <code2>, ...]`
  - `duration`: Delivery window `[<min>, <max>, <unit>]` using ISO 8601 duration units
    - min: Minimum delivery time
    - max: Maximum delivery time
    - unit: "H" (hours), "D" (days), "W" (weeks)
  - `location`: Physical address for pickup
  - `g`: Geohash for precise location

- Constraints:
  - `weight-min`: Minimum weight `[<value>, <unit>]` (ISO 80000-1)
  - `weight-max`: Maximum weight `[<value>, <unit>]`
  - `dim-min`: Minimum dimensions `[<l>x<w>x<h>, <unit>]`
  - `dim-max`: Maximum dimensions `[<l>x<w>x<h>, <unit>]`

- Price Calculations:
  - `price-weight`: Per weight pricing `[<price>, <unit>]`
  - `price-volume`: Per volume pricing `[<price>, <unit>]`
  - `price-distance`: Per distance pricing `[<price>, <unit>]`

```jsonc
{
  "kind": 30406,
  "created_at": <unix timestamp>,
  "content": "<optional shipping description>",
  "tags": [
    // Required tags
    ["d", "<shipping identifier>"],
    ["title", "<shipping method title>"],
    ["price", "<base_cost>", "<currency>"],
    ["country", "<ISO 3166-1 alpha-2>", "...", "..."],  // Array of country codes
    ["service", "<service-type>"],

    // Extra details
    ["carrier","<name of the carrier>"]
    
    // Time and Location
    ["region", "<ISO 3166-2 code>", "...", "..."],  // Array of region codes
    ["duration", "<min>", "<max>", "<unit>"],  // ISO 8601 duration units (H/D/W)
    ["location", "<address string>"],
    ["g", "<geohash>"],
    
    // Constraints
    ["weight-min", "<value>", "<unit>"],
    ["weight-max", "<value>", "<unit>"],
    ["dim-min", "<l>x<w>x<h>", "<unit>"],
    ["dim-max", "<l>x<w>x<h>", "<unit>"],
    
    // Price Calculations
    ["price-weight", "<price>", "<unit>"],
    ["price-volume", "<price>", "<unit>"],
    ["price-distance", "<price>", "<unit>"]
  ]
}
```

#### Implementation Examples

Local Pickup:
```jsonc
{
  "kind": 30406,
  "created_at": 1703187600,
  "content": "Downtown Store Pickup",
  "tags": [
    ["d", "downtown-pickup"],
    ["title", "Downtown Store Pickup"],
    ["price", "0", "USD"],
    ["country", "US"],
    ["region", "US-FL"],
    ["service", "pickup"],
    ["location", "123 Main St, Downtown, FL"],
    ["g", "dhwm9c4ws"]
  ]
}
```

Standard Shipping:
```jsonc
{
  "kind": 30406,
  "created_at": 1703187600,
  "content": "Standard Regional Shipping",
  "tags": [
    ["d", "standard-regional"],
    ["title", "Standard Shipping"],
    ["price", "5.99", "USD"],
    ["country", "US"],
    ["region", "US-FL"],
    ["service", "standard"],
    ["duration", "24", "72", "H"],  // 24-72 hours delivery window
    ["weight-max", "30", "kg"],
    ["dim-max", "120x60x60", "cm"],
    ["price-weight", "0.75", "USD", "kg"]
  ]
}
```

#### Notes
1. Event Management:
   - Create separate events for each distinct shipping option
   - Each option needs a unique `d` tag identifier
   - Merchants can reference third-party shipping options

2. Shipping Rules:
   - Physical pickup requires location and/or geohash
   - Weight/dimension constraints use ISO 80000-1 units

3. Client Behavior:
   - Group options by service type and location
   - Use geohash for distance-based sorting
   - Validate package constraints before offering options

<br>

## 4. Order Communication Flow and Payment Processing

Order processing and status updates use [NIP-17](17.md) encrypted direct messages, with three event kinds serving different purposes:

- Kind `14`: Regular communication between parties
  - General inquiries and responses
  - Order clarifications
  - Subject can be order ID or empty
  
- Kind `16`: Order processing and status. These messages include a `type` field that indicates the specific kind of message
  - Order creation and details. `type`: 1
  - Payment requests. `type`: 2
  - Status updates. `type`: 3
  - Shipping information. `type`: 4
  
- Kind `17`: Payment receipts and verification

Message direction is determined by the author, and `p` tag:
- Buyer → Merchant: event author is the buyer, `p` tag contains merchant's pubkey
- Merchant → Buyer: event author is the merchant, `p` tag contains buyer's pubkey

The payment request flow can operate in two modes:
1. Direct: Merchant processes requests manually. Payment request is initiated by the merchant
2. Service-assisted: Merchant's payment service handles requests. Payment request is initiated by the buyer

### Message Types
#### 1. Order Creation
Sent by buyer to initiate order process.

**Content:** (Optional) Human readable order notes or special requests

**Required tags:**
- `p`: Merchant's public key
- `subject`: Human-friendly subject line for order information
- `type`: Must be "1" to indicate order creation
- `order`: Unique identifier for the order
- `amount`: Total order amount in satoshis
- `item`: Product reference in format "30402:<pubkey>:<d-tag>" with quantity. MAY appear multiple times

**Optional tags:**
- `shipping`: Reference to shipping option "30406:<pubkey>:<d-tag>"
- `address`: Shipping address details
- `email`: Customer email for contact
- `phone`: Customer phone number for contact
- Other optional tags can be added with more details from the customer

```jsonc
{
  "kind": 16,
  "tags": [
    // Required tags
    ["p", "<merchant-pubkey>"],
    ["subject", "<order-info subject>"],
    ["type", "1"],  // Order creation
    ["order", "<order-id>"],  // Unique order identifier
    ["amount", "<total-amount-in-sats>"],
    
    // Order items (can repeat)
    ["item", "30402:<pubkey>:<d-tag>", "<quantity>"],
    
    // Shipping details
    ["shipping", "30406:<pubkey>:<d-tag>"],
    ["address", "<shipping-address>"],
    
    // Customer contact
    ["email", "<customer-email>"],  // Optional
    ["phone", "<customer-phone>"],  // Optional
  ],
  "content": "Order notes or special requests"
}
```
#### 2. Payment Request
There are two variants depending on payment processing mode: manual or automatic processing. After the buyer pays the payment request, they MUST send a payment receipt to the merchant using a kind:`17` dm.

##### Manual Processing (merchant → buyer)

In this mode, the merchant manually initiates the payment by sending a payment request to the buyer. This requires either:
- The merchant being online to process requests, or
- Having an automated system for processing payment requests, which can be run by the merchant or a service they rely on according to merchant preferences.

Important considerations:
- Merchant shouldn't have a recommended application in their merchant's preferences
- Final price may differ from the order creation time
- Merchants decide whether to honor original prices
- Buyers can cancel orders if they don't agree with price changes

**Content:** (Optional) Human readable payment instructions and notes

**Required tags:**
- `p`: Buyer's public key
- `subject`: Human-friendly subject line for order payment requests
- `type`: Must be "2" to indicate payment request
- `order`: The unique order identifier from the original order
- `amount`: Total payment amount in satoshis

**Optional tags:**
- `payment`: Payment method details, can appear multiple times for different options:
  - Lightning format: `["payment", "lightning", "<bolt11-invoice or lud16>"]`
  - Bitcoin format: `["payment", "bitcoin", "<btc-address>"]`
  - eCash format: `["payment", "ecash", "<cashu-req>"]`
  - LNURLcash format: `["payment", "lnurlcash", "<accepted-service-url>"]` — merchant signals acceptance of LUD-25 bearer notes from an issuing service
- `expiration`: Include if the payment format has a defined expiration time

```jsonc
{
  "kind": 16,
  "tags": [
    // Required tags
    ["p", "<buyer-pubkey>"],
    ["subject", "order-payment"],
    ["type", "2"],  // Payment request
    ["order", "<order-id>"],
    ["amount", "<total-amount-in-sats>"],
    
    // Payment options (can include multiple)
    ["payment", "lightning", "<bolt11-invoice|lud16>"],
    ["payment", "bitcoin", "<btc-address>"],
    ["payment", "ecash", "<cashu-req>"],
    ["payment", "lnurlcash", "<accepted-service-url>"],
    ["expiration", "<unix-timestamp>"],
  ],
  "content": "Payment instructions and notes"
}
```

##### Automatic Processing (buyer → merchant)
In this mode, the merchant MUST set valid payment options in their kind:`0` event (such as `cashu` or `lud16`). The key difference is that the buyer initiates the payment request using information provided by the merchant. For merchants using `manual` payment preference, they SHOULD use [NIP-89](89.md) to specify their preferred payment processing service, which can then automatically handle payment requests on their behalf, as described in the merchant preferences section above.

```jsonc
{
  "kind": 16,
  "tags": [
    // Required tags
    ["p", "<merchant-pubkey>"],
    ["subject", "order-payment"],
    ["type", "2"],  // Payment request
    ["order", "<order-id>"],
    ["amount", "<total-amount-in-sats>"],
    
    // Payment details from service
    ["payment", "lightning", "<bolt11-invoice|bolt12-offer>"],
    ["payment", "bitcoin", "<btc-address>"],
    ["payment", "ecash", "<cashu-req>"],
    ["payment", "lnurlcash", "<accepted-service-url>"],
  ],
  "content": "Service-generated payment details"
}
```

#### 3. Order Status Updates
Once the merchant receives payment, they MUST update the status to "confirmed". Status updates can be sent as soon as a new order is acknowledged, initially setting the status to "pending". The "pending" status is optional and can be skipped, starting directly with "confirmed" once payment is received.

**Content:** (Optional) Human readable status update

**Required tags:**
- `p`: Buyer's public key
- `subject`: Human-friendly subject line for status updates
- `type`: Must be "3" to indicate status update
- `order`: The original order identifier
- `status`: Current order status:
  - `pending`: Order received but awaiting payment
  - `confirmed`: Payment received and verified
  - `processing`: Order is being prepared
  - `completed`: Order fulfilled
  - `cancelled`: Order cancelled by either party

```jsonc
{
  "kind": 16,
  "tags": [
    // Required tags
    ["p", "<buyer-pubkey>"],
    ["subject", "order-info"],
    ["type", "3"],  // Status update
    ["order", "<order-id>"],
    
    // Status information
    ["status", "<order-status>"],  // pending|confirmed|processing|completed|cancelled
  ],
  "content": "Human readable status update"
}
```

Buyers may also send a status update to cancel an order, ideally before the status has been set to "confirmed":

```jsonc
{
  "kind": 16,
  "tags": [
    // Required tags
    ["p", "<merchant-pubkey>"],
    ["subject", "order-info"],
    ["type", "3"],  // Status update
    ["order", "<order-id>"],
    
    // Status information
    ["status", "<order-status>"],  // cancelled
  ],
  "content": "Human readable status update"
}
```

#### 4. Shipping Updates
Sent by merchant to provide delivery tracking and status information.

**Content:** (Optional) Human readable shipping status and tracking information

**Required tags:**
- `p`: Buyer's public key
- `subject`: Human-friendly subject line for shipping updates
- `type`: Must be "4" to indicate shipping update
- `order`: The original order identifier
- `status`: Current shipping status:
  - `processing`: Order is being prepared for shipping
  - `shipped`: Package has been handed to carrier
  - `delivered`: Successfully delivered to destination
  - `exception`: Delivery issue or delay encountered

**Optional tags:**
- `tracking`: Carrier's tracking number
- `carrier`: Name of shipping carrier
- `eta`: Expected delivery time as unix timestamp

```jsonc
{
  "kind": 16,
  "tags": [
    // Required tags
    ["p", "<buyer-pubkey>"],
    ["subject", "shipping-info"],
    ["type", "4"],  // Shipping update
    ["order", "<order-id>"],
    
    // Shipping details
    ["status", "<shipping-status>"],  // processing|shipped|delivered|exception
    ["tracking", "<tracking-number>"],
    ["carrier", "<carrier-name>"],
    ["eta", "<unix-timestamp>"],
  ],
  "content": "Shipping status and tracking information"
}
```

#### 5. General Communication
Used for any order-related messages (Kind 14)

```jsonc
{
  "kind": 14,
  "tags": [
    // Required tags
    ["p", "<recipient-pubkey>"],
    ["subject", "<order-id>"],  // Optional, can be empty
  ],
  "content": "General communication message"
}
```

#### 6. Payment Receipt
Sent by buyer to confirm payment completion. The receipt can include proof of payment from any payment system, including traditional fiat gateways.

**Content:** (Optional) Human readable payment confirmation details

**Required tags:**
- `p`: Merchant's public key
- `subject`: Human-friendly subject line for order receipt
- `order`: The original order identifier
- `payment`: Payment proof details (at least one required):
  - Generic format: `["payment", "<medium>", "<medium-reference>", "<proof>"]`
  - Common examples:
    - Lightning: `["payment", "lightning", "<invoice>", "<preimage>"]`
    - Bitcoin: `["payment", "bitcoin", "<address>", "<txid>"]`
    - eCash: `["payment", "ecash", "<mint-url>", "<proof>"]`
    - LNURLcash: `["payment", "lnurlcash", "<service-url>", "<note>"]` — a LUD-25 bearer note redeemable via LNURL-withdraw; the merchant MUST redeem it before confirming the order
    - Fiat: `["payment", "fiat", "<some-id>", "<some-proof>"]`
- `amount`: Payment amount

```jsonc
{
  "kind": 17,
  "tags": [
    // Required tags
    ["p", "<merchant-pubkey>"],
    ["subject", "order-receipt"],
    ["order", "<order-id>"],
    
    // Payment proof (one required)
    ["payment", "<medium>", "<medium-reference>", "<proof>"],
    ["payment", "lightning", "<invoice>", "<preimage>"],
    ["payment", "bitcoin", "<address>", "<txid>"],
    ["payment", "ecash", "<mint-url>", "<proof>"],
    ["payment", "lnurlcash", "<service-url>", "<note>"],
    ["payment", "fiat", "<some-id>", "<some-proof>"],

    // Metadata
    ["amount", "<amount>"]
  ],
  "content": "Payment confirmation details"
}
```

#### Notes
1. Message Flow:
   - Receipts should include verifiable proofs

2. Payment Processing:
   - Manual mode provides more flexibility
   - Automatic mode enables faster processing and convenience
   - Multiple payment options can be offered

3. Status Tracking:
   - Use consistent status codes
   - Include timestamps for all updates
   - Provide clear user messages

<br>

## 5. Product Reviews (Kind: 31555)

Product reviews follow [NIP-85](https://github.com/nostr-protocol/nips/blob/b1432b705f553bde6c4eb5fcfde8525d2913b477/85.md) and [QTS](https://habla.news/u/arkinox@arkinox.tech/DLAfzJJpQDS4vj3wSleum) guidelines with additional marketplace-specific rating criteria. Reviews provide structured feedback about products, merchants, and the overall purchase experience.

**Content:** Detailed review text

**Required tags:**
- `d`: Reference to product `["d", "a:30402:<merchant-pubkey>:<product-d-tag>"]`
- `rating`: Primary rating `["rating", "<score>", "thumb"]`
  - score: 0 (negative) to 1 (positive)
  - "thumb" label MUST be present as primary rating

**Optional tags:**
- Additional Ratings:
  - `rating`: Category scores `["rating", "<score>", "<category>"]`
    - score: 0 to 1 (supports fractional values)
    - category: These are optional, some standard categories may include:
      - "value": Price vs quality
      - "quality": Product quality
      - "delivery": Shipping experience
      - "communication": Merchant responsiveness

```jsonc
{
  "kind": 31555,
  "created_at": <unix timestamp>,
  "tags": [
    // Required tags
    ["d", "a:30402:<merchant-pubkey>:<product-d-tag>"],
    ["rating", "1", "thumb"],  // Primary rating
    
    // Optional rating categories
    ["rating", "0.8", "value"],
    ["rating", "1.0", "quality"],
    ["rating", "0.6", "delivery"],
    ["rating", "0.9", "communication"]
  ],
  "content": "Detailed review text"
}
```

#### Rating Calculation
The final score combines the primary "thumb" rating (50% weight) with additional category ratings (50% combined weight):

```
Total Score = (Thumb × 0.5) + (0.5 × (∑(Category Ratings) ÷ Number of Categories))
```

#### Notes
1. Rating System:
   - Primary thumb rating is required, it determines the overall an overall rating.
   - Additional categories are optional
   - Scores support fractional values between 0-1
   - Custom categories can be added

<br>

## 6. Implementation Guidelines

### Payment Flow Details

#### Payment Preferences
Merchants can specify their payment preferences in their kind:`0` event using the `payment_preference` tag:
```
["payment_preference", "<manual | ecash | lud16>"]
```

If not present, it defaults to `manual`. The preferences are processed in this order of complexity:
1. Manual (default): Merchant provides payment requests directly
2. eCash: Ideally the merchant has a kind `10019` event to know what mint they prefer.
  - If the `10019` event is not present, payment can be made by sending the token embedded directly in the order receipt message from a previously set mint (whether default or user selected); otherwise, the merchant's preferred mint SHOULD be used.
3. Lightning: Requires `lud16` or related lightning fields in kind `0`

#### Payment Processing Scenarios

1. **Manual Processing**
   - Merchant initiates payment request
   - Used when no application is recommended or automatic preferences are set
   - Merchant must manually send payment requests
   - Buyer waits for merchant's payment instructions
   - Merchants can have their own service that listens for new orders and then sends the payment request

2. **Automatic Processing**
   - Buyer initiates payment request
   - Requires a valid `payment_preference` in merchant's kind `0`
   - Service-Based Processing processing if `payment_preference` is `manual` and the merchant have a recommended application
   - Supports automatic payments via:
     - eCash tokens (locked to merchant's pubkey)
     - Lightning (using merchant's `lud16` address)
     - LNURLcash notes (LUD-25, draft — bearer notes redeemable via LNURL-withdraw)

3. **Service-Based Processing**
   - Merchant MUST set `payment_preference` to `manual`
   - Merchant SHOULD have a [NIP-89](89.md) kind `31989` event recommending their preferred service
   - Buyers can immediately request payment using the service
   - Service handles payment details and completion monitoring

For all scenarios:
- Buyer MUST send payment receipt after completion
- Message direction is determined by `p` tag
- Merchant's [NIP-89](89.md) application preferences SHOULD be respected

### Marketplace Application Role
Marketplace applications can optionally facilitate the order processing and payment request by:

1. Generating payment requests based on merchant preferences when buyers initiate orders
2. Verifying payments and generating receipts automatically by prompting the buyer to sign the event
3. Helping merchants managing inventory and order status updates
4. Coordinating shipping information
5. Price calculations

This provides a smoother user experience while maintaining the ability for direct merchant-buyer communication as a fallback mechanism.

### Notes and Considerations

1. Tags are used for all structured, machine-readable data to facilitate easier parsing and filtering.

2. The content field is reserved for human-readable messages and additional information that doesn't require machine parsing.

3. All timestamps should be in Unix format (seconds since epoch).

4. Order IDs should be used consistently across all related messages.

5. Message threading should follow [NIP-10](10.md) conventions when replies are needed.
