# Graded types: make bivector * dual simplify (cancellation) — at least in the notebook

> **UPDATE (2026-06-11): the shared `.simplified()` / `.expanded()` primitive is BUILT** —
> `MultiVectorBase._map_coefficients` + `.simplified()` / `.expanded()` in `base.py` (map a
> sympy op over the coefficients via the blade-dict interchange; inherited by `Gn`/`G1`/`G2`/`G3`
> and the graded subtypes). Tested in `tests/test_conformance.py`. This task can now just *use*
> them rather than build the helper.

Status: **DONE 2026-06-12** · proposed 2026-06-11 (Bill)

> **Done.** Two parts:
> 1. **Can be / is simplified** — covered by `display-simplify` (archived
>    `2026/06/12/display-simplify.md`): `_repr_latex_` renders the simplified view
>    for every representation, so a bivector × its dual displays **cancelled
>    automatically**, no explicit `.simplified()` call needed. (And `.simplified()`
>    exists if a value is wanted.)
> 2. **Symbolic confirmation + teaching cell** (this task) — confirmed
>    `B · B.dual() = |B|² I` (a trivector); for a general bivector the closed form is
>    already clean (`(a²+b²+c²) e₁₂₃`), and the simplification *matters* when the
>    coefficients reduce. Added a cell to `notebooks/displaygraded.py`: a unit
>    bivector `B = cos(t)(e₁∧e₂) + sin(t)(e₁∧e₃)`, whose `B · B.dual()` *stores*
>    `(cos²t+sin²t)·e₁₂₃` (lazy) but **displays as `e₁₂₃`** — the cancellation shown.
>    (`import sympy` added to the notebook.) Notebook runs headless (exit 0), ruff
>    clean.

## Symptom (Bill, 2026-06-11)

For the graded subtypes, **a bivector times its dual should cancel terms out**, but
the displayed result currently doesn't — it shows uncombined/uncancelled symbolic
coefficients. Bill: the graded subtypes deliberately **don't eager-simplify**, but
he wants to **ensure the result *can* be simplified**, and that the **notebook does
it** (even if the notebook has to call simplify explicitly) so the cancellation is
visible.

## Why it happens (the design)

Graded subtypes (`Vector_n`/`Bivector_n`/`Rotor_n`/...) use the **lazy-simplify**
policy (simplify only on equality), unlike `Gn` which eager-simplifies in
`__post_init__`. So a product like `Bivector3 * Bivector3.dual()` lands with its
per-blade coefficients in raw, **un-`sympy.simplify`'d** form — terms that would
cancel (e.g. `a*b - b*a`) are left as-is, so the rendered multivector looks messier
than the true (cancelled) value. (`dual` of a `Bivector3` narrows to `Vector3`;
`Bivector3 * Vector3` has grade support `{1,3}` -> currently widens to `G3` — see
`tasks/model-odd-graded-type.md` — and that `G3` carries the unsimplified coeffs.)

## What to do (investigation + fix)

1. **Confirm the case symbolically** — in a REPL/notebook, build a symbolic
   `Bivector3` `B`, compute `B * B.dual()` (and maybe `B.dual() * B`), and show the
   raw coefficients vs `sympy.simplify`'d ones — verify simplify actually collapses
   them (and to what — likely a trivector / a `|B|^2`-type expression).
2. **Provide a simplify path on the graded types** (and `Gn`/`G1/2/3`) if missing —
   e.g. a `.simplified()` method returning a new instance with each coefficient
   `sympy.simplify`'d (stored fields untouched elsewhere; lazy policy preserved).
   This is the "ensure it *can* be simplified" half. (Mirrors the deferred
   `tasks/display-simplify.md`, and the `expanded()` helper in
   `tasks/show-mult-expand.md` — coordinate the three; they're the same shape:
   map a sympy op over `to_blade_dict()` -> `from_blade_dict`.)
3. **Notebook (`notebooks/displaygraded.py`)** — add/adjust the bivector-dual cell
   to display the **simplified** result (call `.simplified()` or `sympy.simplify`
   per coefficient), so the cancellation is shown even though the algebra stays
   lazy. This is the "notebook does it" half Bill explicitly asked for.

## Decisions for Bill

- **Where does the simplify helper live?** A `.simplified()` method on
  `MultiVectorBase` (works for every representation, discoverable) vs a
  notebook-local helper. Recommend a real method (small, broadly useful, and it
  unblocks `display-simplify` too).
- **Scope now:** just the bivector-dual notebook cell + the helper, or a broader
  "simplify on display" pass (that's `tasks/display-simplify.md`)? Recommend the
  **helper + the one notebook cell** now; leave display-wide simplify to its own
  task.

## Relationship

- Closely related to the deferred `tasks/display-simplify.md` (display-time
  simplify for `G1/G2/G3`) and `tasks/model-odd-graded-type.md` (why `Bivector3 *
  Vector3`/dual widens to `G3` today). The `.simplified()` helper is the shared
  primitive across this, `display-simplify`, and `show-mult-expand`.
