# Delivery Pillar

Status: normative transposition of current shipping option and shipping update material.

This file copies the implementation-sensitive delivery sections from [../SPEC.md](../SPEC.md). The delivery pillar is broad enough to hold future physical, digital, service, ride, lodging, pickup, and milestone fulfillment work, but this PR does not add new delivery semantics.

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
