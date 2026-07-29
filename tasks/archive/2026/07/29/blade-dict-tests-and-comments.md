# Unit tests + interchange-format comments for the blade coefficient dictionary

**Status:** DONE 2026-07-29 — implemented and gate-verified (`make test` 311 passed,
`check-generated`, `check-regions`, `format` all green); archived.
**Created:** 2026-06-13

## Outcome

- **Audit:** 37 incidental `to/from_blade_dict` uses across 7 test files (conversion
  helpers), but no dedicated interchange tests existed — the task's premise held.
- **Tests:** new `tests/test_blade_dict.py` (9 tests) pins the contract: round-trip
  identity for all 12 concrete representations, cross-representation dict
  preservation, arithmetic-through-interchange agreement, `()` = scalar blade,
  emitted keys always canonical (strictly increasing tuples), exact-zero omission +
  missing-reads-zero, the eager/lazy hidden-zero split (Gn prunes `cos²+sin²−1`,
  lazy keeps it un-reduced), the graded silent-drop contract (the `exp()` trap),
  and lazy coefficient-type preservation (float stays float).
- **Docs:** the authoritative format note now lives at `BladeCoef` in `base.py`
  (canonical keys, zero conventions, graded silent-drop, the dispatching-arithmetic
  rule); `MultiVectorBase`'s docstring names the blade dict as THE canonical
  interchange; README's Layout section got a short pointer paragraph.
- **Open questions answered** (per the approved pitch, 2026-07-29): coverage target
  = round-trip + cross-representation + ALL canonical-form invariants; comment
  scope = `base.py` + README line.

## Finding for Bill — possible follow-up (not implemented)

**Non-canonical input keys are undefined behavior with DIVERGENT failure modes**
(measured): `Gn.from_blade_dict({(2, 1): 5})` stores the key raw (and the value
then compares unequal to `-5·e₁₂` — not a signed permutation, just broken), while
`G2.from_blade_dict({(2, 1): 5})` silently drops it. Documented as a writer-side
precondition at `BladeCoef` and deliberately NOT test-frozen (the behaviors are
accidents). If wanted, a follow-up could make `from_blade_dict` either **(a)
raise** on non-canonical keys or **(b) canonicalize** them (sort + sign flip +
merge duplicates); (a) is cheaper and catches bugs, (b) is friendlier input
handling. **Promoted to `tasks/validate-blade-dict-keys.md`** (with a plain-terms
explanation of what canonical keys are), awaiting Bill's (a)/(b) decision.

## Goal

The **blade coefficient dictionary** (`BladeCoef = dict[tuple[int, ...], Coef]`,
produced/consumed by `MultiVectorBase.to_blade_dict()` / `from_blade_dict()` in
`src/gacalc/base.py`) is the central data structure of the library: it's the
**interchange format between all representations** — `scalar`, `g1`, `g2`, `g3`,
and `gn` all convert to/from it, and the shared arithmetic (add/sub, grade ops,
`component`, coefficient maps) is built on top of it. Given how important it is:

1. **Make sure there are dedicated unit tests** for the blade-dict interchange.
2. **Add comments** that explicitly state it is *the* interchange format between
   all the multivector types — so a reader immediately understands its role.

## Plan

- [ ] **Audit existing coverage.** See what `tests/test_multivector.py`,
      `test_graded.py`, and `test_conformance.py` already exercise around
      `to_blade_dict`/`from_blade_dict` and cross-representation conversion; list
      the gaps. (There's a suite already — this likely augments, not creates.)
- [ ] **Add interchange unit tests:**
      - *Round-trip identity:* `from_blade_dict(x.to_blade_dict()) == x` for each
        representation (scalar, G2, G3, Gn).
      - *Cross-representation:* `Gn → blade dict → G2/G3` (and back) preserves
        coefficients; arithmetic routed through the interchange (e.g. `add`) agrees
        across representations.
      - *Canonical form / invariants:* blade keys are sorted index tuples, the
        empty tuple `()` is the scalar blade, zero/missing coefficients behave
        consistently (`.get(blade, 0)`), and unsorted/duplicate input keys are
        handled.
      - *Coef type:* round-trips hold for both sympy and float coefficient types
        (representations differ on eager simplification).
- [ ] **Strengthen the comments/docs.** `MultiVectorBase`'s docstring already calls
      it a "tiny interchange protocol" — make it explicit that the blade dict is
      **the canonical interchange representation that every type converts through
      and that all shared arithmetic routes through**, and document the key format
      (sorted tuple of basis-vector indices; `()` = scalar) and the `Coef` type.
      Put the authoritative note on `BladeCoef` / `MultiVectorBase` in `base.py`,
      and consider a line in the README.
- [ ] **Run the suite** (in the container) to confirm green.

## Notes / decisions

- Key references in `src/gacalc/base.py`: `BladeCoef` type (line ~38);
  `from_blade_dict`/`to_blade_dict` abstract methods (~94/98); shared arithmetic
  built on the interchange (~197+); `component`/grade helpers also go through
  `to_blade_dict()`.
- Filed in **gacalc** (not modelviewprojection) per Bill's decision — the blade
  dict lives here; mvp only consumes gacalc's `Vector2`/`Vector3` via the
  `mathutils.py` façade and has no blade dict of its own.
- gacalc follows the standard `tasks/` convention (this repo already has `tasks/`
  + `tasks/archive/`).

## Open questions

- Coverage target: round-trip + cross-representation only, or also the
  canonical-form invariants (sorted keys, zero pruning, scalar = `()`)?
- Comment scope: just `base.py` (`BladeCoef` + `MultiVectorBase`), or also a short
  "interchange format" subsection in the README?
