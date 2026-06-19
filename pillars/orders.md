# Orders Pillar

Status: normative transposition of current order communication material.

This file copies the implementation-sensitive order sections from [../SPEC.md](../SPEC.md). Payment request, payment receipt, and shipping update details are also represented in the payment and delivery pillars for navigation, but the canonical contiguous context remains [../SPEC.md](../SPEC.md).

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
