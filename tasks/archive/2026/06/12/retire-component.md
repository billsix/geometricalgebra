# Retire `component`, read coefficients via `to_blade_dict` instead

**Created:** 2026-06-12 · **Completed:** 2026-06-12

## Why

`component(x) = ⟨A x̃⟩₀ = (A * x.reverse()).scalar_part()` computed a geometric product and a grade
projection to recover a number the representation already stores (the `Gn` blade dict, or a specialized
class's `coeff_*` field). Reading it from `to_blade_dict()` is direct, representation-agnostic (both
storage forms surface through the interchange protocol), and correct for any grade — unlike
`scalar_product(e_12)`, which is the negative of the e₁₂ coefficient. The maintainer, 2026-06-12: "all
I'm trying to do is get the coefficient it already has — access it directly." `to_matrix` in
`transforms.py` already read coefficients that way.

The translation: `v.component(e_1)` → `v.to_blade_dict().get((1,), 0)`, and
`B.component(e_1 ^ e_2)` → `B.to_blade_dict().get((1, 2), 0)`.

## What was done

- **Deleted `AbstractMultiVector.component`**; a final grep found no other callers (no grade ≥ 2
  readers outside its test).
- **`src/gacalc/nbplotutils.py`:** its 24 uses moved to a private `_coord(mv, blade)` helper over
  `to_blade_dict()`. The typed helper surfaced a latent matplotlib ArrayLike issue that the
  `Unknown`-typed `component` calls had masked, fixed by floating the `Polygon` vertices; the
  now-unused `ex`/`ey` in one helper were removed.
- **Tests:** `test_component` became `test_coefficient_readback` (conformance and graded), asserting
  the `to_blade_dict()` round-trip and the reconstruction identity, so the property stayed covered.
- `notebooks/displaygraded.py`, CLAUDE.md and README moved to the new idiom, and the `component`
  known-issue text was dropped.
- **Then (the maintainer's call) a thin `coefficient(blade)` convenience was added** on
  `AbstractMultiVector`, restoring the ergonomic `v.coefficient(Vector2.e_1)` reader (a unit basis
  blade in) as a direct lookup — `(key,) = blade.to_blade_dict(); return
  self.to_blade_dict().get(key, 0)` — with no geometric product, correct for any grade, and a doctest.
  The tests and the README/CLAUDE/`displaygraded` docs use it; `nbplotutils` kept its tuple-based
  `_coord`. So `coefficient` is the public reader without `component`'s product/sign machinery. (The
  first recommendation had been direct `to_blade_dict().get` at call sites with no new API.)

The full suite passed (220); ty and ruff were clean.

`scalar_product` stayed: it is the genuine scalar product `⟨A B⟩` used by
`magnitude_squared`/`cosine`, not a coefficient reader. This superseded the "blessed getter" role that
`tasks/archive/2026/06/07/graded-class-e_n-zero-vs-basis-vector.md` had given `component`.
