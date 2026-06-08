# Model the odd graded type (Vector·Bivector → {grade 1, grade 3}) in 𝒢₃

Status: **plan — not started** · proposed 2026-06-08 · needs a go/no-go

## The gap (confirmed)

Every product of two graded types lands in a registered graded type **except one
family** in 𝒢₃: products whose grade support is the **odd part `{1, 3}`** (a
vector + a trivector). There is no registered type for `{1, 3}`, so they widen to
the full `G3`. Confirmed:

| product | grade support | current return |
|---|---|---|
| 𝒢₂ `Vector2 * Bivector2` | `{1}` | `Vector2` ✓ |
| 𝒢₂ `Rotor2 * Vector2` | `{1}` | `Vector2` ✓ |
| **𝒢₃ `Vector3 * Bivector3`** | **`{1, 3}`** | **`G3`** ✗ |
| **𝒢₃ `Rotor3 * Vector3`** | **`{1, 3}`** | **`G3`** ✗ |
| **𝒢₃ `Rotor3 * Trivector3`** | **`{1, 3}`** | **`G3`** ✗ |

So **𝒢₂ has no gap** (its odd part is just grade 1 = `Vector2`), **𝒢₁ has no
bivector** (N/A), and the missing type is exactly the **odd part of 𝒢₃**,
`{1, 3}` — the mirror image of the even part `{0, 2}` which is already modeled as
`Rotor3`. This is what `Rotor3 * Vector3` produces, which is why the rotor
sandwich widened.

## Why this is a small change

The generator already does all the hard work; the type registry is one function.
`tools/gen_specialized.py`:

- **`graded_specs(n)`** (line 331) is the registry — it lists `Vector{n}`,
  `Bivector{n}`, `Trivector{n}`, `Rotor{n}` as `TypeSpec(name, blades, dim, kind)`.
  `Rotor{n}` is built as "all even-grade blades."
- **`resolve(support, …)`** (line 358) picks the *smallest registered type
  covering* a product's grade support — so the moment an odd-part type is
  registered, every `{1, 3}` product resolves to it automatically.
- **`product_result(...)`** (line 370) derives each product's closed-form rules
  *symbolically from the general `Gn` product* — **no multiplication rules are
  written by hand.** Register the type and the generator derives `Vector3 *
  Bivector3 = <that type>`, `<that type> * Rotor3 = <that type>`, etc.
- The graded **class emission** (≈line 1282) generates the dataclass (fields
  `coeff_e_1/coeff_e_2/coeff_e_3/coeff_e_123`, the `match`-based products, basis
  constants, docstrings) for every spec.

**So the core change is a few lines in `graded_specs`** — mirror the `Rotor`
(even) entry with an odd one:

```python
if n >= 3:  # odd part {1,3,...}; for n<3 the odd part is just grade 1 (Vector)
    odd = tuple(b for b in bl if len(b) % 2 == 1)
    specs.append(TypeSpec(f"{ODD_NAME}{n}", odd, n, "graded"))
```

Then `make generate` regenerates `g3.py` with the new class + all the rules + the
return-type resolution, **no generator rule-writing**, **no hand-edited output**.

## What it buys

- `Vector3 * Bivector3`, `Rotor3 * Vector3`, `Rotor3 * Trivector3` (and their
  symmetric partners) return a **proper named type** instead of widening to `G3`.
  Type completeness: no common product mysteriously falls back to the full
  algebra. Good for a teaching library and for anyone composing these directly.
- The rotor sandwich's *intermediate* becomes that named type rather than
  `G3`/`Gn` — cleaner to read and reason about.
- The new type gets named `coeff_*` fields and basis constants like the others.

## Honest impact on mvp's remaining "hacks" (set expectations)

You hoped this "could probably make the few hacks remaining in mvp go away."
After the `sandwich` refactor, **mvp's rotations already have no hacks** — they're
thin wrappers over `rotor_rotation`, and the one grade projection lives in
`base.sandwich` (correct, documented). Modeling `{1, 3}` **does not remove that
projection**, because:

