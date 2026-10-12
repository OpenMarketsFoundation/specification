#!/usr/bin/env python3
"""Check experimental schemas and synthetic semantic vectors, not cryptography.

The fixture verification set represents a caller's independently established
rail-verification result. It never verifies an invoice, signature or payment.
"""

import hashlib
import json
import re
from decimal import Decimal, getcontext
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "proposals/private-commerce/v1"
HEX = re.compile(r"^[0-9a-f]{64}$")
ID = re.compile(r"^[0-9a-f]{32}$")
# Each operand has at most 96 characters and each list at most 256 entries.
# Preserve full decimal precision across sums and charge/credit cancellation.
getcontext().prec = 256


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON property")
        result[key] = value
    return result


def load_json(value):
    return json.loads(value, object_pairs_hook=strict_object,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Non-finite JSON")))


def event_hash(message):
    serialized = [0, message["pubkey"], message["created_at"],
                  message["kind"], message["tags"], message["content"]]
    return hashlib.sha256(json.dumps(serialized, separators=(",", ":"),
                                    ensure_ascii=False).encode()).hexdigest()


class Invalid(Exception):
    pass


class Deferred(Exception):
    pass


class Unsupported(Exception):
    pass


class ReferenceModel:
    """Small sequence oracle for the rules documented in the proposal kit.

    Production callers still own transport authentication, signed listing
    validation, durable transactions, payment verification and rollout.
    """

    def __init__(self, validator, fixture):
        self.validator = validator
        self.verified = set(fixture["verified_operations"])
        self.extensions = set(fixture["supported_extensions"])
        self.records = {}
        self.payments = {}
        self.refunds = {}
        self.fulfillments = {}
        self.fulfillment_heads = {}
        self.completed_groups = set()
        self.shipping_heads = {}
        self.delivered_groups = set()

    def reference(self, operation, current, allowed):
        if operation == current["operation"]:
            raise Invalid()
        record = self.records.get(operation)
        if record is None:
            raise Deferred()
        if record["scope"] != current["scope"] or record["type"] not in allowed:
            raise Invalid()
        return record

    def order(self, operation, current):
        record = self.reference(operation, current, {"order", "order_accepted"})
        if record["type"] == "order_accepted":
            return self.reference(record["payload"]["order_operation"], current, {"order"})
        return record

    def money_matches(self, amount, reference):
        if amount["unit"] != reference["unit"]:
            raise Invalid()
        value = Decimal(amount["value"])
        precision = {"SAT": 0, "MSAT": 0, "BTC": 8, "USD": 2, "EUR": 2}
        if amount["unit"] not in precision:
            raise Unsupported()
        if max(0, -value.as_tuple().exponent) > precision[amount["unit"]]:
            raise Invalid()
        return value

    def accept(self, message):
        try:
            if set(message) != {"id", "pubkey", "created_at", "kind", "tags", "content"}:
                raise Invalid()
            if not HEX.fullmatch(message["id"]) or not HEX.fullmatch(message["pubkey"]):
                raise Invalid()
            if type(message["created_at"]) is not int or not 0 <= message["created_at"] <= 9007199254740991:
                raise Invalid()
            if type(message["kind"]) is not int or message["kind"] != 1327 or message["id"] != event_hash(message):
                raise Invalid()
            tags = message["tags"]
            if not isinstance(tags, list) or any(not isinstance(t, list) or
                    len(t) < 2 or any(not isinstance(v, str) for v in t) for t in tags):
                raise Invalid()
            singleton = {}
            for key in ("conversation", "order", "operation", "type", "version"):
                matches = [t for t in tags if t[0] == key]
                if len(matches) != 1 or len(matches[0]) != 2 or not matches[0][1]:
                    raise Invalid()
                singleton[key] = matches[0][1]
            if any(len(singleton[k]) > 128 for k in ("conversation", "order", "type")):
                raise Invalid()
            if not ID.fullmatch(singleton["operation"]):
                raise Invalid()
            recipients = [t for t in tags if t[0] == "p"]
            if len(recipients) != 1 or len(recipients[0]) not in (2, 3) or not HEX.fullmatch(recipients[0][1]):
                raise Invalid()
            payload = load_json(message["content"])
            if not isinstance(payload, dict):
                raise Invalid()
            name = singleton["type"]
            known_types = {branch["properties"]["type"]["const"] for branch in self.validator.schema["oneOf"]}
            if singleton["version"] != "1" or name not in known_types:
                return "unsupported"
            if not self.validator.is_valid({"type": name, "payload": payload}):
                raise Invalid()
            required = set(payload.get("requires", []))
            if not required <= set(payload.get("extensions", {})):
                raise Invalid()
            if not required <= self.extensions:
                return "unsupported"
            # One deliberately trivial fixture extension has an exact schema;
            # advertising its name alone cannot validate arbitrary payloads.
            if "example:terms" in required and payload["extensions"]["example:terms"] != {"x": 1}:
                raise Invalid()
            operation = singleton["operation"]
            record = {"scope": (singleton["conversation"], singleton["order"],
                                tuple(sorted((message["pubkey"], recipients[0][1])))),
                      "operation": operation,
                      "type": name, "author": message["pubkey"], "recipient": recipients[0][1],
                      "payload": payload, "event_id": message["id"]}
            old = self.records.get(operation)
            if old:
                meaning = lambda r: {k: v for k, v in r.items() if k != "event_id"}
                return "duplicate" if meaning(old) == meaning(record) else "conflict"
            order = None
            if name == "order":
                if payload["buyer"] != record["author"] or payload["merchant"] != record["recipient"]:
                    raise Invalid()
                if payload["buyer"] == payload["merchant"]:
                    raise Invalid()
                total = Decimal(payload["total"]["value"])
                expected = Decimal(0)
                line_ids = set()
                for item in payload["items"]:
                    if item["line_id"] in line_ids or item["listing"]["coordinate"].split(":", 2)[1] != payload["merchant"]:
                        raise Invalid()
                    quantity = Decimal(item["quantity"])
                    if item["unit"] != "item":
                        raise Unsupported()
                    if item["unit"] == "item" and quantity != quantity.to_integral_value():
                        raise Invalid()
                    line_ids.add(item["line_id"])
                    expected += self.money_matches(item["amount"], payload["total"])
                adjustment_ids = set()
                for adjustment in payload.get("adjustments", []):
                    if adjustment["adjustment_id"] in adjustment_ids:
                        raise Invalid()
                    adjustment_ids.add(adjustment["adjustment_id"])
                    amount = self.money_matches(adjustment["amount"], payload["total"])
                    expected += amount if adjustment["direction"] == "charge" else -amount
                if total != expected or total < 0:
                    raise Invalid()
                delivered, delivery_ids = set(), set()
                for delivery in payload.get("deliveries", []):
                    members = set(delivery["line_ids"])
                    if delivery["delivery_id"] in delivery_ids or not members <= line_ids or members & delivered:
                        raise Invalid()
                    option = delivery.get("shipping_option")
                    if option and option["coordinate"].split(":", 2)[1] != payload["merchant"]:
                        raise Invalid()
                    delivery_ids.add(delivery["delivery_id"])
                    delivered |= members
                if "supersedes" in payload:
                    previous = self.reference(payload["supersedes"], record, {"order"})
                    if previous["author"] != record["author"]:
                        raise Invalid()
            elif name in {"order_accepted", "order_cancel_requested", "order_cancelled", "fulfillment_update"}:
                order = self.reference(payload["order_operation"], record, {"order"})
                if name == "order_cancelled" and "request" in payload:
                    cancellation = self.reference(payload["request"], record, {"order_cancel_requested"})
                    if cancellation["payload"]["order_operation"] != payload["order_operation"]:
                        raise Invalid()
            elif name == "payment_request":
                order = self.order(payload["terms"], record)
                amount = self.money_matches(payload["amount"], order["payload"]["total"])
                if amount <= 0 or amount > Decimal(order["payload"]["total"]["value"]):
                    raise Invalid()
            elif name in {"payment_proof", "payment_confirmed", "payment_rejected"}:
                request = self.reference(payload["request"], record, {"payment_request"})
                order = self.order(request["payload"]["terms"], record)
                proof = None
                if "proof_operation" in payload:
                    proof = self.reference(payload["proof_operation"], record, {"payment_proof"})
                    if proof["payload"]["request"] != payload["request"]:
                        raise Invalid()
                if "amount" in payload:
                    amount = self.money_matches(payload["amount"], request["payload"]["amount"])
                    if amount <= 0 or amount > Decimal(request["payload"]["amount"]["value"]):
                        raise Invalid()
                    evidence = payload["evidence"]
                    if not any(evidence["rail"] == method["rail"] and evidence["reference"] == method["reference"] for method in request["payload"]["methods"]):
                        raise Invalid()
                    if proof and any(proof["payload"][k] != payload[k] for k in ("payment_id", "amount")):
                        raise Invalid()
            elif name in {"refund_requested", "refund_confirmed"}:
                confirmation = self.reference(payload["payment_confirmation"], record, {"payment_confirmed"})
                request = self.reference(confirmation["payload"]["request"], record, {"payment_request"})
                order = self.order(request["payload"]["terms"], record)
                amount = self.money_matches(payload["amount"], confirmation["payload"]["amount"])
                if amount <= 0 or amount > Decimal(confirmation["payload"]["amount"]["value"]):
                    raise Invalid()
            elif name == "shipping_update":
                fulfillment = self.reference(payload["fulfillment_operation"], record, {"fulfillment_update"})
                order = self.order(fulfillment["payload"]["order_operation"], record)
            if order:
                parties = order["payload"]
                expected_author = parties["buyer"] if name == "payment_proof" else parties["merchant"]
                if name in {"order_cancel_requested", "refund_requested"}:
                    if record["author"] not in {parties["buyer"], parties["merchant"]}:
                        raise Invalid()
                elif record["author"] != expected_author:
                    raise Invalid()
                expected_recipient = parties["merchant"] if record["author"] == parties["buyer"] else parties["buyer"]
                if record["recipient"] != expected_recipient:
                    raise Invalid()
            if name in {"payment_confirmed", "refund_confirmed"}:
                if operation not in self.verified:
                    raise Deferred()
                ledger = self.payments if name == "payment_confirmed" else self.refunds
                identity = (record["scope"], payload["evidence"]["rail"],
                            payload.get("payment_id", payload.get("refund_id")))
                previous = ledger.get(identity)
                if previous:
                    if previous != payload:
                        return "conflict"
                    self.records[operation] = record
                    return "duplicate"
                if name == "payment_confirmed":
                    request_total = sum(Decimal(p["amount"]["value"]) for p in self.payments.values() if p["request"] == payload["request"])
                    if request_total + amount > Decimal(request["payload"]["amount"]["value"]):
                        raise Invalid()
                    order_total = sum(Decimal(p["amount"]["value"]) for (scope, _, _), p in self.payments.items() if scope == record["scope"])
                    if order_total + amount > Decimal(order["payload"]["total"]["value"]):
                        raise Invalid()
                else:
                    refunded = sum(Decimal(p["amount"]["value"]) for p in self.refunds.values() if p["payment_confirmation"] == payload["payment_confirmation"])
                    if refunded + amount > Decimal(confirmation["payload"]["amount"]["value"]):
                        raise Invalid()
                    if "request" in payload:
                        refund_request = self.reference(payload["request"], record, {"refund_requested"})
                        if refund_request["payload"]["payment_confirmation"] != payload["payment_confirmation"] or refund_request["payload"]["amount"] != payload["amount"]:
                            raise Invalid()
                ledger[identity] = payload
            if name == "fulfillment_update":
                line_quantities = {i["line_id"]: Decimal(i["quantity"]) for i in order["payload"]["items"]}
                group = (record["scope"], payload["fulfillment_id"])
                previous = payload.get("previous")
                if previous:
                    predecessor = self.reference(previous, record, {"fulfillment_update"})
                    if predecessor["payload"]["fulfillment_id"] != payload["fulfillment_id"]:
                        raise Invalid()
                if group in self.fulfillment_heads and previous != self.fulfillment_heads[group]:
                    if previous is None:
                        raise Invalid()
                    return "conflict"
                if group in self.completed_groups and payload["state"] not in {"completed", "exception"}:
                    raise Invalid()
                if group in self.fulfillments and self.fulfillments[group] != payload["items"]:
                    raise Invalid()
                prospective = {**self.fulfillments, group: payload["items"]}
                allocated = {}
                for (scope, _), items in prospective.items():
                    if scope == record["scope"]:
                        seen = set()
                        for item in items:
                            if item["line_id"] in seen or item["line_id"] not in line_quantities:
                                raise Invalid()
                            seen.add(item["line_id"])
                            allocated[item["line_id"]] = allocated.get(item["line_id"], Decimal(0)) + Decimal(item["quantity"])
                if any(value > line_quantities[key] for key, value in allocated.items()):
                    raise Invalid()
                accepted = any(r["scope"] == record["scope"] and r["type"] in {"order_accepted", "payment_confirmed"} for r in self.records.values())
                if not accepted:
                    raise Deferred()
                self.fulfillments[group] = payload["items"]
                self.fulfillment_heads[group] = operation
                if payload["state"] == "completed":
                    self.completed_groups.add(group)
            if name == "shipping_update":
                group = (record["scope"], fulfillment["payload"]["fulfillment_id"])
                previous = payload.get("previous")
                if previous:
                    predecessor = self.reference(previous, record, {"shipping_update"})
                    prior_fulfillment = self.reference(predecessor["payload"]["fulfillment_operation"], record, {"fulfillment_update"})
                    if prior_fulfillment["payload"]["fulfillment_id"] != fulfillment["payload"]["fulfillment_id"]:
                        raise Invalid()
                if group in self.shipping_heads and previous != self.shipping_heads[group]:
                    if previous is None:
                        raise Invalid()
                    return "conflict"
                if group in self.delivered_groups and payload["state"] not in {"delivered", "exception"}:
                    raise Invalid()
                self.shipping_heads[group] = operation
                if payload["state"] == "delivered":
                    self.delivered_groups.add(group)
            self.records[operation] = record
            return "accepted"
        except Deferred:
            return "deferred"
        except Unsupported:
            return "unsupported"
        except (Invalid, ValueError, TypeError, KeyError, AttributeError):
            return "rejected"


def classify_legacy_fixture(rumor):
    """Classify these vectors; intentionally grant no financial authority.

    This is not a full legacy payload validator or an application schema.
    """
    tags = rumor.get("tags", [])
    values = lambda key: [t[1] for t in tags if len(t) >= 2 and t[0] == key]
    result = {"category": "unrelated", "type": None, "financial_effect": "none"}
    if not values("order"):
        return result
    if len(values("order")) != 1 or len(values("p")) != 1:
        return {**result, "category": "malformed"}
    if rumor["kind"] == 17 and values("payment") and values("amount"):
        return {**result, "category": "open_markets", "type": "payment_proof"}
    types = values("type")
    if rumor["kind"] != 16:
        return result
    if len(types) != 1:
        return {**result, "category": "malformed"}
    numeric = {"1": "order", "2": "payment_request", "3": "status_update", "4": "shipping_update"}
    if types[0] in numeric:
        return {**result, "category": "open_markets", "type": numeric[types[0]]}
    if types[0] in {"order", "payment_request", "payment_proof", "status_update", "shipping_update", "receipt"}:
        try:
            if isinstance(load_json(rumor["content"]), dict):
                return {**result, "category": "application_schema_required", "type": types[0]}
        except (ValueError, TypeError):
            pass
    return {**result, "category": "malformed"}


def main():
    schema = load_json((KIT / "message.schema.json").read_text())
    caps = load_json((KIT / "capabilities.schema.json").read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator.check_schema(caps)
    validator, cap_validator = Draft202012Validator(schema), Draft202012Validator(caps)
    fixtures = load_json((KIT / "fixtures.json").read_text())
    count = 0
    for case in fixtures["payload_cases"]:
        assert validator.is_valid(case["message"]) == case["valid"], case["name"]
        count += 1
    for case in fixtures["capability_cases"]:
        assert cap_validator.is_valid(case["content"]) == case["valid"], case["name"]
        count += 1
    for case in fixtures["sequence_cases"]:
        model = ReferenceModel(validator, case)
        actual = [model.accept(fixtures["messages"][key]) for key in case["messages"]]
        assert actual == case["expected"], (case["name"], actual, case["expected"])
        if case["name"] == "proof-does-not-confirm-payment":
            assert not model.payments
        if case["name"] == "partial-payment-not-full":
            assert sum(Decimal(p["amount"]["value"]) for p in model.payments.values()) == Decimal(400)
        count += 1
    legacy = load_json((KIT / "legacy-fixtures.json").read_text())
    for case in legacy["cases"]:
        assert classify_legacy_fixture(case["rumor"]) == case["expected"], case["name"]
        count += 1
    print(f"PASS: 2 Draft 2020-12 schemas; {count} synthetic payload/capability/sequence cases")
    print("Scope: schema, hash and reference semantics only; no cryptographic, relay or real-payment certification")


if __name__ == "__main__":
    main()
