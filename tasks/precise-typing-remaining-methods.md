# Extend type-precise typing to the remaining grade-preserving methods

**Status:** in-progress (2026-08-03) — **project/reject/reflect DONE** (type-precise on the
vector types via a new `transform_factory_overrides` generator helper, plus a `base.reject`
grade-narrowing soundness fix). `rotor_from_vectors` + `identity` + the `inverse` spot-check
remain as follow-ups.
**Priority:** 4
**Difficulty:** 4

## Goal

Extend the `@typing.overload` / graded-override type-precision that the products, sums,
contractions, `dual`, `even_part`/`odd_part`, `exp`, and `sandwich` already have (see
[[generated-product-typing]]) to the remaining methods whose result type is statically
knowable — so a consumer with a concrete type (`Vector2`, `Rotor2`, …) gets that type back
instead of the abstract `MultiVectorBase`, without a cast at the use site.

## Analysis (from `src/gacalc/base.py` return annotations, read 2026-08-03)

**Tier 1 — the function-returning family (currently `…[MultiVectorBase]`).** Same fix, same
mechanism (a graded override / overload resolving the concrete type for the provable case,
`MultiVectorBase` catch-all otherwise):

- **`project`** (`base.py:700`) → `ComposableFunction[MultiVectorBase]`. **In progress.**
- **`reject`** (`base.py:751`) → `ComposableFunction[MultiVectorBase]`. **In progress.**
- **`reflect`** (`base.py:789`) → `InvertibleFunction[MultiVectorBase]`. **In progress** (the
  obvious sibling — grade-preserving involution; vector-across-vector is a vector). The three
  are one family; `base.py`'s own comment already groups them ("project/reject/reflect return
  types are typed at MultiVectorBase").

  Correctness bound: proj/rej/reflect of a *vector onto/across a vector* are vectors (grade 1);
  claim precision only there. Higher-grade blades stay the `MultiVectorBase` catch-all — that's
  the separate [[generalize-reject-reflect-higher-grade]].

**Tier 2 — value-returning, type statically known, currently `-> MultiVectorBase`:**

- **`rotor_from_vectors`** (`base.py:848`) → `MultiVectorBase`. Always builds
  `R = |from||to| + to·from` = scalar + bivector = a **rotor**, so per algebra
  `Vector2.rotor_from_vectors(from, to) → Rotor2`, `Vector3 → Rotor3`. Clean candidate
  (mirrors `Bivector_n.exp() → Rotor_n`, already done).
- **`identity`** (`base.py:833`) → `InvertibleFunction[MultiVectorBase]`. Minor — could be a
  generic `InvertibleFunction[T]` so the operand type is preserved. Low value (identity rarely
  needs the concrete type); listed for completeness.

**Different mechanism (not per-type overloads) — note, don't force:**

- `transforms.projection_rotation` / `rotor_rotation` / `plane_rotation` are **free functions**
  returning an operand→operand function; the runtime preserves the operand's type (per CLAUDE.md),
  but static precision would need generics on the free functions, not graded overloads. Separate,
  lower-priority.

**Already precise — no work (listed so they're not re-investigated):**

- The `-> Self` grade-preservers inherited by the `@final` generated types: `reverse`,
  `normalize`, `simplified`, `expanded`, `inverse`. `Self` binds to the concrete class, so
  `Vector2.reverse() → Vector2` etc. (Worth a one-line runtime spot-check that `inverse`
  actually returns the concrete type rather than coercing to `Gn` — if it can widen, `-> Self`
  would be an unsound lie like the old product casts. Expected fine: these rebuild via
  `type(self).from_blade_dict`.)
- The already-overloaded family: `__mul__`/`__xor__`/`outer_product`/`inner_product`/
  `_geometric_product`/`__add__`/`__sub__`, `left/right_contraction`, `wedge`/`dot` aliases,
  `r_vector_part` (Literal overloads), `dual`, `even_part`/`odd_part`, `exp`, `sandwich`.

**Genuinely widens — leave:**

- `outer_product_of_vectors(*vectors)` — variadic; the result grade = the argument count, not
  statically fixed.
- The G3 odd-product gap (`Rotor3 * Vector3`, etc.) — no registered `{1,3}` type; tracked in
  [[model-odd-graded-type]].

## Plan

- [x] project/reject/reflect precise — `transform_factory_overrides(spec, method, param,
      wrapper)` in `tools/gen_specialized.py` emits precise + catch-all `@overload` stubs on the
      vector specs; `base.py` unchanged in signature. **Also fixed a latent soundness bug:**
      `base.reject` didn't narrow to the operand grade (returned raw `G3` in 3D), which would
      make the `Vector3` overload unsound — now narrows like `project`. assert_type-locked;
      `ty` clean (src/tests/tools); 347 tests pass; generator deterministic; doc-regions clean.
- [ ] rotor_from_vectors → Rotor_n (follow-up).
- [ ] identity → generic InvertibleFunction[T] (optional, low value).
- [ ] Spot-check `inverse`'s `-> Self` is sound (returns the concrete type at runtime).
- [x] Update [[generated-product-typing]]'s design section (done — records the mechanism + the
      base.reject fix).

## Caveat for Bill

`ruff format --check` couldn't be run at gate parity in-sandbox: the sandbox ruff (0.15.21) and
the container's ruff differ, and HEAD's `tools/gen_specialized.py` already shows "would reformat"
under the sandbox ruff on **pre-existing** lines. The newly-added generator lines and the four
edited non-generated files are format-clean at 88. **Run `make format` in the container** to
settle the generator's formatting under the gate's ruff before/at commit.

## Notes / decisions

- Origin: Bill (2026-08-03) — "isn't the type for projection going to be another Vector2?" then
  "analyze what else might need that typing treatment, based off existing code."
- Mechanism + rationale for the whole approach: [[generated-product-typing]]. The archetype
  consumer benefit (precise types unlock direct `.coeff_*` field access instead of the
  `.coefficient(blade)` reader) is documented there.
