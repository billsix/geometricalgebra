# Type-annotation audit: sweep all Python, list where types should be added

**Created:** 2026-09-05 · **Completed:** 2026-09-09

## Goal

Every hand-written Python file was swept for places a type annotation should be added or tightened,
against `CLAUDE.md`'s "Type annotations — annotate generously" rule (signatures always; locals as
much as reasonable; loop/unpack targets declared on the line above; parameterize generics; read-only
container params take `Mapping`/`Sequence`; don't fight the checker; inline a single-use value rather
than keep it only to type it). The maintainer wanted more types, not fewer. This was the sibling of
the conditional-refactor sweep (`tasks/archive/2026/09/05/refactor-conditionals-match-and-ternary-returns.md`),
with the same never-churn, per-batch-gated discipline. Excluded: the generated `g1`–`g3` (annotated
via the generator) and the vendored `entrypoint/` Emacs tree.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-09-05)

1. **Scope: all four** — `src/` + `tools/` + `tests/` + `notebooks/`, not `tasks/` ("all four, just
   not tasks").
2. **Apply, not list-only** ("just do them all"), gated per batch.
3. **Add and tighten everything** ("everything you can find"): missing annotations plus loose
   generics, `Any`, and invariant containers.

## What the sweep found

An AST auditor written for the job counted 359 rows at the start and **29** at the end, every one a
deliberate exemption catalogued with its reason in `tasks/reference/type-annotation-exemptions.md`.

| Kind | Start | Fixed | Left | The remainder |
|---|---|---|---|---|
| Missing param | 32 | 31 | 1 | one dimension-defaulting test |
| Missing return | 4 | 2 | 2 | `base.__iter__`, `test_conformance.to` |
| Invariant container param | 17 | 15 | 3 | two out-params, one the stdlib pins |
| Unannotated local | 224 | 221 | 3 | three that lose information when declared |
| Unannotated loop target | 73 | 72 | 1 | derived from one of those three |
| `Any` in an annotation | 9 | 0 | 9 | the documented polymorphic-transform case |

Aliases, `TypeVar`s, `Enum` members and `_` discards were reclassified out of the count. The auditor
was promoted to `tools/check_annotations.py` so the check can be re-run; it is informational only,
not wired into a `make` gate (the maintainer's call).

### Lessons

- **Two documented "we don't annotate these" claims were broader than the facts.** The parametrized
  `cls` params in `tests/test_conformance.py` were said to be deliberately inferred; annotating all 22
  broke exactly one test, so 21 were typed and the stale claim was corrected in place.
- **`ty` does not see the notebooks**, which hid real errors: the first notebook pass was ruff- and
  ty-clean while introducing 22 pyright errors (a wrong `MultiVectorFn` alias, and
  `InvertibleFunction[Vector]` where `[G]` was meant). Only the in-container `pyright notebooks` run
  caught them, against a baseline of 1 pre-existing error — so 23 was a regression, not a discovery.
- **The transform generics are invariant**, so there is no blanket annotation: each site takes the
  exact representation it is built over, and `compose` yields `ComposableFunction` rather than
  `InvertibleFunction` wherever a part has no inverse.
- **Every "don't fight the checker" exemption traces to one root cause**: the abstract
  `MultiVectorBase` is less capable than its concrete subclasses, because the dimension-defaulting
  overrides drop a required `n`.
- **`tools/bench.py`'s `sa`/`sb`** carried a note that they were reused at a different type and had
  to stay inferred; `CLAUDE.md`'s rule is to split them into distinctly named typed variables, which
  was done and verified by running the benchmark.

## Verification

`make format`, `make test`, `make check-generated` and `make check-regions` green; in-container
`pyright notebooks` went from 1 pre-existing error to 0.
