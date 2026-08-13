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
