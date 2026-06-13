# Prove |ab| = |a||b| (any dimension) and use it to simplify the rotor's product magnitude

**Status:** proposed — not started
**Created:** 2026-06-13

## Goal

Develop a way to **prove that the magnitude of two vectors multiplied together
equals the product of their magnitudes** — `|a b| = |a| |b|` for the geometric
product. The proof: one side is the magnitude squared; the other is the magnitudes
squared times `(cos² + sin²)`, and distributing gives the **dot product** squared
plus the wedge squared. That equality lets you reduce between the two forms and
square-root something that doesn't *look* square-root-able but is.

Then **use this** to let the rotor handle the product of two vectors in a way that
**satisfies the type system** — so `rotor_from_vectors` can use

```
... abs(from_vec * to_vec)          # magnitude of the product
```

instead of

```
... abs(from_vec) * abs(to_vec)     # product of the magnitudes
```

(equal by the proof), which is the cleaner form for the **half-angle bivector**
construction.

Wanted progression: prove it for **2D**, then **recursively for 3D**, and ideally
produce a proof for **any number of dimensions**.

**Note:** the existing system already works — this is a refinement for type-system
cleanliness and the half-angle bivector calc, not a bug fix.

## The math (Bill's sketch)

```
a b = a·b + a∧b ,   a·b = |a||b|cosθ ,   |a∧b| = |a||b|sinθ
|a b|² = (a·b)² + |a∧b|² = |a|²|b|²cos²θ + |a|²|b|²sin²θ
       = |a|²|b|² (cos²θ + sin²θ) = |a|²|b|²
⇒  |a b| = |a| |b|.
```

The named identity `|a|²|b|² = |a|²|b|²(sin²θ + cos²θ)`, distributed into
`(a·b)² + |a∧b|²` (Lagrange), is what makes the product's magnitude clean to
square-root. **Recursion to 3D / general n:** two vectors always span a single
2-plane and `a b` lives in that plane's even subalgebra, so n-D reduces to 2D.

## Relevant gacalc code

- `MultiVectorBase.rotor_from_vectors` — `src/gacalc/base.py:686` (the shared
  construction; specialized reps may override — see codegen note).
- `MultiVectorBase.sandwich` — `base.py:755`; `MultiVectorBase.rotate` — `base.py:655`;
  `rotor_rotation` wraps them — `src/gacalc/transforms.py:385`.
- `MultiVectorBase.__abs__` (= `magnitude`) — `base.py:215`/`229`; `magnitude_squared`
  — `base.py:238`. `abs(from_vec * to_vec)` is `__abs__` of the geometric product.
- The geometric product `vector * vector` returns the **even / Rotor type** (see
  `g1.py:309`) — so the "type system" angle is: `abs()` of that even-grade product
  yields a scalar `Coef`, and the proof justifies the implied square root.

## Plan

- [ ] **Write the 2D proof precisely** (scalar + bivector parts → Pythagorean
      reduction to `|a||b|`).
- [ ] **Recursive 3D proof** — reduce to the 2-plane spanned by `a`, `b`.
- [ ] **General n-D proof** — state + prove for arbitrary dimension. gacalc's
      symbolic vectors make this tractable: `sym_vec2_1/2`, `sym_vec3_1/2`,
      `sym_vec_plane` (`gn.py:194–200`) over sympy coefficients — e.g. show
      `simplify(magnitude_squared(a*b) - magnitude_squared(a)*magnitude_squared(b)) == 0`,
      generalized via `Gn` with symbolic vectors.
- [ ] **Decide the proof's form** — a symbolic check in `tests/` and/or a worked
      derivation in a docstring (remember `--doctest-modules` runs docstring
      examples as tests).
- [ ] **Apply to `rotor_from_vectors`** — use `abs(from_vec * to_vec)` in place of
      `abs(from_vec) * abs(to_vec)`, type-checking cleanly. If the method is
      code-generated for the specialized reps, edit the **source/template** and
      regenerate (don't hand-edit `g2.py`/`g3.py`).
- [ ] **Regression-verify** against the current implementation (the system works
      today — rotors/rotations must come out identical).

## Notes / decisions

- Moved here from modelviewprojection per Bill's correction — this is native gacalc
  work (the rotor primitives + magnitude live here); mvp consumes it via the
  `mathutils.py` façade and needs no task of its own.
- Codegen + doctest constraints apply (see `CLAUDE.md`): specialized reps are
  generated, and docstring examples execute under `--doctest-modules`.
- Pedagogically this "reduce between two forms" result could anchor a docs section
  once proven.

## Open questions

- Deliverable form: a symbolic proof (sympy/test), a written/docstring derivation,
  or both? "A proof for any dimension" favors something that generalizes.
- Confirm the exact algebraic shape of the target expression against the current
  `rotor_from_vectors` body before changing it.
- Does `abs(from_vec * to_vec)` already type-check (just needs the proof to justify
  the sqrt), or does anything in the magnitude path need adjusting for the
  even/Rotor product type?
