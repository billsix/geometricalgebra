# Changelog

Notable changes to gacalc, emphasizing **breaking changes** — anything that would break code
that imports gacalc: renamed or removed public methods, changed defaults, changed return
types, new immutability. Not exhaustive; the bar is *"would a consumer bumping the pin need to
migrate?"*. Format loosely follows [Keep a Changelog](https://keepachangelog.com); versions
match the `git` tags and PyPI releases.

Releases before 0.0.14 predate this changelog and are not retro-documented here — see the
`git log` and `tasks/archive/` for the older history.

## [Unreleased]

### Fixed
- **Numeric `==` no longer calls `sympy.simplify`.** Comparing two multivectors whose
  coefficients are plain numbers now short-circuits on the native `==` in both outcomes;
  sympy is reached only when a coefficient is symbolic. `simplify` can never make two
  unequal numbers equal, so this is a pure speedup with **no change in results** —
  symbolic equality, including structurally-different-but-equal forms, is unchanged.
  A differing `g2.Vector` comparison drops from ~48 µs to ~0.4 µs. The rule now lives in
  one place, `base._coef_eq`, shared by the generated same-type and blade-dict paths.

### Changed
- **Read-only container parameters widened to their covariant supertypes.**
  `transforms.compose_intermediate_fns` and `compose_intermediate_fns_and_fn` now take
  `Sequence[InvertibleFunction[V]]` rather than `list[...]`, so any sequence is accepted.
  Purely permissive — existing calls passing a list are unaffected. Part of the repo-wide
  type-annotation sweep, whose deliberate exemptions are recorded in
  `tasks/reference/type-annotation-exemptions.md`.

## [0.0.20] — 2026-09-06

### Added
- **`rotate_90_degrees` — the 𝒢₂ quarter turn, in two forms** (additive; a PATCH bump). `g2.Vector.rotate_90_degrees()` (generated, closed form, `Vector -> Vector`)
  and the module-level `g2.rotate_90_degrees()` factory returning an `InvertibleFunction[Vector]`
  (composes: four turns are the identity; inverts to the −90° turn; `at(t)` interpolates through
  `plane_rotation(e_1, e_2)(t·π/2)`). Both ARE `v * e_12` — multiplication by the unit
  pseudoscalar, `(x, y) -> (-y, x)`, exact on integer and symbolic coefficients (no `cos`/`sin`).
  𝒢₂ only (`g1`/`g3` deliberately have neither), and the factory rejects anything but a `g2.Vector`
  with `TypeError`. `g2.py` now imports `gacalc.transforms` (for the interpolation law; acyclic).
  Design record: `tasks/archive/2026/09/06/add-quarter-turn-to-g2.md`.
- **Compile-once matrix templates: `to_matrix_template(fn, cls, params, n=None)` and
  `MatrixTemplate`** (`gacalc.transforms`; additive). Compiles a linear/affine function built over
  sympy symbols into a template whose `fill(*numbers)` returns the homogeneous `np.float32` matrix by
  copying constants and assigning the parameter entries — no basis probing per call (the per-sprite
  model matrix of a game renderer is the motivating case). Entries that are expressions in the
  parameters (a symbolic rotation angle's `cos`/`sin`) are evaluated per fill through one lambdified
  call. Works in 𝒢₂ (3×3), 𝒢₃ (4×4) and `Gn` with explicit `n`, linear or affine. Also **method forms
  on `ComposableFunction`** (inherited by `InvertibleFunction`): `fn.to_matrix(cls, n=None, *,
  backend=...)` and `fn.to_matrix_template(cls, params, n=None)`. Record:
  `tasks/archive/2026/09/06/matrix-template-compile-once.md`.

### Changed
- `to_matrix`'s `fn` parameter is now typed `ComposableFunction[Any]` (was
  `InvertibleFunction[Any]`) — a widening, no call changes: a matrix needs only the forward map and
  the `linearity` tag, both on the base type. A hand-built linear `ComposableFunction` is now
  matrix-able.

## [0.0.19] — 2026-09-05

### Changed
- **Typing precision for the scalar transform factories and `to_matrix`** (no runtime change).
  `uniform_scale(m)` and `scale_non_uniform(*factors)` now return `InvertibleFunction[V]` (was
  `[MultiVectorBase]`), so a caller annotating `InvertibleFunction[g3.Vector]` type-checks under
  ty ≥ 0.0.72's invariance enforcement; `to_matrix` takes `InvertibleFunction[typing.Any]` (was
  `[MultiVectorBase]`) so concrete and representation-agnostic functions both pass. Not breaking:
  every previously valid call still checks; a `typing.cast` at the two factories' return is now
  visible in any book region that `literalinclude`s their bodies. Driven by modelviewprojection's
  ty sweep; record: `tasks/archive/2026/09/06/ty-invariance-transform-factories-bind-v.md`.

## [0.0.18] — 2026-08-31

### Added
- **The cross product.** New `gacalc.vectorcalc` module with `cross(a, b)` — the dual
  of the wedge, `(a ∧ b) I₃⁻¹` — for 3-D vectors (`g3` or `Gn` with basis indices ≤ 3);
  a `MultiVectorBase.cross(other)` pass-through method; and a **generated closed-form
  `g3.Vector.cross`** typed precisely (`Vector -> Vector` overload). Dot and the scalar
  triple product intentionally get no aliases — they are `scalar_product` and
  `measure.signed_volume` (the identity `a · (b × c) = signed_volume(a, b, c)` is
  gated by tests).
