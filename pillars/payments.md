# Payments Pillar

Status: normative transposition of current merchant preference, payment request, and payment receipt material.

This file copies the implementation-sensitive payment sections from [../SPEC.md](../SPEC.md). Do not change payment preference values, payment tag shapes, amount semantics, receipt examples, or NIP references in this transposition.

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
  ],
  "content": "Service-generated payment details"
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
