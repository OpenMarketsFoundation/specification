# Product Modifiers and Variation Details

Status: experimental proposal. This page is not current normative Open Markets text.

## Problem

A café sells a latte in two sizes. A customer can choose the milk, add syrups, and add extra shots. Each of those changes the price, and the order has to say exactly what was chosen so the café can make it and charge for it.

The specification already covers the sizes. A product can be published as a `variable` parent with one `variation` listing per size, and each size has its own price and stock. But it does not answer three questions, and this proposal answers them:

- The parent must carry a price. Which price?
- How does a size listing say "I am the 16 oz"?
- Can a customer order the parent itself, or only a size?

The specification has nothing for the milk, the syrups or the shots. Making every combination a separate size does not work: two sizes, four milks and a handful of syrups is dozens of listings for one latte. And an order line can only name a product and a quantity, so there is no way to say "oat milk, on the first latte, not the second".

This proposal adds two things.

The first is a rule a collection can carry, the **`select` tag**, that says how many of its members a customer may pick: exactly one milk, up to three syrups. The specification has no way to say that today.

The second is the **modifier**: an ordinary product that is sold only together with another product. Modifiers are grouped into **modifier groups**, which are collections marked as such and carrying a `select` rule, and a product says which groups it accepts. An order line that names a modifier also says which line it belongs to.

Everything added here is optional. A reader that knows nothing about this proposal still sees valid listings and a valid order with the right total. Synvya runs the listings, the groups and the order-line link in production for restaurant takeout, on an order line written as a positional array; the `extensions` form given for the private commerce envelope is specified here and not yet implemented. The example below is a real coffee menu.

## Non-goals

- A modifier whose price depends on the size of the product it goes with. A modifier has one price.
- A modifier on a modifier.
- One product that is both sold on its own and used as a modifier. Fries as a side dish and fries added to a burger are two products.
- A second variation axis on one product. If a drink comes in sizes and also hot or iced, the sizes are the variations and "hot or iced" is a modifier group where the customer picks exactly one.

## Terms

- **Product**: a `kind:30402` listing.
- **Parent**: a product with `type` = `variable`. It describes the product and holds what its variations share. It is never sold.
- **Variation**: a product with `type` = `variation` and an `a` tag that names its parent. It is one sellable form of the parent, for example one size.
- **Modifier**: a product sold only together with another product: a syrup, a milk, an extra shot, a side. The word is the one Square, Toast, Clover and the delivery platforms use; schema.org calls the same thing `menuAddOn`.
- **Modifier group**: a `kind:30405` collection marked `["type", "modifier_group"]`, whose members are modifiers, with a `select` rule for how many may be picked.
- **Sellable product**: anything an order line may name: a simple product, a variation, or a modifier.

## Variations: three things the current text leaves unsaid

The specification requires a `price` on every product and says a variation must carry an `a` tag pointing at its parent. It stops there. The three readings below fill the gaps so that two implementations behave the same way.

### The parent's price is its lowest price

A parent's `price` is the lowest price among its variations, in the same currency. A reader that only knows one price per product shows it as a starting price: "from $4.50". When a merchant reprices a variation and that changes which one is cheapest, the merchant republishes the parent too.

### A variation says what it is with a `spec` tag

A variation carries one `spec` tag with the axis it varies on and its value:

```jsonc
["spec", "size", "16 oz"]
```

The axis is free text; `size` is the usual one. A reader lists a parent's variations by price, lowest first, and then by this value.

The variation's `title` is a complete name on its own, such as `Latte — 16 oz`, so a reader that ignores `spec` still shows something sensible. A reader never takes the label apart from the title; it reads `spec`.

### A parent is never sold, and each variation has its own stock

