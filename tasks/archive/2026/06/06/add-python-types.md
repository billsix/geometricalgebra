# Add Python type annotations to local variables (source + generator)

**Status:** complete
**Completed:** 2026-06-06
**Started:** 2026-06-05

> **Completion note (2026-06-06).** Applied with the agreed light-touch policy (annotate NON-OBVIOUS
> locals; skip obvious literals/counters/strings and unpacking). `ty check src`/`tests` clean,
> `ruff check src tools tests` clean, generated files regenerated, 141 tests pass.
>
> - **base.py:** `product: AbstractMultiVector` (moved its inline comment above to stay ≤88).
> - **gn.py:** the folded-in future-annotations — added `from __future__ import annotations`,
>   unquoted `rhs`/`product`/`-> Gn`. Dropped the `sorted_blade_dictionary_entry` annotation (it
>   forced the line to 89 chars for marginal value — the name is self-describing).
> - **transforms.py:** `cls: type[AbstractMultiVector]` (×2), `rot_90`/`parallel`/`perpendicular`/
>   `plane: AbstractMultiVector`.
> - **nbplotutils.py:** representative subset — `blade_dict: BladeCoef`, `rng: np.random.Generator`,
>   `x: float | None`, `df`/`df_latex: pd.DataFrame` (added `BladeCoef` import). **Skipped** the
>   repeated `ex`/`ey`/`origin`/`vertices` boilerplate across the 5 near-identical `draw_*` demos, and
>   the `blades`/`coefs` locals (static list-invariance / numeric-ABC errors under `ty`).
> - **gen_specialized.py:** (a) **emitted** annotations into the generated `g*.py` — `result: <Class>`,
>   `left`/`right: Gn`, and `left`/`right: <FullClass>` in the dispatch fallback — but **not** the
>   `cse` temporaries (would stamp `: numbers.Real` on every arithmetic line). (b) Emitted
>   `from __future__ import annotations` into every generated module (both `header()` and
>   `SCALAR_HEADER`) for #6 consistency; the generated dataclasses still work (`DIMENSION` ClassVar
>   detected from the string annotation — conformance suite confirms). (c) Annotated the generator's
>   own core type-resolution locals (`graded_specs`/`resolve`/`product_result`/`unary_result`/
>   `_renamer`: `specs`/`candidates`/`want`/`rd: BladeCoef`/`support`/`rspec: TypeSpec`/`out_exprs`/
>   `a_syms`/`b_syms`/`result_mv: Gn`/`rename`/`token`), and added the `BladeCoef` import.
>
> **Deliberately scoped out** (low value / high churn, not worth the noise): the ~9 `ap = lines.append`
> aliases, the many transient `str`/`int`/`list[str]` locals in the emit helpers, and the bulk of the
> repetitive notebook-demo locals. The generated `cse` temporaries are intentionally left unannotated.

## Goal

Read through the source and add type annotations where it's reasonable to do so for **local
variables** — not just function signatures, which are already well annotated. The codebase already
annotates many locals (e.g. `left: BladeCoef = ...`, `inner: "AbstractMultiVector" = ...`), so this
extends an established style for legibility and to keep `ty` informative. Do the same for the **code
generator** (`tools/gen_specialized.py`): annotate its own locals, and — where it emits local
variables into the generated `g*.py` — have it emit annotations too, so the generated classes are
likewise typed. Per repo convention, survey and propose the concrete sites first, then apply what's
approved; keep `ty check src`/`tests` clean throughout.

## Plan

- [ ] Survey locals lacking annotations across `src/` (base.py, gn.py, transforms.py, nbplotutils.py)
      and `tools/gen_specialized.py`; note where a type is non-obvious enough that an annotation aids
      reading (skip trivially-inferable throwaways where it would just be noise).
- [ ] For the generator's *emitted* locals (e.g. the `cse` temporaries / `result = G2(...)` in
      `emit_bilinear`, and any `left`/`right` coercion locals), decide whether to emit annotations and
      what type to use (the field types are `numbers.Real`; the result is the class type).
- [ ] Present candidate sites as a reviewable list (file:line, proposed annotation) for go-ahead.
- [ ] Apply approved annotations. For generated code, change the **generator**, never `g*.py`; then
      regenerate (auto-formats) and diff.
- [ ] `ruff check`, `ty check src` + `ty check tests`, full suite (124) green.

## Notes / decisions

- Boundary to respect: `g1/g2/g3.py` are generated — their annotations come from the generator.
- Style already in use: annotate locals where the RHS type isn't obvious at a glance (dict/blade
  structures, sums seeded with `type(self).zero()`, match-bound intermediates). Don't annotate
  obvious literals/loop counters where it adds noise.
- Coordinate with `tasks/use-match-and-modern-python.md` (e.g. `X | None` syntax, `typing.Self`) so
  the two passes stay consistent and don't churn the same lines twice.
- `ty` is the type checker of record (per CLAUDE.md "keep `ty check` clean").
- **Folded in from `future-annotations-drop-forward-ref-quotes` (#6, base.py done 2026-06-06):** carry
  the `from __future__ import annotations` treatment into `gn.py` and the generator here, since this
  task already touches both. Add the import to `gn.py` (drop its `"AbstractMultiVector"` forward-ref
  quotes — `Gn` is a `@dataclass(slots=True)`, so confirm nothing introspects `__annotations__` for
  real types; the `__post_init__` only iterates the dict, so it's expected-safe), and have
  `tools/gen_specialized.py` **emit** the import at the top of every generated `g*.py` for
  consistency, then regenerate. The module-level `MultiVectorFn` alias stays quoted (runtime
  assignment; PEP 563 doesn't apply).

## Open questions

- How aggressive? Annotate *every* reasonable local, or only the ones where the type is genuinely
  non-obvious (lighter touch, less visual noise)?
- For the generator's emitted temporaries (`cse` results), is an annotation worth it given they're
  short-lived closed-form intermediates?
