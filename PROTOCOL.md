# Protocol

## Interface

| Method | Caller | Result |
|---|---|---|
| `create(slug, product, units_json)` | Any sender | Immutable product and units; returns book ID |
| `link(book_id, expected_revision, source, target, statement)` | Book owner | Independent semantic consensus, deterministic graph update, complete book JSON |
| `freeze(book_id, expected_revision)` | Book owner | Immutable connected conversion table; complete book JSON |
| `get_book(book_id)` | Public | Complete book JSON, or empty string if absent |
| `convert(book_id, source, target, amount)` | Public | Exact rational amount and table hash; requires FROZEN |
| `protocol()` | Public | Version, semantic rules and limits as JSON |

`units_json` is one string containing a JSON array. Unit indices are zero-based. One FROM unit corresponds to `to_count / from_count` TO units. The model receives the declared product, the two labels and the statement, with no prior graph or leader result. Validators run the same interpretation independently. Their normalized status and exact reduced ratio must agree.

## States and outcomes

A book begins OPEN at revision zero. Every successful `link` adds one immutable attempt and advances the revision, including conflicts and unresolved findings. Connected books are READY; others remain OPEN. READY can become FROZEN, advancing the revision and permanently preventing writes.

| Outcome | Active graph effect | Evidence retained |
|---|---|---|
| LINKED | Join two disconnected components | Accepted equality and attempt index |
| REDUNDANT | None | Existing equal path |
| CONFLICT | None | Existing path, submitted ratio, exact cycle product |
| UNRESOLVED | None | Original statement and unresolved finding |

The active graph is a forest. Each successful link joins previously disconnected components, so it introduces no cycle. Between connected units the unique path implies one exact ratio. A conflicting closing edge is rejected from the active graph; the existing path plus the rejected equality form the contradiction witness. Its cycle product is the submitted ratio divided by the implied ratio and cannot equal one. Retaining a rejected attempt is a successful protocol write, not a reverted transaction or successful link.

A conflict does not repair or revoke prior declarations. The first accepted consistent links define the book. Use a new book for corrected specifications. Rejected or unresolved attempts remain visible after freezing, but are never table inputs. Freeze requires connectivity of every declared unit, not an empty rejection history.

## Exact conversion

Fractions are positive integer pairs reduced by GCD; no floating point is used. Accepted equality counts are 1–1,000,000. A path multiplies ratios and inverts them for reverse traversal. Freeze stores all ordered unit pairs, including the identity diagonal, and a SHA256 over the immutable scope hash and complete table.

`convert` accepts an integer amount from 0 through 10^12 and returns `numerator`, `denominator`, `whole_units`, `remainder_numerator` and `table_hash`. A quantity of 25 pieces at 24 pieces per case returns 25/24 cases, one whole case and a 1/24 remainder. This is mathematical equivalence; it does not claim the packages can physically be split or assembled. No ceil operation or charge is implied.

Canonical hashing uses sorted compact JSON, UTF-8 and `ensure_ascii=False`. Scope hashes bind protocol, product and ordered labels. Attempt hashes bind scope, directed endpoints and exact statement. Hashes identify declared bytes, not truth.

## Bounds and errors

12 books per owner; 2–6 labels of 2–40 characters; product 10–200 characters; 12 attempts per book; statements 20–800 characters. Slugs are 3–32 lowercase ASCII letters, digits or hyphens. Labels differing only by ASCII/Unicode lowercase conversion are rejected, but semantic alias detection is not provided.

Owner checks, exact revision guards, endpoint validity, size limits, attempt limits and duplicate input hashes are checked before model execution. Repeated inputs reject; an unsuccessful network transaction is not silently retried. Strict schema validation rejects booleans, floats, duplicate JSON keys and unknown fields. Malformed model output and runtime failures do not mutate the book. Counts for UNRESOLVED must be zero; uncertainty never supplies a conversion factor.

Views return JSON strings. Full-consensus network finalization is required before interpreting any saved result as authoritative.
