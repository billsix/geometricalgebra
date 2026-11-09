# Extend type-precise typing to the remaining grade-preserving methods

**Created:** 2026-08-03 · **Completed:** 2026-08-26

## Goal

The `@typing.overload` / graded-override precision already on the products, sums, contractions,
`dual`, `even_part`/`odd_part`, `exp`, and `sandwich` (see `tasks/reference/generated-product-typing.md`)
was extended to the remaining methods whose result type is statically knowable, so a consumer with
a concrete type (`Vector2`, `Rotor2`, …) gets that type back instead of `MultiVectorBase`, without a
cast. Origin: the maintainer (2026-08-03) — "isn't the type for projection going to be another
Vector2?" then "analyze what else might need that typing treatment, based off existing code." The
consumer benefit (precise types allow direct `.coeff_*` field access instead of
`.coefficient(blade)`) is documented in the reference doc.

## What was done

**Tier 1 — `project` / `reject` / `reflect` (the function-returning family).** A new generator
helper `transform_factory_overrides(spec, method, param, wrapper)` in `tools/gen_specialized.py`
emits precise + catch-all `@overload` stubs on the vector specs; `base.py` signatures were unchanged.
Precision is claimed only where it is provable — a vector onto/across a vector is a vector;
higher-grade blades stay the `MultiVectorBase` catch-all (generalizing those is
`tasks/generalize-reject-reflect-higher-grade.md`). **A latent soundness bug was fixed on the way:**
`base.reject` did not narrow to the operand grade (it returned raw `G3` in 3D), which would have
made the `Vector3` overload unsound; it now narrows like `project`. Locked with `assert_type`; ty
clean on src/tests/tools; 347 tests.

**Tier 2 — value-returning methods (2026-08-14, William Emerison Six <billsix@gmail.com>).**
`rotor_from_vectors → Rotor_n` (it always builds `|from| * |to| + to·from`, a rotor) and
`bivector_from_vectors → Bivector_n` via `inherited_classmethod_narrowing` on the graded `Vector`
(n ≥ 2); the emitted `i(a, b)` → `Bivector_n` via `classmethod_narrowing_overloads`, and the instance
`.i()` / `plane_of_rotation` → `Bivector_n`. These were folded in from the `i` work in
`tasks/archive/2026/08/15/redo-exp-book-referenced.md` (same mechanism).
- The narrowing is sound because the precise overload discriminates on the `Vector` param type: the
  wedge/rotor of two same-algebra vectors is that algebra's `Bivector`/`Rotor` at runtime (verified
  `type(Vector.i(...)).__name__ == "Bivector"`); any other input falls to the catch-all. 𝒢₁ has no
  bivector/rotor, so it stays `MultiVectorBase`.
- This did **not** unblock `plane_rotation` reuse: `transforms.plane_rotation` is a free function
  generic over the operand type `V`, so a concrete-`Bivector` classmethod would still widen `V`. It
  stayed inline (also for its numeric-preservation reason). The narrowing only helps concrete-typed
  call sites (e.g. `tests/test_exp.py`, rewritten to `g3.Vector.i(...)` on 2026-08-14).
- The `inverse` `-> Self` spot-check confirmed it is sound: Vector/Rotor/Bivector `.inverse()`
  return the concrete type (rebuilt via `type(self).from_blade_dict`), not `Gn`.
- ty clean (src/tests/tools), 358 tests, generator deterministic, doc-regions OK.

**Tier 3 — pass-through instance methods (2026-08-26).** `projected_onto(onto)`,
`rejected_away_from(away_from)`, `reflected_across(across)` on `MultiVectorBase` — sugar for
`factory(arg)(self)`, factories unchanged. Design, names and rationale:
`tasks/archive/2026/08/26/passthrough-project-reject-methods.md` (names decided by William Emerison
Six <billsix@gmail.com>, 2026-08-26). Precise typing on the graded `Vector_n` types came from a new
helper `passthrough_method_overrides` (the instance-method analog of `transform_factory_overrides`):
`Vector.rejected_away_from(Vector|Bivector) → Vector`, catch-all otherwise, with the same grade caps
as the factories (project any grade; reject/reflect ≤ bivector). The impl returns `MultiVectorBase`
directly, so there was no invariance issue (unlike the `ComposableFunction` wrapper). `frame.py` was
converted to `w = w.rejected_away_from(prior)`; tests are `assert_type` + runtime equivalence in
`tests/test_dot_wedge_projection_split.py`.

`tasks/reference/generated-product-typing.md`'s design section was updated with the mechanism and
the `base.reject` fix.

## Declined / not done

- **`identity` → generic `InvertibleFunction[T]` was declined** (low value): `identity` takes no
  operand, so nothing binds `T`; a caller would have to supply it, which costs more than the
  imprecise `InvertibleFunction[MultiVectorBase]`.
- The broader one-shot call-site sweep beyond `frame.py` (e.g. the `notebooks/displayg2.py`
  one-shots) was left undone as optional.
- `transforms.projection_rotation` / `rotor_rotation` / `plane_rotation` would need generics on the
  free functions, not graded overloads; noted, not done.

## Already precise or genuinely widening (no work)

- Already precise: the `-> Self` grade-preservers on the `@final` generated types (`reverse`,
  `normalize`, `simplified`, `expanded`, `inverse`), and the already-overloaded family (products,
  sums, contractions, `wedge`/`dot`, `r_vector_part` Literal overloads, `dual`, even/odd parts, `exp`,
  `sandwich`).
- Genuinely widens: `outer_product_of_vectors(*vectors)` (variadic; grade = argument count), and the
  𝒢₃ odd-product gap (`Rotor3 * Vector3`; no registered `{1,3}` type at the time), tracked in
  `tasks/archive/2026/09/05/model-odd-graded-type.md`.

## Verification (Tier 3)

ruff clean; ty clean on `src`, `tests` (the `assert_type` checks) and the full-context generated
modules; 411 tests; doc-regions unique/balanced; generator byte-deterministic. `ruff format --check`
could not run at gate parity in the sandbox (sandbox ruff 0.15.21 differs from the container's, and
already flagged pre-existing generator lines), so the maintainer was asked to run `make format` in
the container to settle the generator's formatting.
