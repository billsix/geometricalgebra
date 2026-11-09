# Use match statements and modern Python features where appropriate

**Created:** 2026-06-05 · **Completed:** 2026-06-05

The codebase was surveyed for `if/elif/else` chains that read better as structural `match`, and for
other modern-Python features that help readability or correctness. Candidates were listed for
per-item go-ahead before editing; items A–F were applied and G was split into its own task.

## Findings

- **Python floor was already 3.13:** `base.py` imports `typing.TypeIs` (3.13); the container ran
  3.14. So `match`, `Self`, `X | Y` unions and `TypeIs` were all available, but `pyproject.toml`
  declared no `requires-python`.
- **Genuine `match` candidates were few.** Every structural-dispatch site already used `match`
  (`decrease_grade`, `__mul__`/`__rmul__`, `reject`/`reflect`). The remaining chains (`project`'s
  `is_scalar`/`is_r_vector`, the generator's `term_grade_key` and `format_assignment`) are predicate
  guards, where `match` would be churn, so they were left alone.

## What changed

- **A.** `__mul__`/`__rmul__` (`base.py`): identical `case int()` and `case float()` bodies merged
  into `case int() | float() as n:`.
- **B.** `decrease_grade` (`gn.py`): identical `case ():` and `case (a,):` bodies merged into
  `case () | (_,):` ("a scalar or single basis vector is already canonical").
- **C** (the maintainer's go-ahead, 2026-06-05). `reject`/`reflect`: `case _ as sequence if
  isinstance(away_from, Sequence):` became the structural `case [*sequence]:`, and the redundant
  `assert isinstance(...)` lines went.
- **D — `slots=True`** (go-ahead 2026-06-05). Feasibility was checked first: no `cached_property`/
  `lru_cache`, no `__dict__`/`vars`/`setattr` or dynamic attributes, no instance state on the ABC, no
  copy/pickle, `DIMENSION` is a `ClassVar`. Three coordinated changes: `__slots__ = ()` on
  `AbstractMultiVector` (so slotted subclasses don't inherit a `__dict__`),
  `@dataclasses.dataclass(slots=True)` on `Gn`, and the generator emitting
  `@dataclasses.dataclass(eq=False, slots=True)` for G1/G2/G3. Instances have no `__dict__`,
  `__slots__` lists exactly the fields, and a typo assignment (`mv.bogus = 1`) raises
  `AttributeError`.
- **E.** The generator emits a `match r:` (with `case _:`) for `r_vector_part` instead of an
  `if r == k:` chain (`emit_structural` in `tools/gen_specialized.py`); g1/g2/g3 regenerated.
  `grades` stayed as independent `if`s: it tests several conditions, not single-value dispatch.
- **F.** `requires-python = ">=3.13"` was added to `pyproject.toml`. Under 3.13 semantics `ty` then
  flagged a latent bug: `"AbstractMultiVector" | Sequence["AbstractMultiVector"]` in
  `project`/`reject`/`reflect`, a string forward reference `|`'d with a real type that worked only by
  luck. It was fixed to one fully quoted forward reference,
  `"AbstractMultiVector | Sequence[AbstractMultiVector]"`.
- **G.** `from __future__ import annotations` (to drop forward-reference quotes) was split into
  `tasks/archive/2026/06/06/future-annotations-drop-forward-ref-quotes.md`, since it changes
  annotation semantics module-wide.

The pedagogical, textbook-faithful style was kept throughout, and the generated `g*.py` changes
were made in the generator, never in the output.

## Verification

After each batch: `ruff check`, `ty check src`/`tests`, and the full suite (124) green; after D,
both notebooks ran headless.
