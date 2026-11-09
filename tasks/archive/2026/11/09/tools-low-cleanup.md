# `tools/` low cleanup: generator dead code and history comments, ePiX tool gaps, the hypothesis detector removed

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §5.4
**Decision** (William Emerison Six <billsix@gmail.com>, 2026-11-09): delete
`tools/detect_unused_hypotheses.py`. Lean's `unusedVariables` lint and the delete-and-rebuild method
cover it.

## What changed

- **Generator (`tools/gen_specialized.py`, `tools/astbuild.py`):**
  - `term_grade_key`'s docstring now matches the code: a constant term sorts last, and any other
    symbol raises.
  - The unused `owner` parameter of `result_block_stmts` is gone, along with its six call sites'
    arguments.
  - `full_name_for(dim)`, which ignored `dim`, was inlined as `"G"`.
  - `return_construct` lost its unreachable non-`final` branch and `final` parameter (the only caller
    passed `final=True`), and `astbuild.construct_type_self` was deleted.
  - The seven history comments describe the present.
  - The one-off `ScalarN` spelling became the `Scalar_n` placeholder `CLAUDE.md` uses. The emitted
    scalar docstring names the real class, `Scalar`.
  - Already fixed, so dropped: `ROTATE_90_METHOD_DOC` is emitted.
- **`tools/check_epix_keywords.py`** also checks the book notebooks that draw ePiX figures live
  (`book/docs/notebooks/*.py` mentioning `epix`). It reports unknown callees only in figure files,
  because the rest of a notebook is gacalc code. Both notebooks pass. Chained calls are still
  skipped.
- **`tools/render_epix_figures.py`** reports a `FileNotFoundError` and goes on to the next figure.
  After a full render it deletes outputs whose figure file is gone (none today).
- **`tools/detect_unused_hypotheses.py`** was deleted. Its mentions in
  `tasks/reference/lean-ga-proof-architecture.md` and `tasks/lean-proofs-remove-extras.md` are
  updated.

## Verification

- Regenerating `g1.py`–`g3.py` before and after the change differs only in the scalar docstring line,
  one line per module.
- `make check-generated` (determinism), `make check-regions`, `make format` and `make test` (775
  passed) pass.
- One slip, caught: an early regeneration crashed after `g1.py` on a leftover `owner=` argument.
  Hidden output made `g2`/`g3` compare as "identical" until their timestamps showed they hadn't been
  rewritten.
