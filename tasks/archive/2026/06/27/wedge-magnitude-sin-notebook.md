# Notebook demonstration: |a∧b| = |a||b| sin θ  (G2 → G3 → rotor magnitude)

**Status:** **complete** (2026-06-27) — Phases 1, 2 done (notebooks); Phase 3 **determined: do not
change the code** (the substitution is a confirmed symbolic regression). Ready to archive.
**Proposed:** 2026-06-27
**Completed:** 2026-06-27

## Phase 3 result (2026-06-27) — DONE (determination: keep the current code)

The end goal was to let `rotor_from_vectors` use `abs(from_vec * to_vec)` instead of
`abs(from_vec) * abs(to_vec)`. **Outcome: this should NOT be done — it is a confirmed regression**, and
the current code is already correct.

- `rotor_from_vectors` lives **only in `base.py`** (shared; not code-generated, no specialized
  override) — so this was a pure `base.py` question, no generator involved.
- Its code already carries a comment (now extended) explaining the author **previously tried
  `abs(from*to)` and reverted it**: `abs(from*to) = √(|to|²|from|²)` is a nested radical sympy cannot
  push through the sandwich, breaking the symbolic `R v R⁻¹ == rotate` identity.
- **Reproduced empirically:** with symbolic 𝒢₂ vectors, the sandwich residual `simplify(R.sandwich(v) −
  rotate(from,to)(v))` is **`0` for `abs(from)*abs(to)`** and a **large unsimplifiable nested-radical
  expression for `abs(from*to)`** (numerically `~1e-138`, i.e. mathematically zero but symbolically
  irreducible). So the change keeps numeric rotations correct but breaks the symbolic identity used by
  tests/doctests.
- **Why the proof can't rescue it:** the intractable `√((a·b)² + |a∧b|²)` is exactly the *unfactored
  Lagrange form* from Phases 1–2; sympy only collapsed it there with a manual `factor` (2D) / because it
  was a bare sum-of-squares (3D). There's no clean way to make a `Rotor`'s `magnitude()` return the
  factored `|a||b|` form, since the rotor doesn't carry its vector factors.

**The proof's real payoff is documentation, not a code change:** it justifies the equality the existing
`base.py` comment relies on (`|a||b| = |to from|`). Added a pointer in that comment to the
`displayg2.py`/`displayg3.py` demonstrations. **No behavior change; no regression.**

## Phase 2 result (2026-06-27) — DONE