An order line never names a parent. If a merchant receives one that does, the merchant declines the order. A parent has no `stock` tag. Each variation carries its own stock, and a reader never adds variation stock up into a parent total or subtracts from one. The open [event-commerce proposal](https://github.com/OpenMarketsFoundation/specification/pull/15) says the same for the listings it assigns to events; this proposal says it for every variable product.

## Choosing from a collection: the `select` tag

A collection can say how many of its members a customer may pick. That is a new idea for the specification: today a collection only groups products, it never limits a choice. The rule is one tag:

```jsonc
["select", "<min>", "<max>"]
```

Read it as "pick at least `min` and at most `max` from this list". `1`, `1` means the customer must pick exactly one. `0`, `3` means the customer may pick none, or up to three. `min` and `max` are whole numbers, `min` is not above `max`, and `max` is at least `1`.

The numbers are for one unit of the product the choice goes with. "Up to three" on a syrups group means up to three pumps on that one latte, in any mix of flavours; a second latte on the same order gets its own three.

| Group | `select` | What the customer sees |
|---|---|---|
| Milk | `1`, `1` | Pick one; a milk is required |
| Syrups | `0`, `3` | Optional; up to three pumps in any mix |
| Extra shots | `0`, `4` | Optional; up to four of the one modifier |
| Tea blend | `1`, `1` | Pick one; every blend is free |

This proposal uses `select` on modifier groups only. The tag is defined on its own so that a later proposal can put the same rule on another kind of collection without redefining it.

## Modifiers

### The modifier product

A modifier is an ordinary simple product. That is one deliberate difference from a point-of-sale system, where a modifier lives only inside its group and has no identity of its own: here it has its own coordinate, price and stock, so an order stays a flat list of purchasable products with amounts, and running out of oat milk is ordinary stock. Its price is what it adds to the order, in the same currency as the products it goes with, and a free choice has a price of `0`. It references the same shipping options as the products it goes with, so a merchant's fulfilment check works line by line without special cases. Its `a` tag names the modifier group it belongs to.

```jsonc
{
  "kind": 30402,
  "content": "**Vanilla syrup**",
  "tags": [
    ["d", "syrup-vanilla"],
    ["title", "Vanilla syrup"],
    ["type", "simple", "physical"],
    ["price", "0.50", "USD"],
    ["shipping_option", "30406:<merchant>:pickup"],
    ["a", "30405:<merchant>:syrups"]
  ]
}
```

### The modifier group

A modifier group is a list of choices that go with a drink or a dish: the milks a latte can have, the syrups that can be added to any coffee, the blends a tea comes in. It is a `kind:30405` collection with two extra tags:

- `["type", "modifier_group"]` says this collection is a modifier group, not a menu or a section. Every product it lists is a modifier.
- `["select", "<min>", "<max>"]` says how many of them a customer may pick, as defined above. The tag is required on a modifier group.

The modifiers are listed in the order the merchant wants them shown. When the group requires a choice, the first modifier in that order that is not sold out is the one preselected for the customer.

A group has no `parent` tag, and it never lists a `variable` or `variation` product.

```jsonc
{
  "kind": 30405,
  "content": "",
  "tags": [
    ["d", "syrups"],
    ["title", "Syrups"],
    ["type", "modifier_group"],
    ["select", "0", "3"],
    ["a", "30402:<merchant>:syrup-vanilla"],
    ["a", "30402:<merchant>:syrup-caramel"]
  ]
}
```

### A product says which groups it accepts

A product lists each modifier group it accepts with an `modifier_group` tag, one per group:

```jsonc
["modifier_group", "30405:<merchant>:milk"],
["modifier_group", "30405:<merchant>:syrups"]
```

This is the same pattern the specification already uses for shipping: a product points at a collection to take on what that collection defines, and nothing applies to a product unless the product points at it. One group can serve any number of products, so "any coffee can have a syrup" is one syrups group referenced by every coffee.

A parent and each of its variations carry the same `modifier_group` tags, so every listing a customer might order is complete on its own. If a product points at a group that cannot be found, a reader ignores that tag, and a merchant republishing the product keeps it.

The two directions have one owner each. Whether a product accepts a group is decided by the product's own `modifier_group` tag, never by the group. Whether a product is a modifier is decided by the product's own `a` tag naming a group marked `modifier`; the group's member list gives the display order, and a member the group lists whose own `a` tag names a different collection is ignored. This keeps the specification's rule that nothing applies to a product unless the product itself points at it.

### What a reader shows

A reader looks at each product and decides what it is:

| Listing | How a reader can tell | Where it appears | Can it be ordered |
|---|---|---|---|
| Simple product | `type` is `simple`, and it is not listed by a modifier group | On the menu | Yes |
| Parent | `type` is `variable` | On the menu, with its variations beneath it | No |
| Variation | `type` is `variation`, and its `a` tag names a parent that exists | Under its parent | Yes |
| Modifier | Its collection is marked `["type", "modifier_group"]` | As a choice on a product that accepts its group | Only together with a product |

A variation whose parent cannot be found, and a modifier whose group cannot be found, are neither shown nor sold.

## Order lines

An order is a list of lines, and each line names a sellable product and a quantity. This proposal adds one optional value to a line that names a modifier: the position of the line it belongs to, counting from zero.

In plain terms: the latte is line 0, so the oat milk line says "0". A second drink is line 3, so its extra shot says "3". Without this, an order with two drinks cannot say which one gets the oat milk.

### On the current `kind:16` order

The `item` tag gains an optional fourth value:

```jsonc
["item", "30402:<merchant>:latte-16-oz",   "1"],
["item", "30402:<merchant>:oat-milk",      "1", "0"],
["item", "30402:<merchant>:syrup-vanilla", "2", "0"],
["item", "30402:<merchant>:americano",     "1"],
["item", "30402:<merchant>:extra-shot",    "1", "3"]
```

That order is one 16 oz latte with oat milk and two pumps of vanilla, and one americano with an extra shot. `amount` is still the sum of every line.

### On the private commerce envelope

The [private structured commerce messages](https://github.com/OpenMarketsFoundation/specification/pull/12) proposal gives every order line an immutable random `line_id`, allows no undeclared field on a line, and puts optional additions in a namespaced `extensions` object on the payload. So on that envelope the link is not a position but a `line_id`, carried in one extension entry that maps each modifier line to its product line:

```jsonc
{
  "buyer": "<customer pubkey>",
  "merchant": "<merchant pubkey>",
  "items": [
    { "line_id": "a1…", "listing": { "coordinate": "30402:<merchant>:latte-16-oz",    "event_id": "…" }, "quantity": "1", "unit": "item", "amount": { "value": "5", "unit": "USD" } },
    { "line_id": "b2…", "listing": { "coordinate": "30402:<merchant>:oat-milk",       "event_id": "…" }, "quantity": "1", "unit": "item", "amount": { "value": "0.6", "unit": "USD" } },
    { "line_id": "c3…", "listing": { "coordinate": "30402:<merchant>:syrup-vanilla",  "event_id": "…" }, "quantity": "2", "unit": "item", "amount": { "value": "1", "unit": "USD" } }
  ],
  "total": { "value": "6.6", "unit": "USD" },
  "extensions": {
    "openmarkets:modifiers": { "b2…": "a1…", "c3…": "a1…" }
  },
  "requires": ["openmarkets:modifiers"]
}
```

Each key is the `line_id` of a modifier line and each value the `line_id` of the product line it belongs to. The entry is listed in `requires`, because a merchant that cannot read it cannot check the rules below or price the order as the customer meant it; under #12's rules an unknown required extension makes the order unsupported rather than silently accepted. A `line_id` survives a re-issued order (`supersedes`) where a position would not, which is why the link is an id here and a position only on the kind `16` tag, which has no ids.

Synvya's implementation writes this form for takeout: object lines with a minted `line_id`, the `openmarkets:modifiers` entry above, and the entry listed in `requires`. It replaces an earlier positional line, `[coord, price, quantity, total]`, with the link as an optional fifth value, which predates #12's object line and is no longer written. The amounts above follow #12's money type, which allows no trailing zeros: `"5"`, not `"5.00"`; a product's `price` tag keeps its own format.

### What makes an order well formed

A merchant checks these before accepting:

1. Every line names a product that can be sold. A line that names a parent is refused.
2. A line that names a modifier has a link, and a line with a link names a modifier.
3. The link points at a product line, never at another modifier line.
4. The product on that line accepts the modifier's group.
5. The modifier's quantity is a whole multiple of the product line's quantity. Two lattes with one vanilla each is a latte line of quantity 2 and a vanilla line of quantity 2. Two lattes with different modifiers are two latte lines.
6. For each group the product accepts, the count for one product is within the group's `select` range. The count is the sum of the quantities of every modifier line from that group that links to the product line, divided by the product line's quantity (rule 5 makes that a whole number). A latte line of quantity 1 with a vanilla line of 2 and a caramel line of 1 from the same syrups group counts 3.

A merchant that finds a line breaking one of these declines the order. A product whose required group (`min` of 1 or more) has no modifier that can be sold — every member sold out or missing — cannot be ordered at all, and a reader shows it that way rather than offering it without the choice. Every line is priced at the merchant's own price for that product; nothing is computed from another line.

A reader that knows nothing about the link still sees every line as a product with a quantity, and the total is the same. The only thing it cannot tell is which product each modifier goes with.

## Stock

Each sellable product has its own stock, whether it is a simple product, a variation or a modifier. Running out of oat milk is `stock` = `0` on the oat milk product, and the merchant declines any line that names it. No product's stock is shared with or subtracted from another's.

## Worked example

A latte in two sizes, with a required milk and optional syrups.

```jsonc
// The parent
{ "kind": 30402, "content": "**Latte**\n\nEspresso with steamed milk.", "tags": [
  ["d", "latte"], ["title", "Latte"], ["type", "variable", "physical"],
  ["price", "4.50", "USD"],
  ["shipping_option", "30406:<merchant>:pickup"],
  ["modifier_group", "30405:<merchant>:milk"],
  ["modifier_group", "30405:<merchant>:syrups"],
  ["a", "30405:<merchant>:coffee"] ] }

// The 12 oz size
{ "kind": 30402, "content": "**Latte — 12 oz**\n\nEspresso with steamed milk.", "tags": [
  ["d", "latte-12-oz"], ["title", "Latte — 12 oz"], ["type", "variation", "physical"],
  ["price", "4.50", "USD"], ["spec", "size", "12 oz"], ["stock", "20"],
  ["shipping_option", "30406:<merchant>:pickup"],
  ["modifier_group", "30405:<merchant>:milk"],
  ["modifier_group", "30405:<merchant>:syrups"],
  ["a", "30402:<merchant>:latte"] ] }

// The 16 oz size
{ "kind": 30402, "content": "**Latte — 16 oz**\n\nEspresso with steamed milk.", "tags": [
  ["d", "latte-16-oz"], ["title", "Latte — 16 oz"], ["type", "variation", "physical"],
  ["price", "5.00", "USD"], ["spec", "size", "16 oz"], ["stock", "12"],
  ["shipping_option", "30406:<merchant>:pickup"],
  ["modifier_group", "30405:<merchant>:milk"],
  ["modifier_group", "30405:<merchant>:syrups"],
  ["a", "30402:<merchant>:latte"] ] }

// A group where the customer must pick one
{ "kind": 30405, "content": "", "tags": [
  ["d", "milk"], ["title", "Milk"], ["type", "modifier_group"], ["select", "1", "1"],
  ["a", "30402:<merchant>:whole-milk"],
  ["a", "30402:<merchant>:oat-milk"] ] }

// The free default in that group
{ "kind": 30402, "content": "**Whole milk**", "tags": [
  ["d", "whole-milk"], ["title", "Whole milk"], ["type", "simple", "physical"],
  ["price", "0", "USD"],
  ["shipping_option", "30406:<merchant>:pickup"],
  ["a", "30405:<merchant>:milk"] ] }
```

The "Coffee" section lists the latte only. A customer sees one latte, "from $4.50", with its two sizes, a milk to pick with whole milk preselected, and up to three syrups.

## Compatibility

- Every tag this proposal adds is optional, and every listing is still valid without it.
- A reader that ignores `type` and `select` on a collection sees an ordinary collection of cheap products. It never offers them with a drink, and nothing breaks.
- A reader that ignores the link on an order line reads a valid order with the right total.
- The three readings under *Variations* add no tag. They only fix a meaning where the text was silent.

## Open questions

- Whether `select` should also carry a limit per modifier (four shots in total, but at most two of one kind). None of the cases above needs it.
- Whether `select` should be allowed on collections that are not modifier groups, for example a bundle where the customer picks any three for one price. This proposal leaves the tag free for that but does not define it.
- Whether one product may be both sold on its own and used as a modifier. This proposal says no, because then two collections own it and can disagree.
- Whether a modifier's price may depend on the size of the product it goes with. This proposal says no; a merchant that needs it publishes two modifiers.
