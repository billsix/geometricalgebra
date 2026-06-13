# Unit tests + interchange-format comments for the blade coefficient dictionary

**Status:** proposed — not started
**Created:** 2026-06-13

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
