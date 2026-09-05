# Graded subspaces vs subalgebras (why `Odd_3` is a type but not a subalgebra)

**Reference document** — a domain note on a distinction that pervades geometric algebra and that
gacalc's *graded subtypes* lean on directly: most grade-defined subspaces are **linear subspaces
but NOT subalgebras**. Written 2026-09-05 because the even/odd split of 𝒢₃ is the cleanest first
example of "a subspace that is not closed under the product." Not a task; update in place.

## The distinction, in plain algebra terms

Given an algebra `A` (a vector space with a bilinear product):

- A **linear subspace** `S ⊆ A` is closed under **addition and scalar multiplication**: `u, v ∈ S`
  and scalar `λ` ⟹ `u + v ∈ S` and `λu ∈ S`. Nothing is said about the product.
- A **subalgebra** is a linear subspace that is *also* closed under the **product**: `u, v ∈ S`
  ⟹ `uv ∈ S`.

Every subalgebra is a subspace; the converse is false. The gap — **a subspace whose product can
land outside it** — is common, but it rarely gets a spotlight because in many familiar algebras the
subspaces one names *happen* to be closed. Geometric algebra is the opposite: **most of the
subspaces you'd naturally name are not subalgebras**, and that is completely fine.

## Why it pervades GA: the grade-parity rule

The geometric product of a grade-`j` blade and a grade-`k` blade has components only at grades

    |j − k|, |j − k| + 2, …, j + k

— i.e. grades that step by 2, so **every output grade has the same parity as `j + k`**. That single
fact (the geometric product respects the ℤ₂ / even–odd grading of the exterior algebra) decides
which grade-sets are closed:

| operands' parities | result parity |
|---|---|
| even × even | even |
| even × odd  | odd  |
| odd × even  | odd  |
| **odd × odd** | **even** |

So a grade-set `G` is a subalgebra **iff** it is closed under this grade arithmetic. Two grade-sets
are always closed — the **scalars `{0}`** (the base field) and the **even part `{0, 2, 4, …}`** — and
almost nothing else is.

## The even part IS a subalgebra; the odd part is NOT

- **Even part `𝒢⁺ = {0, 2, 4, …}`** — closed (even × even → even). It is a genuine subalgebra, and a
  famous one: `𝒢⁺₂ ≅ ℂ` (`{a + b·e₁₂}`, `e₁₂² = −1`) and **`𝒢⁺₃ ≅ ℍ`, the quaternions** (its unit
  elements are exactly the rotors/spinors). In gacalc this is `Rotor_n`.
- **Odd part `𝒢⁻ = {1, 3, 5, …}`** — a perfectly good linear subspace (closed under `+`, scalar
  `·`, and `reverse`, which preserves grade), but **NOT closed under the geometric product**:
  **odd × odd = even**. E.g. in 𝒢₃, an `Odd_3` value (a vector + a trivector) times another `Odd_3`
  lands in `{0, 2}` = `Rotor_3` — *outside* `Odd_3`. So `𝒢⁻` is a subspace, not a subalgebra. This is
  the type we call `Odd_3` (see `tasks/model-odd-graded-type.md`).

The odd part is not structureless, though — it is a **bimodule over the even subalgebra**:
`even × odd → odd` and `odd × even → odd`, so `Rotor_n · Odd_n ⊆ Odd_n` on both sides. The clean way
to say it: `𝒢 = 𝒢⁺ ⊕ 𝒢⁻` is a **ℤ₂-graded (super)algebra** — the even part is the degree-0
subalgebra, the odd part is the degree-1 component, an `𝒢⁺`-module but not an algebra in its own
right.

## Even the single grades aren't subalgebras

The pure-grade subspaces gacalc already types are the same story:

- `Vector` (grade 1): `v·v = |v|² + (v ∧ v)` → `{0, 2}`, not grade 1.
- `Bivector` (grade 2): `B·B ∈ {0, 2}`, not pure grade 2.
- `Trivector` (grade 3 in 𝒢₃): `T² = ±1` → grade 0, not grade 3.

None is closed, yet all are legitimate, useful graded types. So `Odd_3` being non-closed puts it in
the same, well-populated company as `Vector`/`Bivector`/`Trivector` — the norm, not the exception.

## The 𝒢₃ scorecard (which grade-sets are subalgebras)

| grade-set | gacalc type | subalgebra? | why |
|---|---|---|---|
| `{0}` | `Scalar` | **yes** | the base field, `s·s ∈ {0}` |
| `{1}` | `Vector` | no | `v·v ∈ {0,2}` |
| `{2}` | `Bivector` | no | `B·B ∈ {0,2}` |
| `{3}` | `Trivector` | no | `T² ∈ {0}` |
| `{0,2}` | `Rotor` | **yes** (≅ ℍ) | even × even → even |
| **`{1,3}`** | **`Odd_3`** | **no** | **odd × odd → even** |
| `{0,3}` | (unnamed) | **yes** (≅ ℂ) | `I₃` is central in odd dim and `I₃² = −1`, so `{a + b·I₃}` is closed |
| `{0,1,2,3}` | `G3` | **yes** | the whole algebra |

Note the subtlety in `{0,3}` vs `{1,3}`: closure is about the *specific* grade-set's product
behaviour, not the number of grades. `{0,3}` is closed (the central pseudoscalar), `{1,3}` is not.

## Why gacalc's type system doesn't care

A gacalc **graded subtype is just a named linear subspace** — a fixed set of grades with `coeff_*`
fields for exactly those blades. Closure under the product is **irrelevant to whether it is a valid
type**: `Vector`/`Bivector`/`Trivector` are all non-closed and all typed. `Odd_3` is no different.

What *does* matter is that the product's **return type follows the operation**, resolved from the
symbolic result's grade support (see `tasks/reference/generated-product-typing.md`). So the generator
types `Odd_3 * Odd_3 → Rotor_3` (odd × odd = even) automatically — the non-closure surfaces as a
*correct return type*, never as a problem. That is exactly why adding `Odd_3` is safe: the type
records a subspace, and the generator's grade-support resolution already handles the fact that
products leave it.

## Related

- `tasks/model-odd-graded-type.md` — the task that registers `Odd_3 = {1,3}` and (Option B) adds a
  grade query + cast so an `Odd_3` value can be narrowed to `Vector`/`Trivector` when a grade
  vanishes.
- `tasks/reference/generated-product-typing.md` — how the generator resolves a product's return type
  from its grade support ("smallest covering registered type, else widen to `G_n`").
