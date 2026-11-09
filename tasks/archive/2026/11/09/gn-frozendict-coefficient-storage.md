# Store `Gn`'s coefficients in a `frozendict`, raise `requires-python` to 3.15, inline `BladeReal`

**Done:** 2026-11-09
**Priority:** 5
**Difficulty:** 3
**Source:** `tasks/archive/2026/11/09/frozendict-research-and-fit.md` (the research and
measurements)

## Summary

`Gn.coefficient_of_blade` became an immutable `frozendict` (the built-in of PEP 814, new in Python
3.15), so a caller writing into a `to_blade_dict()` result can no longer corrupt the value or a
shared constant such as `e_1`. `Gn.to_blade_dict()` returns the stored mapping with no copy.
`requires-python` rose to `>=3.15`. As a final step the `BladeReal` alias was deleted, and every
use now writes `Mapping[Blade, Real]`. The current state and its rationale are in
`tasks/reference/blade-dict-interchange.md` › "Immutable storage".

## What changed

- `src/gacalc/gn.py`: `__post_init__` wraps the zero-pruning comprehension in `frozendict(...)`.
  `to_blade_dict()` returns `self.coefficient_of_blade`. The field stays typed
  `Mapping[Blade, Real]`, so `Gn({...})` with a dict still type-checks.
- `src/gacalc/base.py`: the blade-dict contract (read-only, canonical keys, zero omission, the
  graded silent-drop) moved from the alias's `#:` comment into the `MultiVectorBase` class
  docstring, and `to_blade_dict`, `from_blade_dict` and `_require_canonical_blades` point there.
  The contract went on the class rather than on the abstract `to_blade_dict` because the
  generator copies the abstract method docstrings into every generated class. On the method it
  would have added 26 lines to every generated `to_blade_dict`.
- `src/gacalc/nbplotutils.py` › `_expand_numerators_dict`: `out: dict[Blade, Real] = {}` (it
  writes into the dict it builds).
- `tests/test_multivector.py`: `test_to_blade_dict_is_a_copy` became
  `test_to_blade_dict_is_immutable` (a write raises `TypeError`; `e_1` is unchanged).
- `pyproject.toml`: `requires-python = ">=3.15"`. With the bump, `ruff format` drops the
  parentheses in multi-exception `except` clauses (PEP 758), so it reformatted
  `src/gacalc/nbplotutils.py` and `tools/check_annotations.py`. No ruff or `ty` version setting,
  CI workflow or README install note named an older Python.
- `BladeReal` inlined in about 75 sites: `src/` (`base.py`, `gn.py`, `transforms.py`,
  `nbplotutils.py`), `tests/` (`test_blade_dict.py`, `test_conformance.py`,
  `test_multivector.py`), `tools/derive_lean_algebra.py` and `tools/gen_specialized.py`, plus
  `CLAUDE.md`, `README.md` and three reference docs (`blade-dict-interchange.md`,
  `scalar-vs-real-naming.md`, `type-annotation-exemptions.md`). Each file imports `Mapping` from
  `collections.abc`, and `Blade`/`Real` from `gacalc.base`, where it didn't already.
- **The generator** emits `parse_expr("Mapping[Blade, Real]")` in place of `name_ref("BladeReal")`,
  writes `Mapping[Blade, Real]: …` in its `Returns:` text, and imports `Mapping` and `Blade` in
  the generated header. Compared with the output before the step, g1–g3 changed only in these
  ways: the alias was spelled out (15 `to_blade_dict` signatures, 30 `left`/`right` annotations,
  12 `d` annotations, 12 `Returns:` lines), the header imports, and the inherited docstrings'
  pointer to `MultiVectorBase`.
- `CHANGELOG.md` `[Unreleased]`: BREAKING entries for the Python 3.15 floor and for the immutable
  `to_blade_dict()` result. `BladeReal` was itself an unreleased rename of `BladeCoef`, so the
  existing "`Coef` → `Real`, `BladeCoef` → `BladeReal`" entry now reads "`BladeCoef` removed;
  write `Mapping[Blade, Real]`". The earlier "Fixed" entry for the shared-state bug now says a
  caller can no longer corrupt a `Gn` through `to_blade_dict()`.

## Checks

- No writes into a `to_blade_dict()` result outside the repo. mvp
  (github.com/billsix/modelviewprojection) uses no `to_blade_dict`, `BladeReal` or `BladeCoef`
  outside `book/docs/_gacalc_src/`, its copy of gacalc's own source.
- Gates after the frozendict change: `make test` (775 passed, 2 skipped), `make format`,
  `make check-notebooks` (0 errors), `make check-generated` (deterministic) and `make docs`, all
  passing.
- Gates after inlining `BladeReal`: the same five, all passing (`make test` 775 passed, 2 skipped).
  The first `make format` run failed on four lines over 88 columns, three of which ruff
  rewrapped; the fourth, a test docstring, was reflowed by hand.

## Decisions

1. Go ahead, as part of a committed batch with `tasks/frame-derived-orthogonal-set-and-tuple-field.md`
   (William Emerison Six <billsix@gmail.com>, 2026-11-09: "make a branch do the
   gn-frozendict-coefficient-storage task, commit it, archive it"). The research task made the two
   design decisions (raise `requires-python` to 3.15 with no fallback; immutable `Gn` storage).
2. As the final step, remove the `BladeReal` alias and write `Mapping[Blade, Real]` everywhere it
   was used (William Emerison Six <billsix@gmail.com>, 2026-11-09: "as a final step, remove the
   'BladeReal = Mapping[Blade, Real]', and just inline 'Mapping[Blade, Real]' everywhere 'BladeReal'
   is used").
3. `Gn` gets no `__hash__`: its `__eq__` is value equality (it simplifies the difference), so a
   structural hash would break the hash contract.
