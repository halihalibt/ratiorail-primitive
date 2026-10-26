# RatioRail

A standalone GenLayer Intelligent Contract that turns natural-language **packaging equalities** into a consistent, exact conversion table for one declared product. Independent validators interpret each statement; deterministic rational arithmetic prevents contradictory declarations from changing the active conversion graph.

One case contains six boxes. One box contains four pieces. A later claim of twenty pieces per case must not silently replace twenty-four. RatioRail retains the conflicting declaration and its numerical cycle witness while preserving the existing conversion.

**Deployed:** [Stable Studionet contract](https://explorer-studio.genlayer.com/address/0x81E98E8162e8EB1E02ef11E2eF5ea7aA391a1dED). Six finalized successful transactions cover two accepted equalities, a blocked contradiction and a frozen exact table. [Inspect evidence](EVIDENCE.md).

## Mechanism

1. `create` fixes the product and 2–6 named units in the caller's namespace.
2. `link` asks the leader and validators to independently interpret a fixed equality between two units. Approximate, conditional or insufficient statements become `UNRESOLVED`.
3. Equivalence compares exact reduced rational values: “2 cases = 12 boxes” and “1 case = 6 boxes” agree; a reversed ratio does not. A model or schema failure does not become a valid business finding.
4. The contract links disconnected components, recognizes redundant equalities, or records a conflict against an existing path. A conflict includes the exact path and a non-unit cycle product.
5. Only a connected graph can be frozen. `freeze` publishes an immutable complete conversion table and hash. Public `convert` reads require no model, signer or transaction, and expose exact fractions rather than hiding rounding.

There is no administrator bypass, editable equality, frontend, token, price oracle or companion application. Source statements are caller declarations; consensus does not authenticate a supplier or a physical package.

## Developer use

Deploy [contracts/ratio_rail.py](contracts/ratio_rail.py) with no constructor arguments. Use Stable Studionet only: chain **61999**, RPC `https://studio.genlayer.com/api`. The Python runtime is pinned in the source header; call examples target `genlayer-js@1.1.8`.

[API and invariants](PROTOCOL.md) · [Design](DESIGN.md) · [Security and limitations](SECURITY.md) · [Synthetic fixture](examples/clips.json) · [Verification](EVIDENCE.md).

```sh
python -m unittest discover -s tests -v
npm ci
npm run verify:live
```

The Python tests use a scripted SDK/host and model outputs. They check graph, validation and state behavior; they are not real model or VM consensus evidence. The live verifier is read-only and checks the separate recorded deployment.

A record ID is `<lowercase-owner-address>:<slug>`. Unit positions are zero-based. Every write must finalize successfully before the next current revision is used; persist the returned hash and inspect it on timeout. Never resubmit an uncertain write automatically.

MIT licensed.
