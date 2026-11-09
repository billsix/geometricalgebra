# Notebook demonstration: |a∧b| = |a||b| sin θ  (G2 → G3 → rotor magnitude)

**Created:** 2026-06-27 · **Completed:** 2026-06-27

## What it was

A feasibility-gated, notebook-first check of how hard it is to show symbolically that
`|a∧b| = |a| * |b| * sin(θ)`, derived the maintainer's way: start from
`|a|² * |b|² = |a|² * |b|² * (cos²(θ) + sin²(θ))`, use the dot-product definition
`a·b = |a| * |b| * cos(θ)` so that `(a·b)²` peels off, leaving `|a∧b|² = |a|² * |b|² * sin²(θ)`. 𝒢₂ came
first (the gate), then 𝒢₃, then the rotor application. It overlapped
`tasks/archive/2026/06/27/geometric-product-magnitude-proof.md` (the same identity and rotor end goal,
framed as a proof); the two were run together, this task owning the notebook demonstrations and the
difficulty assessment, that one the rotor decision.

```
a * b = a·b + a∧b
Lagrange:  |a|² * |b|² − (a·b)² = |a∧b|²          (in 𝒢₂: (a₁ * b₂ − a₂ * b₁)²)
⇒  |a∧b| = |a| * |b| * sin(θ)                     (sin(θ) ≥ 0 for θ ∈ [0, π])
and  |a * b|² = (a·b)² + |a∧b|² = |a|² * |b|²  ⇒  |a * b| = |a| * |b|
```

## Phase 1 — 𝒢₂ (`notebooks/displayg2.py`)

A self-checking section after the transforms section builds two general `Vector2` vectors from
`Vector2.e_1`/`e_2` with sympy symbols declared `real=True`, and walks dot → wedge → Lagrange → magnitude
→ rotor capstone with `assert` cells that fail loudly if an identity breaks (chosen over prose alone).
All asserts passed; the notebook compiled and was `ruff`-clean.

**Verdict: easy at the squared level, moderate to reach the magnitude.**
- The Lagrange step `simplify(|a|² * |b|² − (a·b)² − |a∧b|²)` collapsed to `0` at once, no assumptions.
- The square-root step needed two nudges: sympy would not reduce the radicand to `|a∧b|` until it was
  `factor`ed into the perfect square `(a₁ * b₂ − a₂ * b₁)²`, after which `√` gave
  `Abs(a₁ * b₂ − a₂ * b₁)`, equal to `(a ^ b).magnitude()`; and `sin(θ) = √(1 − cos²(θ))` assumes
  `sin(θ) ≥ 0` (θ ∈ [0, π]), the same branch the `Abs` in gacalc's magnitude encodes — accepted for a
  demonstration. The symbols must be `real=True` or `√(x²)` does not become `|x|`.
- No coercion friction: the graded subtypes were used (`inner_product` → `Scalar`, `^` → `Bivector2`),
  avoiding `Gn`'s eager simplify.
- Capstone: `a * b → Rotor2` with `simplify(|a * b|² − |a|² * |b|²) == 0`.

## Phase 2 — 𝒢₃ (`notebooks/displayg3.py`)

The same chain for two general `Vector3` vectors, after the plotting section, with `assert` cells (the
missing `import sympy` and `Vector3` imports were added). All asserts passed; it compiled and was
`ruff`-clean.

**Verdict: cleaner than 𝒢₂ at the magnitude level.** The Lagrange residual simplified to `0` directly
(now a sum of three squares, `(a₁b₂−a₂b₁)² + (a₁b₃−a₃b₁)² + (a₂b₃−a₃b₂)²`), and the square-root step
needed no `factor`: both `|a∧b|` and `|a| * |b| * sin(θ)` are `√(the same sum of squares)`. (𝒢₂ needed
the nudge because its radicand was a single perfect square, `√(x²)` versus `Abs(x)`.) `real=True` and the
`sin(θ) ≥ 0` branch were still required. Capstone: `a * b → Rotor3`, `|a * b|² = |a|² * |b|²`. Since two
vectors span one 2-plane, the result generalizes to any 𝒢ₙ.

## Phase 3 — rotor magnitude: decided, keep the current code

The end goal was letting `rotor_from_vectors` use `abs(from_vec * to_vec)` in place of
`abs(from_vec) * abs(to_vec)`. **It was not done: it is a confirmed regression**, and the current code was
already correct.

- `rotor_from_vectors` lives only in `base.py` (not generated, no specialized override), so no generator
  was involved. Its comment already recorded that the author had tried `abs(from*to)` and reverted it.
- Reproduced: with symbolic 𝒢₂ vectors, `simplify(R.sandwich(v) − rotate(from, to)(v))` was `0` for
  `abs(from) * abs(to)` and a large unsimplifiable nested-radical expression for `abs(from*to)`
  (numerically ~1e-138: mathematically zero, symbolically irreducible), which breaks the symbolic identity
  the tests and doctests use.
- The proof cannot rescue it: the intractable `√((a·b)² + |a∧b|²)` is the unfactored Lagrange form,
  which sympy collapsed above only with a manual `factor` (2D) or as a bare sum of squares (3D), and a
  `Rotor`'s `magnitude()` cannot return the factored `|a| * |b|` because the rotor does not carry its
  vector factors.

The proof's payoff was documentation: it justifies the equality the `base.py` comment relies on, and that
comment gained a pointer to the `displayg2.py`/`displayg3.py` demonstrations. No behaviour change.
