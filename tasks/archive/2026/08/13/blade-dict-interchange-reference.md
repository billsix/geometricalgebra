# Reference doc: the blade-dict interchange contract

**Created:** 2026-08-13 · **Completed:** 2026-08-13

Pulled out of Group A of the 2026-08-13 archive gap-analysis sweep into its own task, because the
interchange is core enough to deserve a standing reference doc rather than a one-line harvest
(siblings: the four `harvest-*` tasks in this folder).

## What was done

Created `tasks/reference/blade-dict-interchange.md`, a standing reference for `BladeCoef`
(`dict[blade, coef]`), the canonical interchange format every representation (`Gn`,
`G1`/`G2`/`G3`, the graded subtypes) converts through via `to_blade_dict` / `from_blade_dict`, and
which all shared arithmetic in `base.py` routes through. Before it, the full contract lived only in
`base.py`'s `BladeCoef` docstring. Every claim was verified empirically against `base.py`, and the
doc was cross-linked from CLAUDE.md's interchange note and `tasks/reference/design-decisions.md`.

The doc captures:

- **Canonical keys.** Strictly increasing index tuples; `()` is the scalar blade. Every
  `from_blade_dict` (via the shared `_require_canonical_blades`) **raises `ValueError`** on a
  non-canonical key (`(2, 1)`, duplicates), a deliberate raise-over-canonicalize decision:
  `from_blade_dict` is an interchange/constructor primitive, not user sugar. It replaced two
  silent wrong answers (`Gn` stored the bad key raw; the graded/full classes dropped it). `e₂e₁` is
  a legal algebra element but not a legal key (it equals `−e₁e₂`, under key `(1,2)` with the sign
  folded in).
- **Zero handling.** Readers omit exact-zero coefficients; a missing blade reads as 0.
- **The eager/lazy "hidden zero" split.** `Gn` eager-simplifies, so a hidden zero
  (`cos²+sin²−1`) is pruned; the lazy classes keep a structural `0` only, so they can carry an
  un-reduced coefficient.
- **The graded silent-drop rule (the "exp() trap").** A graded type's `from_blade_dict` keeps only
  its own blades, so a result carrying a new grade must be built via dispatching arithmetic
  (`Bivector + scalar → Rotor`), never via `from_blade_dict` on the operand's type.

## Sources

- `base.py`: the `BladeCoef` docstring + `_require_canonical_blades` (authoritative).
- `tasks/archive/2026/07/29/validate-blade-dict-keys.md` (the raise-vs-canonicalize decision).
- `tasks/archive/2026/07/29/blade-dict-tests-and-comments.md` (the consolidated contract, tests).
