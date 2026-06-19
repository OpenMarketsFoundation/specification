# E-commerce Lane

Status: normative transposition of current e-commerce requirements.

This lane preserves the current Open Markets e-commerce flow as the first fully expressed market lane. The canonical contiguous compatibility snapshot remains [../SPEC.md](../SPEC.md). The copied section below is unchanged from the pre-refactor specification.

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

## Related Pillars

- Items: [../pillars/items.md](../pillars/items.md)
- Orders: [../pillars/orders.md](../pillars/orders.md)
- Payments: [../pillars/payments.md](../pillars/payments.md)
- Delivery: [../pillars/delivery.md](../pillars/delivery.md)

The existing standard e-commerce flow remains in [../docs/architecture.md](../docs/architecture.md). Future lanes can be added without changing this lane's current requirements.
