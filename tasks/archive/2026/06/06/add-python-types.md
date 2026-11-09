# Add Python type annotations to local variables (source + generator)

**Created:** 2026-06-05 · **Completed:** 2026-06-06
**Superseded:** the "light-touch typing" policy below was replaced by the "annotate every binding" rule (see `tasks/reference/python-coding-standard-gacalc.md` and `tasks/reference/type-annotation-exemptions.md`).

Type annotations were added to **local variables** (signatures were already well annotated) across
`src/` and `tools/gen_specialized.py`, and the generator was taught to emit annotations into the
generated `g*.py`. Candidate sites were surveyed and proposed before applying.

## Decisions

- **Light-touch policy** (agreed with the maintainer): annotate non-obvious locals (blade-dict
  structures, sums seeded with `type(self).zero()`, match-bound intermediates); skip obvious
  literals, counters, strings, and unpacking.
- **Generated `cse` temporaries stay unannotated**: annotating them would stamp `: numbers.Real` on
  every arithmetic line of short-lived closed-form intermediates.
- Generated annotations come from the generator, never from editing `g*.py`.
- The `from __future__ import annotations` treatment for `gn.py` and the generator was folded in
  from `tasks/archive/2026/06/06/future-annotations-drop-forward-ref-quotes.md` (#6), since this task
  already touched both files. The module-level `MultiVectorFn` alias stayed quoted (a runtime
  assignment; PEP 563 does not apply). The pass was coordinated with
  `tasks/archive/2026/06/05/use-match-and-modern-python.md` so the same lines were not churned twice.
- **Scoped out** as low value / high churn: the ~9 `ap = lines.append` aliases, the transient
  `str`/`int`/`list[str]` locals in the emit helpers, and most of the repetitive notebook-demo locals.

## What changed

- **`base.py`:** `product: AbstractMultiVector` (its inline comment moved above to stay ≤ 88 cols).
- **`gn.py`:** `from __future__ import annotations`; unquoted `rhs`/`product`/`-> Gn`. The
  `sorted_blade_dictionary_entry` annotation was dropped: it pushed the line to 89 chars for
  marginal value, and the name is self-describing.
- **`transforms.py`:** `cls: type[AbstractMultiVector]` (×2), and `rot_90`/`parallel`/
  `perpendicular`/`plane: AbstractMultiVector`.
- **`nbplotutils.py`:** a representative subset (`blade_dict: BladeCoef`, `rng: np.random.Generator`,
  `x: float | None`, `df`/`df_latex: pd.DataFrame`, plus the `BladeCoef` import). Skipped: the
  repeated `ex`/`ey`/`origin`/`vertices` boilerplate across the five near-identical `draw_*` demos,
  and the `blades`/`coefs` locals (they raised list-invariance / numeric-ABC errors under `ty`).
- **`gen_specialized.py`:** (a) emits `result: <Class>`, `left`/`right: Gn`, and
  `left`/`right: <FullClass>` in the dispatch fallback; (b) emits `from __future__ import
  annotations` into every generated module (`header()` and `SCALAR_HEADER`) — the dataclasses still
  detect the `DIMENSION` `ClassVar` from the string annotation, as the conformance suite confirmed;
  (c) annotates its own type-resolution locals in `graded_specs`/`resolve`/`product_result`/
  `unary_result`/`_renamer`, with a `BladeCoef` import.

## Verification

`ty check src`/`tests` clean, `ruff check src tools tests` clean, generated files regenerated, 141
tests pass.