Added the parallel demonstration to `notebooks/displayg3.py` (after the plotting section), using two
general `Vector3` vectors. Same chain — dot → wedge → Lagrange → magnitude → rotor capstone — with
`assert` cells. All asserts pass; the notebook compiles and is `ruff`-clean. (Added the missing
`import sympy` and `Vector3` to that notebook's imports.)

**Difficulty verdict in 𝒢₃: actually CLEANER than 𝒢₂ at the magnitude level.**
- Lagrange residual `simplify(|a|²|b|² − (a·b)² − |a∧b|²)` → `0` directly (now the identity is a *sum of
  three squares*, `(a₁b₂−a₂b₁)² + (a₁b₃−a₃b₁)² + (a₂b₃−a₃b₂)²`).
- The square-root step **needs no `factor`** (unlike 𝒢₂): both `|a∧b|` and `|a||b|sin θ` are
  `√(same sum of squares)`, so `simplify(|a∧b| − |a||b|sin θ) → 0` on its own. The 𝒢₂ `factor` nudge was
  only needed because there the radicand was a *single* perfect square (`√(x²)` vs `Abs(x)`).
- `real=True` still required; `sin θ ≥ 0` branch still assumed.
- Rotor capstone: `a*b → Rotor3`, `simplify(|ab|² − |a|²|b|²) == 0`.

**Conclusion: confirmed in both 𝒢₂ and 𝒢₃.** The "two vectors span a 2-plane" argument means this
generalizes to any 𝒢ₙ. Phase 3 (apply to `rotor_from_vectors`) is ready, but **overlaps**
`geometric-product-magnitude-proof.md` — decide whether to merge before doing it.

## Phase 1 result (2026-06-27) — DONE

Added a self-checking demonstration section to `notebooks/displayg2.py` (after the transforms
section): builds two general `Vector2` vectors `a = a₁e₁ + a₂e₂`, `b = b₁e₁ + b₂e₂` (sympy symbols
declared **`real=True`**), then walks dot → wedge → Lagrange → magnitude → rotor capstone, with
`assert` cells that fail loudly if any identity breaks. All asserts pass; the notebook compiles and is
`ruff`-clean.

**Difficulty verdict: EASY at the squared level, MODERATE to reach the magnitude.**
- The **Lagrange / squared step is trivial**: `sympy.simplify(|a|²|b|² − (a·b)² − |a∧b|²)` collapses
  to `0` immediately (no assumptions, no coaxing).
- The **square-root step needs two small nudges**: (a) sympy won't, on its own, reduce
  `√((a₁²+a₂²)(b₁²+b₂²) − (a₁b₁+a₂b₂)²)` to `|a∧b|` — you must **`factor` the radicand** so it sees the
  perfect square `(a₁b₂ − a₂b₁)²`, after which `√` gives `Abs(a₁b₂ − a₂b₁)` which equals `(a^b).magnitude()`
  exactly (diff simplifies to `0`); (b) the `sin θ = √(1 − cos²θ)` choice assumes `sin θ ≥ 0`
  (θ ∈ [0, π]) — and the `Abs` in the gacalc magnitude already encodes exactly that branch, so they
  agree. Symbols **must be `real=True`** or `√(x²)` won't become `|x|`.
- **Coercion friction: none** — `Vector2.e_1`/`Vector2.e_2` build a `Vector2` directly; `inner_product`
  returns `Scalar`, `^` returns `Bivector2`, magnitudes are clean. (Used the graded subtypes rather than
  `Gn`-coerced vectors; no eager-simplify surprises.)
- **Bonus (Phase-3 preview):** also showed `a*b → Rotor2` with
  `simplify(|ab|² − |a|²|b|²) == 0`, i.e. `|ab| = |a||b|`.

**Conclusion: feasible and clean in 𝒢₂ → proceed to Phase 2 (𝒢₃).** Expect the same shape in 3D, with
the one open risk that `a∧b` is now a 3-component bivector, so the `factor`-the-radicand step may need
`factor`/`simplify` to recognize a sum-of-squares rather than a single square (Lagrange in 3D is
`|a|²|b|² − (a·b)² = (a₁b₂−a₂b₁)² + (a₁b₃−a₃b₁)² + (a₂b₃−a₃b₂)²`).

## Goal

Find out **how hard it is** to symbolically demonstrate, in the **g2 notebook**
(`notebooks/displayg2.py`, jupytext percent-format), that the magnitude of the wedge product
is `|a∧b| = |a| |b| sin θ` — derived the way Bill would:

1. start from the named identity `|a|²|b|² = |a|²|b|² (cos²θ + sin²θ)`, and
2. use the **definition of the dot product** `a·b = |a||b| cos θ`,

so that `(a·b)² = |a|²|b|² cos²θ` peels off and leaves `|a∧b|² = |a|²|b|² sin²θ`, i.e.
`|a∧b| = |a||b| sin θ`. The **feasibility question is the deliverable of Phase 1**: does this fall out
cleanly symbolically in `G2` (a clean `sympy.simplify`), or is it fiddly (branch/sign of `sin`,
square-root reduction)? The answer gates whether we extend to `G3` and then to rotors.

## Phases

### Phase 1 — G2, in `notebooks/displayg2.py`  (feasibility gate)
Demonstrate `|a∧b| = |a||b| sin θ` for two general `G2` vectors and **write down how hard it was.**
- Use symbolic vectors (`a = a₁e₁ + a₂e₂`, `b = b₁e₁ + b₂e₂`) — build them in the notebook, or reuse
  `gacalc.gn.sym_vec2_1` / `sym_vec2_2` coerced to `G2`.
- Show the chain in notebook cells (markdown + code):
  - `a·b = a.inner_product(b)` (scalar) and `a∧b = a ^ b` (bivector);
  - the **Lagrange step** `|a|²|b|² − (a·b)² == |a∧b|²` —
    `sympy.simplify(a.magnitude_squared()*b.magnitude_squared() - a.inner_product(b)**2
    - (a ^ b).magnitude_squared()) == 0`;
  - then `cos θ = a·b / (|a||b|)` (the dot-product definition; `a.cosine(b)` is available,
    `base.py:547`), `sin²θ = 1 − cos²θ`, giving `|a∧b| = |a||b| sin θ`.
- **Assess & record (the actual point of this phase):** did `sympy.simplify` close it directly? Did the
  `√` / `sin = √(1−cos²)` step need a non-negativity assumption (θ ∈ [0,π] ⇒ sin θ ≥ 0)? Any coercion
  friction (`Gn` symbolic vector → `G2`, eager-simplify vs lazy)? Write a short verdict at the end of
  the phase: **easy / moderate / hard**, with the blockers.
- **Gate:** only proceed to Phase 2 if Phase 1 actually works in `G2`.

### Phase 2 — G3, in `notebooks/displayg3.py`  (only if Phase 1 succeeds)
Repeat for two general `G3` vectors (`sym_vec3_1` / `sym_vec3_2`). Two vectors always span a single
2-plane, so the identity still holds; the question is whether it stays clean symbolically when `a∧b` is
a general `G3` bivector (three components) rather than a single `e₁₂`. Record the same easy/moderate/hard
verdict and note any 3D-specific friction.

### Phase 3 — rotor magnitude (end goal)
Use the result so a **rotor takes the magnitude of the product `ab` directly** instead of multiplying
the two magnitudes. Since `ab = a·b + a∧b` (orthogonal grades),
`|ab|² = (a·b)² + |a∧b|² = |a|²|b|²(cos²+sin²) = |a|²|b|²`, so `|ab| = |a||b|`. Concretely, let
`rotor_from_vectors` use `abs(from_vec * to_vec)` in place of `abs(from_vec) * abs(to_vec)` (equal by the
above) — the cleaner form for the half-angle bivector. **This is exactly the application already scoped
in `geometric-product-magnitude-proof.md`** — see overlap note below; Phase 3 should likely be merged
into / handed off to that task rather than duplicated.

## The math (sketch)

```
a b = a·b + a∧b ,   a·b = |a||b| cos θ ,   |a∧b| = |a||b| sin θ
Lagrange:  |a|²|b|² − (a·b)² = |a∧b|²          (in G2: (a₁b₂−a₂b₁)²)
⇒  |a∧b|² = |a|²|b|² − |a|²|b|² cos²θ = |a|²|b|² sin²θ
⇒  |a∧b| = |a||b| sin θ                         (sin θ ≥ 0 for θ ∈ [0,π])
and  |a b|² = (a·b)² + |a∧b|² = |a|²|b|²  ⇒  |a b| = |a||b|.
```

## Relationship to existing task — READ FIRST

`tasks/geometric-product-magnitude-proof.md` (proposed, 2026-06-13) already covers the **same identity**
and the **same rotor end-goal** (`abs(from*to)` vs `abs(from)*abs(to)`), targeting 2D → 3D → general-n
as a **proof** (sympy check in `tests/` and/or a docstring derivation). This new task differs only in
**framing**: it is **notebook-first** (`displayg2.py`/`displayg3.py` worked demonstrations) and
**feasibility-gated** (assess difficulty before generalizing). They should be **consolidated** —
recommend: keep this task as the *notebook demonstration + difficulty assessment* (Phases 1–2), and let
`geometric-product-magnitude-proof.md` own the *general-n proof + the `rotor_from_vectors` change*
(Phase 3 feeds it). **Decision needed from Bill:** merge them, or run this as the notebook front-end to
that proof task?

## Relevant gacalc code

- Symbolic vectors: `sym_vec2_1`/`sym_vec2_2`, `sym_vec3_1`/`sym_vec3_2`, `sym_vec_plane`
  (`src/gacalc/gn.py:194–200`).
- `inner_product` (`base.py:308`), `outer_product` / `^` (`base.py:341`), `magnitude` (`base.py:229`),
  `magnitude_squared` (`base.py:250`), `cosine(self, other)` (`base.py:547`).
- `rotor_from_vectors` (`base.py:686`) — the Phase-3 call site (codegen-aware: if specialized, change the
  generator, not `g2.py`/`g3.py`).
- Notebooks are jupytext percent-format; `--doctest-modules` does **not** run them, but keep cells
  runnable. Convention (CLAUDE.md): express any rotation via `rotate`/`rotor_from_vectors`, never a
  hand-built rotor literal.

## Open questions

- Deliverable shape for the "how hard" verdict — just prose in the notebook, or also a `sympy.simplify`
  assertion cell that fails loudly if the identity ever breaks?
- Does the `sin = √(1−cos²)` step need an explicit `θ ∈ [0,π]` (or `sin θ ≥ 0`) assumption to satisfy
  sympy, and is that acceptable in a demonstration?
- Consolidation decision with `geometric-product-magnitude-proof.md` (see above).
