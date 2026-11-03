# Commerce testing examples

Status: **Experimental**, derived from the proposed
[commerce testing profile](../../proposals/commerce-testing.md), not current
normative Open Markets behavior.

`cases.json` is a machine-readable set of synthetic policy scenarios. Each
case supplies named observations and expected outcomes. Observation values
such as `authenticated: true` are assumptions for the scenario, not results
of cryptographic verification. Symbolic resources and actors are not on-wire
identifiers, pubkeys, or credentials.

The proposal also includes parseable JSON fragments for a listing template,
decoded private order, canonical label pair, and public discovery filter.
They are deliberately incomplete, unsigned artifacts; do not publish them as
events or interpret the order fragment as an encryption test vector.

## Using the scenarios

An implementation should translate the named observations into its own
authenticated events, configured test participants, and persisted transaction
state, then check each expected outcome. Include assertions that the relevant
live resources and side-effect boundaries remain untouched.

The repeated-delivery, restart, and roster-removal cases require stateful
testing. Privacy and payment-provider cases require inspection at the actual
encryption and wallet boundaries. Do not substitute the booleans in this file
for those checks or claim these scenarios prove signing, encryption, safe
provider selection, or relay interoperability.

## Evidence status

These examples define proposed expectations only. JSON parsing, internal
consistency, and documentation checks can be performed locally without any
network writes. Client implementations and a two-client relay trial remain
unperformed acceptance work, not a prerequisite for opening this draft.
