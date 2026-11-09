# Prove |ab| = |a||b| (any dimension) and use it to simplify the rotor's product magnitude

**Created:** 2026-06-13 · **Completed:** 2026-06-27

## What it was

The maintainer asked for a proof that the magnitude of the geometric product of two vectors is the
product of their magnitudes, `|a * b| = |a| * |b|` — 2D first, then 3D, ideally any dimension — and then
to use it so `rotor_from_vectors` could write `abs(from_vec * to_vec)` instead of
`abs(from_vec) * abs(to_vec)`, the cleaner form for the half-angle bivector and, at the time, for the
type system. The task moved here from modelviewprojection on the maintainer's correction: the rotor
primitives and magnitude are native gacalc work, and mvp consumes them through its `mathutils.py`
façade. It was handled together with its notebook-first sibling
`tasks/archive/2026/06/27/wedge-magnitude-sin-notebook.md`, whose phase results hold the worked detail.

## The math (the maintainer's sketch)

```
a * b = a·b + a∧b ,   a·b = |a| * |b| * cos(θ) ,   |a∧b| = |a| * |b| * sin(θ)
|a * b|² = (a·b)² + |a∧b|² = |a|² * |b|² * (cos²(θ) + sin²(θ)) = |a|² * |b|²
⇒  |a * b| = |a| * |b|
```

Distributing `|a|² * |b|² * (sin²(θ) + cos²(θ))` into `(a·b)² + |a∧b|²` (Lagrange) is what makes the
product's magnitude clean to square-root. For 3D or general n: two vectors span one 2-plane and `a * b`
lives in that plane's even subalgebra, so n-D reduces to 2D.

## Outcome (2026-06-27)

- **The proof was demonstrated** symbolically for general vectors, with self-checking `assert` cells,
  in `notebooks/displayg2.py` (𝒢₂) and `notebooks/displayg3.py` (𝒢₃). A formal arbitrary-`n` proof was
  not pursued as a separate artifact; the 2D/3D demonstrations plus the 2-plane argument were judged
  sufficient.
- **The rotor change was decided won't-do.** Switching `rotor_from_vectors` to `abs(from*to)` was
  re-confirmed to regress the symbolic `R v R⁻¹ == rotate` identity: `abs(from*to) = √(|a|² * |b|²)` is a
  nested radical sympy cannot simplify through the sandwich (the residual stayed a large irreducible
  expression, numerically ~1e-138). `abs(from) * abs(to)` is correct and symbolically tractable.
- **The type motivation had already gone:** `magnitude()` was typed `Coef`, so
  `abs(from) * abs(to)` type-checked (see `tasks/archive/2026/06/13/magnitude-sympy-cast-to-coef.md`).

The only code change was a comment in `rotor_from_vectors` (`base.py`, not generated) pointing at the
notebook proof.
