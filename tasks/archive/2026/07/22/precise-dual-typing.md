# Precise `dual()` return type: drop the last unsound `Self` cast on a generated unary op

**Created:** 2026-07-22 · **Completed:** 2026-07-22

The last member of the typing-cleanup family
(`tasks/archive/2026/07/22/retype-even-odd-part-off-self.md`,
`tasks/archive/2026/07/22/overload-r-vector-part.md`,
`tasks/archive/2026/07/22/overloads-and-drop-cast-on-product-primitives.md`): `dual` was the one
remaining generated op declared `-> Self` with an unsound cast. E.g. `Bivector3.dual()` returned a
`Vector3` at runtime (`typing.cast(typing.Self, Vector3(...))`) but typed as `Bivector3`, and its
non-default-`n` branch returned a `_coerce(self, G3).dual(n)` also lied to `Self`.

## The wrinkle and the options

The mechanism was the same as the even/odd retype (no argument to key an `@overload` on the
result): retype `base.dual` to `-> MultiVectorBase`, then have each generated graded override
declare its resolved return type with no cast. `dual` added an `n` (dimension) parameter and a
two-branch body (the default-`n` closed form, and a non-default-`n` fallback to `G_n`), which a
single precise return type cannot cover. Two options were weighed:

1. **Drop or raise on the non-default-`n` fallback**: a fixed-dimension type's dual is
   intrinsically at its own dimension; `Bivector3.dual(5)` is meaningless.
2. **Overload on `n`** (`n: Literal[<DIMENSION>] | None` → resolved type, `n: int` →
   `MultiVectorBase`): keeps the fallback, at the cost of more machinery.

**Chosen: Option 1, raising on a mismatched `n`** (the loud-on-invalid variant, per the repo's
total-dispatch preference). No existing caller passed a non-dimension `n`, so nothing broke.

**`Gn`** inherits the `-> MultiVectorBase` floor with no override, consistent with the even/odd
resolution; no call site needs `Gn.dual()` statically precise.

## What shipped

All gates green: **297 tests** (incl. 2 new dual guards in `tests/test_operator_typing.py`),
`ty check` src/tests/tools clean, `ruff check` clean, `check-regions` clean, generator deterministic;
runtime values unchanged (a pure static-typing fix).

- **`base.py`**: `dual` retyped `-> typing.Self` → `-> MultiVectorBase` (body untouched), the floor
  that lets fixed-dimension overrides narrow.
- **Generator (`tools/gen_specialized.py`)**: a module-level `dim_mismatch_guard(cls, dim)` helper
  (`if n is not None and n != DIM: raise ValueError`); a `dual_method()` in `generate_graded_type`
  mirroring `parity_part` (declares the `unary_result`-resolved grade type, constructs it directly,
  **no cast**) but keeping the `n` param + guard; the full-class `G_n.dual` in
  `dimension_known_methods` dropped its `super().dual(n)` fallback for the same guard (keeps
  `-> Self`).
- **Result types**: `Vector3.dual() -> Bivector3`, `Bivector3.dual() -> Vector3`,
  `Trivector3.dual() -> Scalar`, `Rotor3.dual() -> G3`, `Vector2.dual() -> Vector2`,
  `Bivector2.dual() -> Scalar`, `Rotor2.dual() -> Rotor2`, `Vector1.dual() -> Scalar`,
  `G1/G2/G3.dual() -> Self`. Every unsound `cast(typing.Self, …)` on `dual` was gone.
- **`Rotor3.dual() -> G3`** is an honest widen: Rotor3 is grades {0,2}, its dual {3,1} is the odd
  part, which then had no covering graded type (an odd type was later modelled in
  `tasks/archive/2026/09/05/model-odd-graded-type.md`).

**Deviation from the original goal: `Scalar.dual()` could not narrow** (it was to be
`-> Trivector3`). `Scalar` was then a single grade-0 type shared across every 𝒢ₙ (`scalar.py`), so
it did not know its own dimension (its dual is `Vector1` / `Bivector2` / `Trivector3` by algebra).
It kept requiring an explicit `n` and was retyped `-> MultiVectorBase`, dropping its own unsound
cast. The reverse, `Trivector3.dual() -> Scalar`, was precise and shipped. The follow-on
`tasks/archive/2026/07/22/per-algebra-scalar-types.md` split `Scalar` per algebra to fix this.

## Release and the cross-repo payoff

This was a downstream-visible typing change. mvp's dual coefficient cleanup
(github.com/billsix/modelviewprojection `tasks/archive/2026/07/22/dual-coefficient-cleanup.md`) was
gated on a released gacalc carrying it, because mvp consumes gacalc only from **PyPI** (the
`gacalc==` wheel pin in `requirements.txt` and the sdist the `Dockerfile` `ARG GACALC_VERSION`
fetches), not GitHub. It unblocked the one site that mvp's precise-product cleanup
(github.com/billsix/modelviewprojection `tasks/archive/2026/07/22/precise-product-types-coefficient-cleanup.md`) had to leave alone: `find_normal` in `mathutils.py` does
`n = bivector.dual()` then reads a coefficient, which with `Bivector3.dual() -> Vector3` became a
direct `.coeff_*` field read.

The release (0.0.12 → 0.0.13 in `pyproject.toml`, `make release` to PyPI, host `git tag`, push to
GitHub) was the maintainer's to run, batched with the per-algebra-Scalar work; `v0.0.13` was tagged.

## Related

- `tasks/reference/generated-product-typing.md` (same family/rationale);
  `tasks/archive/2026/07/22/retype-even-odd-part-off-self.md` is the closest sibling.
- `tasks/archive/2026/09/05/model-odd-graded-type.md` (the `Rotor_n.dual` widening).
