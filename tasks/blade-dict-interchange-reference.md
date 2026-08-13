# Reference doc: the blade-dict interchange contract

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-08-13
**Origin:** the 2026-08-13 archive gap-analysis sweep — pulled out of Group A into its
own task because the interchange is core enough to deserve a standing reference doc, not a
one-line harvest. Siblings: the four `harvest-*` group tasks.

## Goal

Create `tasks/reference/blade-dict-interchange.md` — a standing reference for `BladeCoef`
(`dict[blade, coef]`), THE canonical interchange format every representation (`Gn`,
`G1`/`G2`/`G3`, and the graded subtypes) converts through via `to_blade_dict` /
`from_blade_dict`, and which all shared arithmetic in `base.py` routes through. The full
contract lives only in `base.py`'s `BladeCoef` docstring today; the harvest docs
(`design-decisions.md`, CLAUDE.md) don't consolidate it in one place.

## What the doc should capture

- **Canonical keys.** Strictly-increasing index tuples; `()` is the scalar blade.
  `from_blade_dict` (every representation, via the shared `_require_canonical_blades`
  helper) **raises `ValueError`** on a non-canonical key (`(2, 1)`, duplicates) — a
  deliberate *raise-over-canonicalize* decision: `from_blade_dict` is an
  interchange/constructor primitive, not user sugar, so loud rejection fits. It replaced
  two *silent* wrong answers (`Gn` stored the bad key raw → corrupt; the graded/full
  classes silently dropped it). (`e₂e₁` is a legal algebra *element* but not a legal
  *key* — it equals `−e₁e₂`, belonging under key `(1,2)` with the sign folded in.)
- **Zero handling.** Readers omit exact-zero coefficients; a missing blade reads as 0
  (`.get(blade, 0)`).
- **The eager/lazy "hidden zero" split.** `Gn` eager-simplifies, so a hidden zero
  (`cos²+sin²−1`) is pruned; the lazy classes keep a structural `0` only, so they can
  carry an un-reduced coefficient.
- **The graded silent-drop rule (the "exp() trap").** A graded type's `from_blade_dict`
  keeps only its own blades — foreign keys are silently dropped — so a result carrying a
  new grade must be built via dispatching arithmetic (`Bivector + scalar → Rotor`), never
  via `from_blade_dict` on the operand's type.

## Sources

- `base.py` — the `BladeCoef` docstring + `_require_canonical_blades` (primary, authoritative).
- `tasks/archive/2026/07/29/validate-blade-dict-keys.md` (the raise-vs-canonicalize decision).
- `tasks/archive/2026/07/29/blade-dict-tests-and-comments.md` (the consolidated contract, tests).

## Notes

- **Verify every claim against current `base.py` before writing** (reference-doc discipline).
- Cross-link from CLAUDE.md's interchange note and `design-decisions.md`.
