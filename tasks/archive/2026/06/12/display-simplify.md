# Display simplification for G1/G2/G3

> **UPDATE (2026-06-11): the shared `.simplified()` / `.expanded()` primitive is BUILT** —
> `MultiVectorBase._map_coefficients` + `.simplified()` / `.expanded()` in `base.py` (map a
> sympy op over the coefficients via the blade-dict interchange; inherited by `Gn`/`G1`/`G2`/`G3`
> and the graded subtypes). Tested in `tests/test_conformance.py`. This task can now just *use*
> them rather than build the helper.

Status: **DONE 2026-06-12** · proposed 2026-06-04

> **Done.** `AbstractMultiVector._repr_latex_` (base.py, inherited by every
> representation — no regeneration) now renders the **simplified** view: it reads
> `self.simplified().to_blade_dict()` instead of `self.to_blade_dict()`, so the
> lazy classes (G1/G2/G3, graded subtypes) display coefficients in lowest terms
> (e.g. `sin²+cos² → 1`, or a bivector times its dual whose terms cancel) while the
> **stored fields stay untouched** (still lazy). The zero-check became `not d` (an
> empty simplified blade-dict ⇒ the value simplified to zero). `Gn` already
> eager-simplifies, so it's a cheap no-op there; display is not hot. Test:
> `test_repr_latex_shows_simplified` (stored stays raw, displayed is simplified).
> Full suite **221**, ty + ruff clean.
>
> **Decisions (the open questions):**
> - *Display only, or a `.simplified()` helper too?* — the helper already exists
>   (built earlier); this task just uses it. Display now simplifies via it.
> - *`__repr__` too?* — **No.** Left `__repr__` as the raw dataclass repr
>   (`Vector2(coeff_e_1=…, …)`) — it's the honest stored state for debugging;
>   `_repr_latex_` is the pretty, user-facing render. Only the latter simplifies.
> - *Cost acceptable?* — yes (display-only; one simplify pass per shown value).
>
> **Overlap:** this largely covers the *display* half of
> `tasks/graded-bivector-dual-simplify.md` — a bivector×dual now renders cancelled
> automatically in any notebook cell, with no explicit `.simplified()` call. That
> task is now mostly the symbolic-confirmation + an optional explicit cell.

## Background

In the specialized-multivector work (see `tasks/archive/specialized-multivectors.md`) the coefficient
policy was "symbolic, but lazy simplify": `Gn` eager-simplifies; `G1`/`G2`/`G3` simplify lazily.
Decision 1 said the specialized classes should "simplify **on display**" as well as on equality.

We implemented lazy simplify on **equality** (their `__eq__` simplifies the per-blade difference),
but **display was never done**: `G1`/`G2`/`G3` inherit `AbstractMultiVector._repr_latex_` (in
`base.py`), which renders the raw, lazily-unsimplified coefficients. (sympy still auto-simplifies
trivially, so it's not wrong — just potentially not in lowest terms.)

## The decision

Do we want specialized values to fully `sympy.simplify` their coefficients when displayed
(`_repr_latex_`, and maybe `__repr__`)?

## Sketch if yes

- Override `_repr_latex_` on `G1`/`G2`/`G3` (generated) to render a simplified view — e.g. build a
  blade-dict with `sympy.simplify` applied, then reuse the base rendering logic. Keep the stored
  fields untouched (still lazy); only the displayed form is simplified.
- Alternatively, give the ABC `_repr_latex_` a small hook (e.g. simplify `to_blade_dict()` values
  before formatting) controlled by a class flag, so only the specialized classes opt in.

## Open questions

- Display only, or also a `.simplified()` helper returning a new fully-simplified instance?
- Is the extra simplify cost acceptable on display (display is not hot, so almost certainly yes)?
