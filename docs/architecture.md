# Architecture

Status: explanatory map plus unchanged current core protocol text.

Open Markets is organized around four homes for existing and future work: items, orders, payments, and delivery. This document is a navigation layer. It does not redefine the protocol; [../SPEC.md](../SPEC.md) remains the contiguous compatibility snapshot.

## Pillar Map

- Items: listings, collections, drafts, reviews, product metadata, discovery, categorization, and pricing.
- Orders: order creation, buyer/seller intent, status transitions, cancellation, and order-linked communication.
- Payments: merchant preferences, payment requests, payment receipts, payment proofs, and future payment rails.
- Delivery: shipping options, pickup, shipping updates, and future fulfillment models.

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

## Navigation

- Item event material is transposed into [../pillars/items.md](../pillars/items.md).
- Order communication material is transposed into [../pillars/orders.md](../pillars/orders.md).
- Payment preference and receipt material is transposed into [../pillars/payments.md](../pillars/payments.md).
- Shipping and fulfillment material is transposed into [../pillars/delivery.md](../pillars/delivery.md).
- The current e-commerce lane is preserved in [../lanes/ecommerce.md](../lanes/ecommerce.md).
