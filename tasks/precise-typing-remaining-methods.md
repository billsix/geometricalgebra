# Extend type-precise typing to the remaining grade-preserving methods

**Status:** in-progress (2026-08-03) — **project/reject/reflect DONE** (type-precise on the
vector types via a new `transform_factory_overrides` generator helper, plus a `base.reject`
grade-narrowing soundness fix). **Tier 2 DONE 2026-08-14** (William Emerison Six
<billsix@gmail.com>): `rotor_from_vectors → Rotor_n`, plus `bivector_from_vectors` / `i` /
`.i()` / `plane_of_rotation → Bivector_n` (folded in from the `i` work in
`tasks/archive/2026/08/15/redo-exp-book-referenced.md` — same mechanism), and the `inverse` `-> Self` spot-check
(confirmed sound: returns the concrete type, not `Gn`). Generic helpers
`classmethod_narrowing_overloads` / `inherited_classmethod_narrowing` in `gen_specialized.py`;
ty clean (src/tests/tools), 358 tests, generator deterministic, doc-regions OK. **Tier 3 DONE
2026-08-26** (the pass-through instance methods — see Outcome). Only `identity` (optional, low
value) is left, and is **declined** (see Outcome), so this task is **DONE**.
**Priority:** 4
**Difficulty:** 4

## Outcome — Tier 3 done (2026-08-26)

Added the value-returning **pass-through instance methods** on `MultiVectorBase`:
**`projected_onto(onto)`**, **`rejected_away_from(away_from)`**, **`reflected_across(across)`** —
sugar for `factory(arg)(self)`, keeping the factories unchanged. **Names (Bill, 2026-08-26):** each
mirrors its factory's exact keyword (`onto` / `away_from` / `across`); the earlier `rejected_from` /
`reflected_in` were renamed because "rejected *from*" reads as "excluded from" and both dropped the
factory's preposition (see [[passthrough-project-reject-methods]]).

Precise typing on the graded `Vector_n` types via a new generator helper
**`passthrough_method_overrides`** (the instance-method analog of `transform_factory_overrides`):
`Vector.rejected_away_from(Vector|Bivector) → Vector`, `MultiVectorBase` catch-all otherwise; same
grade caps as the factories (project any grade; reject/reflect ≤ bivector). Impl returns
`MultiVectorBase` directly (no invariance issue, unlike the `ComposableFunction` wrapper). Call site
`frame.py:120` converted to `w = w.rejected_away_from(prior)`. Tests: `assert_type` (static
narrowing) + runtime equivalence in `tests/test_dot_wedge_projection_split.py`.

**Verified:** ruff clean; ty clean on `src`, `tests` (the `assert_type` checks), AND the full-context
generated modules; **411 tests**; doc-regions unique/balanced; generator byte-deterministic.

**`identity` declined (low value).** Making `base.identity() -> InvertibleFunction[T]` generic is
awkward: `identity` takes **no operand**, so there is nothing to bind `T` from — a caller would have
to supply it explicitly, which is more friction than the imprecise `InvertibleFunction[MultiVectorBase]`
costs (identity rarely needs the concrete type). Left as-is; reopen only if a concrete need appears.

**Not done (optional):** the broader one-shot call-site sweep beyond `frame.py` (e.g. the
`Vector.project(onto=b)(a)` one-shots in `notebooks/displayg2.py`) — the factories still work
everywhere, and `frame.py` demonstrates the sugar; convert the rest if/when desired.

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
  (mirrors `Bivector_n.exp() → Rotor_n`, already done). **DONE 2026-08-14** via
  `inherited_classmethod_narrowing` on the graded `Vector` (n≥2).
- **`bivector_from_vectors`** (`base.py:943`) → `MultiVectorBase`. Always the wedge
  `a ∧ b` = a **bivector**, so `Vector_n.bivector_from_vectors(a, b) → Bivector_n`. **DONE
  2026-08-14** (same helper). Its normalizing sibling **`i(a, b)`** (emitted, not inherited)
  → `Bivector_n` via `classmethod_narrowing_overloads`, and the instance
  **`.i()`** / **`plane_of_rotation`** → `Bivector_n`. All landed with the `i` work in
  `tasks/archive/2026/08/15/redo-exp-book-referenced.md`; the generic narrowing helpers were added here.
  - **Why the classmethod narrowing is sound:** the precise `@overload` discriminates on
    the `Vector` param type — the wedge/rotor of two *same-algebra* vectors is that algebra's
    `Bivector`/`Rotor` at runtime (verified: `type(Vector.i(...)).__name__ == "Bivector"`,
    etc.); any other input falls to the `MultiVectorBase` catch-all. 𝒢₁ has no bivector/rotor,
    so the narrowing is gated on n≥2 (𝒢₁ stays `MultiVectorBase`).
  - **Note — this does NOT unblock `plane_rotation` reuse.** `transforms.plane_rotation` is a
    **free function generic over `V`** (the operand type), so a classmethod returning the
    concrete `Bivector` would still widen `V`. It stays inline (also for its own
    numeric-preservation reason). The narrowing only helps *concrete-typed* call sites (e.g.
    `tests/test_exp.py`, rewritten to `g3.Vector.i(...)` 2026-08-14).
- **`identity`** (`base.py:833`) → `InvertibleFunction[MultiVectorBase]`. Minor — could be a
  generic `InvertibleFunction[T]` so the operand type is preserved. Low value (identity rarely
  needs the concrete type); listed for completeness.

**Tier 3 — project/reject/reflect pass-through instance methods (added 2026-08-25, Bill).** Design
+ rationale + call-site sweep live in [[passthrough-project-reject-methods]]; that work was folded
into this task so the pass-throughs are typed precisely from the start rather than shipped at
`MultiVectorBase` and revised. Add on `MultiVectorBase` (delegating to `type(self).project/reject/
reflect`): **`projected_onto(onto)`**, **`rejected_away_from(away_from)`**, **`reflected_across(across)`** —
value-returning sugar for `factory(arg)(self)`, keeping the factories unchanged. Then give them the
same precise graded returns as their factories — the *instance-method* analog of the Tier-1
overloads (`Vector.rejected_away_from(b) → Vector` for a vector arg, `MultiVectorBase` catch-all
otherwise), reusing the established overload machinery. Same correctness bound as Tier 1
(vector-onto/across-vector only; higher grades stay the catch-all). Also do the call-site sweep from
the spec doc (convert one-shot applications like `frame.py:120`; leave factory-reuse sites alone).

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
- [x] rotor_from_vectors → Rotor_n; bivector_from_vectors / i / .i() / plane_of_rotation →
      Bivector_n (2026-08-14, `classmethod_narrowing_overloads` +
      `inherited_classmethod_narrowing`; folded in the `i` work from `tasks/archive/2026/08/15/redo-exp-book-referenced.md`).
- [~] identity → generic InvertibleFunction[T] (optional, low value).
- [x] Tier 3: add `projected_onto`/`rejected_away_from`/`reflected_across` pass-throughs on
      `MultiVectorBase`, precisely typed via instance-method overloads on the graded types; convert
      the one-shot call sites. Spec: [[passthrough-project-reject-methods]].
- [x] Spot-check `inverse`'s `-> Self` is sound — confirmed: Vector/Rotor/Bivector `.inverse()`
      returns the concrete type, not `Gn` (rebuilt via `type(self).from_blade_dict`).
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