- The sandwich `R v R⁻¹` is grade-preserving **only because R is a versor**,
  which the type system can't track statically. So even with the odd type,
  `Rotor3 * Vector3` types as `{1,3}` and `{1,3} * Rotor3` types as `{1,3}` — the
  result is the odd type, **not** `Vector3`. `base.sandwich` still projects to
  `type(x)` to hand back a pure `Vector3`. (That projection is mathematically the
  right operation, not a hack — and it lives in gacalc, not mvp.)
- The other mvp coercions (`.scalar_part()` because `dot` returns a `Scalar`
  multivector; `float()` because gacalc is symbolic-first) are **unrelated** to
  this gap and are unaffected.

**Bottom line:** this is a worthwhile *gacalc type-completeness/precision* change,
and it makes the sandwich's intermediate a named type — but it won't materially
change mvp's code, which is already clean. Worth doing for gacalc's own sake; not
a silver bullet for the symbolic→float boundary.

## Work plan

1. **Explore/confirm in a notebook** (`notebooks/displaygraded.py` or a scratch
   script): symbolically evaluate `Vector3 * Bivector3`, `Rotor3 * Vector3`,
   `Rotor3 * Trivector3`, confirm support `{1, 3}` and eyeball the closed forms
   (sanity, not for hand-coding — the generator derives them).
2. **Register the type** in `graded_specs(n)` (the snippet above). Name TBD
   (decision below).
3. **`make generate`** → `g3.py` (and `g4.py` if `ALGEBRAS` includes it) grow the
   new class; products auto-resolve to it. Inspect the regenerated source.
4. **Tests:** add the new type to `tests/test_graded.py` (return-type + value per
   operation), and to the `SPECIALIZED` map in `tests/test_conformance.py` if it
   should run the shared conformance suite. Run `make test`; `make check-generated`
   (determinism). `ty`/`ruff` clean.
5. **Docs/notebook:** extend `notebooks/displaygraded.py` to show the new type and
   its products; update the README "Graded subtypes" table + the return-type
   tables; note it in `CLAUDE.md`'s graded-types description.
6. **(Optional) re-verify the sandwich path**: `Rotor3 * Vector3 * Rotor3` now
   goes through the odd type instead of `G3`; `base.sandwich` still returns
   `Vector3`. Confirm the gacalc + mvp suites stay green (no behavior change,
   tighter intermediate types).

## Decisions for you

1. **Name.** The even part is `Rotor{n}`; the odd part has no standard name.
   Options: `Odd{n}` (concise, mirrors "even/Rotor"), `VectorTrivector{n}`
   (descriptive, matches the grade-naming of `Bivector`/`Trivector`), or a
   Hestenes-flavored term you prefer. (Note: it's a graded *subspace*, not a
   subalgebra — odd·odd = even — same as `Bivector` isn't closed; that's fine.)
2. **Scope.** Just the **odd part `{1,3}`** (the product gap), or go for **full
   completeness** and also model the combinations that arise from *addition* —
   `{0,1}` (paravector), `{1,2}`, `{2,3}`, `{0,3}`, … which currently widen too?
   Recommend the odd type **first** (it's the one products hit and the one behind
   the sandwich widening); treat full completeness as a separate, larger follow-up.
3. **Generalization.** Define it as "the odd-grade subspace" (mirrors `Rotor` =
   even subspace) so it's right for 𝒢₃ *and* any future 𝒢₄+ — vs. hardcoding
   `{1,3}`. Recommend the subspace rule, gated `n >= 3` (for `n < 3` the odd part
   is just grade 1, already `Vector`).

## Cost note

Generation runs the general `Gn` symbolic products; adding a graded type adds its
row/column of product derivations. 𝒢₃ regen is tens of seconds today; this grows
it modestly. Paid once at generate time; the generated code stays fast.
```
```
