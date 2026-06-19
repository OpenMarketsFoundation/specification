# Items Pillar

Status: normative transposition of current listing, collection, draft, and review material.

This file copies the implementation-sensitive item sections from [../SPEC.md](../SPEC.md). Do not change kind numbers, tag names, tag shapes, required/optional semantics, examples, or normative keywords in this transposition.

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

### Drafts
Products and collections can be saved as private drafts while being prepared for publication. This allows merchants to work on listings before making them publicly visible. Implementation MUST follow [NIP-37](https://github.com/nostr-protocol/nips/blob/master/37.md) for draft management.

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
