# Unit tests + interchange-format comments for the blade coefficient dictionary

**Created:** 2026-06-13 · **Completed:** 2026-07-29

## Goal

The **blade coefficient dictionary** (`BladeCoef = dict[tuple[int, ...], Coef]`, produced/consumed
by `MultiVectorBase.to_blade_dict()` / `from_blade_dict()` in `src/gacalc/base.py`) is the
interchange format between all representations (`scalar`, `g1`, `g2`, `g3`, `gn` all convert
to/from it), and the shared arithmetic (add/sub, grade ops, `component`, coefficient maps) is built
on it. The task was to give it dedicated unit tests and comments stating that role. It was filed in
gacalc, not modelviewprojection, per the maintainer's decision: the blade dict lives here; mvp only
consumes gacalc's `Vector2`/`Vector3` via its `mathutils.py` façade.

## Outcome

Gate-verified: `make test` 311 passed; `check-generated`, `check-regions`, `format` all green.

- **Audit:** 37 incidental `to/from_blade_dict` uses across 7 test files (conversion helpers), but no
  dedicated interchange tests existed, so the task's premise held.
- **Tests:** new `tests/test_blade_dict.py` (9 tests) pins the contract: round-trip identity for all
  12 concrete representations, cross-representation dict preservation,
  arithmetic-through-interchange agreement, `()` = scalar blade, emitted keys always canonical
  (strictly increasing tuples), exact-zero omission + missing-reads-zero, the eager/lazy hidden-zero
  split (Gn prunes `cos²+sin²−1`, lazy keeps it un-reduced), the graded silent-drop contract (the
  `exp()` trap), and lazy coefficient-type preservation (float stays float).
- **Docs:** the authoritative format note lives at `BladeCoef` in `base.py` (canonical keys, zero
  conventions, graded silent-drop, the dispatching-arithmetic rule); `MultiVectorBase`'s docstring
  names the blade dict as THE canonical interchange; README's Layout section got a short pointer
  paragraph.
- **Decisions** (per the approved pitch, 2026-07-29): coverage target = round-trip +
  cross-representation + ALL canonical-form invariants; comment scope = `base.py` + a README line.

## Finding for the maintainer: non-canonical input keys

**Non-canonical input keys were undefined behavior with DIVERGENT failure modes** (measured):
`Gn.from_blade_dict({(2, 1): 5})` stored the key raw (the value then compared unequal to `-5·e₁₂`:
not a signed permutation, just broken), while `G2.from_blade_dict({(2, 1): 5})` silently dropped it.
This was documented as a writer-side precondition at `BladeCoef` and deliberately NOT test-frozen
(the behaviors were accidents). The options were (a) raise on non-canonical keys (cheaper, catches
bugs) or (b) canonicalize them (sort + sign flip + merge duplicates; friendlier). It was promoted,
**decided (a) raise, and done the same day**: `tasks/archive/2026/07/29/validate-blade-dict-keys.md`
(which includes a plain-terms explanation of canonical keys).
