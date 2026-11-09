# Annotation auditor: fix its blind spots, then re-baseline the floor

**Priority:** 4
**Difficulty:** 2
**Source:** tasks/review/2026/11/08/repo-review.md §5.2, §4.3, §5.4 (the unannotated bindings the auditor misses)
**Created:** 2026-11-06 (William Emerison Six <billsix@gmail.com>): "make a task to investigate
tools/check_annotations.py reports 43 findings, but tasks/reference/type-annotation-exemptions.md still
says the floor is 32, and to make a decision to either fix something that's broken, or update the md
file to reflect the reality".

## Summary

`tools/check_annotations.py` reported 43 rows against a documented floor of 32, and the review's
§5.2 found it blind to whole classes of unannotated binding. The auditor was fixed to see them
(which raised the count to 105 rows in 31 files), 66 of those rows were real gaps and were
annotated, and the remaining 39 rows in 16 files are the new documented floor in
`tasks/reference/type-annotation-exemptions.md`: 13 classified-out (10 aliases, 3 enum members)
and 26 listed exemptions.

## Decisions

1. The auditor stays a report, not a gate: it always exits 0 and no `make` target runs it.
   `CLAUDE.md` › "Coding standard (Python)" no longer calls it enforcement (William Emerison Six
   <billsix@gmail.com>, 2026-11-09: "change the wording to not call it enforcement").
2. `uniform_scale(m)` and `scale_non_uniform(*factors)` were widened from `float` to `Real`. Typing
   `tests/test_matrix_template.py`'s symbols as `sympy.Symbol` showed the tests pass symbolic factors,
   which the functions already handled; `plane_rotation` already typed its angle as `Real`. A
   `CHANGELOG.md` `[Unreleased]` › Changed entry records it.
3. `tests/test_odd3.py`'s `versor` joined the §5 exemption next to `conjugated`: declaring it
   `g3.Versor` breaks the same `sympy.simplify` line. The in-code comment covers both.
4. The six `sympy.symbols` unpacks in the pyright-checked `notebooks/` stay undeclared (new
   exemption §6). The first full `make check-notebooks` run after the codemod failed with 9
   pyright errors: once the names are typed `sympy.Symbol`, pyright resolves `a_1 * e_1` through
   sympy's `Expr.__mul__` (an `Expr`) instead of the multivector's `__rmul__`. The codemod's edits
   to `notebooks/displayg2.py`, `displayg3.py`, `displayrotations.py` and `displayvectorcalc.py`
   were reverted, and a comment above each unpack gives the reason. `ty` doesn't make this
   mistake, so the declarations stay in `tests/`, `src/` and `book/docs/notebooks/`.

## What was done

- **The auditor (`tools/check_annotations.py`)**, the four §5.2 defects:
  - annotated names are tracked per scope (module, class body, each `def`), not per file, so an
    annotated `x` in one function no longer hides an unannotated `x` in another;
  - unpacking and chained assignments (`a_1, a_2 = sympy.symbols(...)`) are reported as LOCAL,
    and unpacked `for` targets name every unannotated name (nested and starred targets included);
  - gitignored files are excluded (via `git ls-files`), as its docstring had claimed;
  - the docstring says it is a report that no `make` target runs.
- **The 66 gaps**, fixed across 22 files in `src/`, `tools/`, `tests/`, `notebooks/` and
  `book/docs/notebooks/`:
  - the `sympy.symbols` unpack names declared `sympy.Symbol` on the lines above, by the
    idempotent codemod `tasks/adhoc/annotation-auditor-floor-drift/declare_symbol_unpacks.py`
    (a second run changed nothing), then reverted in the four pyright-checked notebooks
    (decision 4);
  - the rest by hand: loop-target declarations, `Figure`/`Axes` for `plt.subplots`,
    `sympy.cse`/`sympy.fraction` results, the generator's closure locals, and nine read-only
    `list`/`set` parameters widened to `Sequence`/`AbstractSet` (`tests/test_frame.py`,
    `tests/test_frame_class.py`, `tools/render_epix_figures.py`). Two bare `frame: list`
    annotations in `tests/test_frame.py` gained their element type.
- **The reference doc** was re-baselined to 39 rows in 16 files, its §5 duplicate `conjugated`
  bullet was merged, §6 was added, and the floor paragraph names this record.

## Verification

- `python tools/check_annotations.py`: 39 findings in 16 files, every one classified out or listed.
- On the host: `ruff check` and `ruff format --check` clean; `ty check` clean on
  `--no-respect-ignore-files src`, `tests`, `tools` and `book/docs/notebooks`.
- The generator's g1–g3 output is byte-identical before and after its annotation edits (the HEAD
  generator and the edited one, run on the host and compared with `cmp`).
- Container gates: `make test` 775 passed, 2 skipped; `make format` exit 0. `make check-notebooks`
  first failed (decision 4), then passed after the revert: 0 errors and the same 42 warnings as
  before, re-run with the target's own `podman run` line against the built image.
