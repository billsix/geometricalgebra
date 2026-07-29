# Notebook: derive the cross product as a composed projection-rotation pipeline

**Status:** complete
**Completed:** 2026-07-17
**Created:** 2026-07-17 (retroactive — work was already done when the doc was written)

## Goal

Add a cell to one of the gacalc notebooks that *builds* the 3D cross product out of
nothing but `projection_rotation` and `project`, composed — no cross-product formula
hand-written — starting from two symbolic 3D vectors, to demonstrate the composable-function
layer (`ComposableFunction` / `@`) shipped in gacalc 0.0.9.

## What was done

Added a section to **`notebooks/displayrotations.py`** (the natural home — it already uses
`Gn` + `projection_rotation`); imported `ComposableFunction` from `gacalc.transforms`.

Construction (Bill's design):
- `a`, `b` = `Gn.symbolic_multivector(3, "a").r_vector_part(1)` (and `"b"`) — the grade-1
  part of a symbolic multivector, i.e. two symbolic 3D vectors.
- Four steps, composed with `@` (written reverse of application order):
  1. `align`   = `projection_rotation(a → e_1)`   — spin `a` onto `e_1`
  2. `perp`    = `project(e_2 ^ e_3)`               — drop the part along `a`, keep the ⟂ part
  3. `turn`    = `projection_rotation(e_2 → e_3)`  — the 90° turn in the ⟂ plane
  4. `unalign` = `projection_rotation(e_1 → a)`    — undo step 1
- `cross_over_norm_a = unalign @ turn @ perp @ align`; apply to `b`.

## Result (verified)

`cross_over_norm_a(b)` comes out as **(a × b) / |a|** exactly:

```
(a2*b3 - a3*b2)/sqrt(a1**2+a2**2+a3**2) e_1
+ (a3*b1 - a1*b3)/sqrt(...)              e_2
+ (a1*b2 - a2*b1)/sqrt(...)              e_3
```

The `/|a|` arises because every rotation is a *pure* `projection_rotation` (magnitude-
preserving) and `project` only drops a component — so the pipeline never multiplies in the
`|a|` a real cross product carries. Closing verification cell:
`(result * abs(a)).simplified() == (a ^ b).dual(n=3)` → **True** (the GA cross product is the
dual of the wedge).

## Follow-on tweak

Relabelled the four functions per Bill's convention — **subscript = "from", superscript =
"to"**: `R_{a}^{e_1}`, `P_{e_2 e_3}`, `R_{e_2}^{e_3}`, `R_{e_1}^{a}` (the projection was wrapped
in a `ComposableFunction` to replace its auto-generated `P_{1 e₂ e₃}` label). Pipeline renders
as `R_{e_1}^{a} ∘ R_{e_2}^{e_3} ∘ P_{e_2 e_3} ∘ R_{a}^{e_1}`.

## Verification

- Ran the cells standalone (symbolic, ~seconds): result + dual-equality check both correct.
- `ruff` + `ruff format` clean; `py_compile` OK. (Notebooks aren't collected by pytest, so no
  suite impact.)

## Notes

- The section reuses the local names `a`/`b`, shadowing the earlier rotation-demo `a`/`b` in the
  same notebook — harmless (cells run top-to-bottom; the earlier ones are done being used).
  Flagged to Bill; rename to `u`/`v` if the shadow is undesirable.
