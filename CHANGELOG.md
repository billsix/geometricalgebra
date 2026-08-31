# Changelog

Notable changes to gacalc, emphasizing **breaking changes** — anything that would break code
that imports gacalc: renamed or removed public methods, changed defaults, changed return
types, new immutability. Not exhaustive; the bar is *"would a consumer bumping the pin need to
migrate?"*. Format loosely follows [Keep a Changelog](https://keepachangelog.com); versions
match the `git` tags and PyPI releases.

Releases before 0.0.14 predate this changelog and are not retro-documented here — see the
`git log` and `tasks/archive/` for the older history.

## [Unreleased]

_Nothing yet._

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
