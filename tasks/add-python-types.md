# Add Python type annotations to local variables (source + generator)

**Status:** in-progress
**Started:** 2026-06-05

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

## Open questions

- How aggressive? Annotate *every* reasonable local, or only the ones where the type is genuinely
  non-obvious (lighter touch, less visual noise)?
- For the generator's emitted temporaries (`cse` results), is an annotation worth it given they're
  short-lived closed-form intermediates?
