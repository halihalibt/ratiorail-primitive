# Verification

## Network and source

- Stable Studionet, chain **61999**, `https://studio.genlayer.com/api`.
- [Contract 0x81E98E8162e8EB1E02ef11E2eF5ea7aA391a1dED](https://explorer-studio.genlayer.com/address/0x81E98E8162e8EB1E02ef11E2eF5ea7aA391a1dED).
- Source SHA256: `52ff676a63628d504dc9639bb07f136385ddd6765bf1d82002130811e898e5fd`.
- [Source checkpoint](https://github.com/halihalibt/ratiorail-primitive/commit/bb99f5e5ec0f2a000e3d87968683ca9dcb6015b1).
- Official RPC [preflight](evidence/preflight.json): chain 61999, gas price zero, complete contract schema accepted. Client: `genlayer-js@1.1.8`; Python dependency pinned in the source header.
- [Deployment manifest](deployment.json), [final frozen book](evidence/final-book.json), [read-only verification output](evidence/live-verification.txt).

The deployment and lifecycle used a fresh development account, zero transfer value and zero gas price, without paid APIs or funding. It is not presented as the repository owner's everyday wallet. No external-wallet key or seed phrase was supplied. Only Stable Studionet was used; no Appeal or client retransmission occurred.

## Finalized lifecycle

All six receipts are **FINALIZED / MAJORITY_AGREE**, successful leader execution (`return`), Normal mode, `leader_only=false`. The conflict is a successfully recorded **rejected graph edge**, not a reverted transaction or an accepted conversion factor.

| Step | Explorer | RPC projection |
|---|---|---|
| Deploy | [Transaction](https://explorer-studio.genlayer.com/tx/0x073bda60bc8cc74098f8495bfa62b5a7e2a7aabf8788461c8e91e9a01390976d) | [Receipt](evidence/receipt-deployment.json) |
| Create book | [Transaction](https://explorer-studio.genlayer.com/tx/0xfaef67c2301f56b30967c7be5ef21fbd29f0d87508531ec82faf1ef2cbe1ade5) | [Receipt](evidence/receipt-create.json) |
| LINKED: 1 case = 6 boxes | [Transaction](https://explorer-studio.genlayer.com/tx/0xf649901c9a434eb7c4ace1e03f9a1108e9adcff6329c99345af24d5551b839a3) | [Receipt](evidence/receipt-link0.json) |
| LINKED: 1 box = 4 pieces | [Transaction](https://explorer-studio.genlayer.com/tx/0x550f1282a7736b561d5ac133b5f035d8eb0d0e9f9bc6983cf90ea219f3fdb0ed) | [Receipt](evidence/receipt-link1.json) |
| CONFLICT: 20 versus 24 pieces per case | [Transaction](https://explorer-studio.genlayer.com/tx/0x785c419043d4b222be73e7c77233a81d47cdfc531af0533683221f3d009a4582) | [Receipt](evidence/receipt-link2.json) |
| FROZEN, revision 4 | [Transaction](https://explorer-studio.genlayer.com/tx/0xbf8fe9f833af98820041f6eb8c15f63d6da826c6b7774b04a6b348bb6b9bba96) | [Receipt](evidence/receipt-freeze.json) |

The fixture is a **synthetic packaging specification**, not an authenticated supplier statement. Two consensus-interpreted links imply 24 pieces per case. The third model assessment independently extracts the declared 20; deterministic code excludes it and records the path through attempts 0 and 1, an implied ratio of 24/1, and a cycle product of 5/6. The active forest remains unchanged. The connected book then freezes with the full 3×3 conversion table.

A finalized read of `convert(book_id, 2, 0, 25)` returns **25/24 cases**, one whole case and a 1/24 remainder, bound to the frozen table hash. This read sends no transaction and invokes no model.

## Observed voting

These are final-round vote counts, not claims about independent real-world operators. IDLE votes do not establish successful semantic replay. Round history and VM diagnostics remain in each receipt projection.

| Step | AGREE | DISAGREE | IDLE | Network rounds | Leader rotations |
|---|---|---|---|---|---|
| deployment | 3 | 0 | 2 | 1 | 0 |
| create | 5 | 0 | 0 | 1 | 0 |
| link0 | 3 | 0 | 2 | 1 | 0 |
| link1 | 3 | 0 | 2 | 1 | 0 |
| link2 | 3 | 0 | 2 | 1 | 0 |
| freeze | 3 | 0 | 2 | 1 | 0 |

`receipt-*.json` preserves exact RPC fields for identity, calldata, results, votes and every reported consensus round; repeated source encodings, raw byte arrays and provider configuration are omitted. Step JSON files retain the actual arguments and finalized state readbacks. Explorer links allow independent retrieval.

## Offline scope and remaining limits

**18 scripted Python tests passed on 2026-10-26.** They exercise rational equivalence, reverse/transitive paths, conflict certificates, malformed/error/disagreement rollback, ownership, revision and duplicate guards, disconnected freeze rejection, terminal freezing, conversion fractions, and bounds. [Recorded scope](evidence/offline.json).

The test host and model are scripted; these are not real VM or semantic accuracy measurements. Live evidence covers two accepted equalities, a transitive contradiction and terminal publication. UNRESOLVED, proportional-count equivalence, redundant edges, prompt injection and unauthorized-write rejection have not received separate live-network control transactions. Source authenticity and model interpretation remain limitations.

## Recheck without writes

```sh
npm ci
npm run verify:live
```

The verifier has no account or signer. It checks the exact deployed bytes, protocol, all six finalized receipts and full-consensus mode, actual sender/recipient and calldata, fixture inputs and hashes, active forest, conflict witness, complete frozen table, table hash and exact fractional conversion. It sends no transactions.

Official references: [networks](https://docs.genlayer.com/developers/networks), [custom equivalence](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle).