- **Custom blade display symbols** (LaTeX display only): `set_blade_symbols({(1,):
  r"\mathbf{i}", ...})` in a notebook setup cell makes every later display render
  mapped blades under custom names (e.g. calc-3 **i**/**j**/**k**); `blade_latex` and a
  `symbols` parameter on `blade_dict_latex` are the pure layer underneath. The
  blade-tuple interchange format and `__repr__` are untouched. New demo notebook
  `notebooks/displayvectorcalc.py`.

### Changed
- Cosmetic rendering unification (`blade_dict_latex` and the plot labels now share one
  blade renderer): basis subscripts are braced (`\mathbf{\vec{e}}_{1}` — renders
  identically), and plot blade labels dropped their `\,` thin-space join.

## [0.0.17] — 2026-08-23

*(Retro-filled 2026-08-31 — this release originally shipped without a changelog
entry; reconstructed from `git log v0.0.16..v0.0.17`.)*

### Breaking
- **`exp()` of a vector now raises `ValueError`.** The old galgebra-derived
  hyperbolic (`cosh/sinh`) vector branch was removed — it is a Minkowski boost with
  no meaning in this Euclidean library. `exp` remains defined for scalars and
  negative-square blades, and **exp of a bivector is now typed as a `Rotor`**
  (`Bivector.exp() -> Rotor`).
- **The generated `dual()` is dimension-locked.** On `g1`/`g2`/`g3` types, `dual(n)`
  now defaults to the algebra's own dimension and **raises on any other `n`** (it
  previously coerced through the full class). `Gn.dual(n)` is unchanged.

### Added
- `gacalc.frame` — frames (linear independence via the wedge test): `is_frame`,
  `make_orthogonal_frame`, `make_orthogonal_frame_hestenes`.
- `gacalc.measure` — named measures: `content` / `content_by_rejection` / `area` /
  `volume` and the signed determinants `signed_content` / `signed_area` /
  `signed_volume`, plus pass-through methods on vectors (`v.area(w)`).
- Unit-bivector plane helpers: `cls.i(a, b)` (the plane of two vectors) and `.i()`
  (a bivector/rotor's own unit plane); rotation transforms gained LaTeX label
  customization (`latex_repr=` on `plane_rotation`).
- `g4`/`g5` are generated at release time (`GACALC_DIMS=1,2,3,4,5` in `make dist`)
  and ship in the wheel.

## [0.0.16] — 2026-08-13

### Breaking
- **All generated types lost their dimension suffix; the module now carries the
  dimension.** `Vector2`/`Vector3` → `Vector`, and likewise `Bivector`/`Trivector`/
  `Rotor`/`Scalar`; the full class `G2`/`G3` → `G`. Import module-qualified —
  `import gacalc.g2 as g2` then `g2.Vector`, `g2.G` (or `from gacalc.g2 import Vector`
  in single-dimension code). `Gn` (the dimension-agnostic reference in `gacalc.gn`) is
  **unchanged**. Reprs are now module-qualified (`g2.Vector(coeff_e_1=3, coeff_e_2=4)`)
  so a value's dimension stays visible despite the shorter class name. Migrate a
  multi-dimension consumer by module-qualifying its imports (do **not** alias
  `Vector as Vector2` — that re-adds the suffix).

### Fixed
- **`normalize()` / `inverse()` of a zero-magnitude multivector now raise
  `ZeroDivisionError` for every coefficient kind.** Previously a float zero raised,
  but an int/symbolic zero silently returned `nan`-poisoned coefficients (sympy
  `0 ** -1` → `zoo`, `0 * zoo` → `nan`).

## [0.0.15] — 2026-08-03

### Breaking
- **`is_close` → `isclose`, and its tolerances no longer default to `1e-5`.** Both `rel_tol`
  and `abs_tol` now default to `0.0`, so a bare `isclose(a, b)` is **exact** equality; callers
  pass the tolerance they want (e.g. `a.isclose(b, rel_tol=1e-5, abs_tol=1e-5)`). Rationale and
  the standard-library grounding: `tasks/reference/approximate-float-equality.md`. *(This is the
  change that motivated starting this changelog — it broke a downstream consumer's 36 call
  sites silently.)*
- **Module basis constants are now the graded type, not the full class.** `from gacalc.g2
  import e_1` is a **`Vector2`** (was `G2`); `e_12` a `Bivector2`; `zero`/`one` a `Scalar_n`.
  Runtime values are identical — only the static type tightened (`e_1 * e_2` now types as
  `Rotor2`). To build a general `G_n` concisely use the full class's own constant (`G2.e_1`),
  `G2(...)`, or `Gn`. See `tasks/reference/design-decisions.md` ("Two ways to name a basis
  blade").

## [0.0.14] — 2026-07-22

### Breaking
- **Generated value types are now frozen (immutable) — `@dataclass(frozen=True)`.** Coefficient
  fields cannot be reassigned and the `x`/`y`/`z` coordinate properties are read-only; "changing
  a coordinate" means **rebinding** a new value (`v = Vector2(-v.x, v.y)`), not `v.x = …`.
  Consumers that mutated multivectors in place must convert to rebinding. (Frozen types are also
  **not hashable** — the custom `__eq__` leaves `__hash__ = None`.) See
  `tasks/reference/design-decisions.md` (the frozen/slots entry).
