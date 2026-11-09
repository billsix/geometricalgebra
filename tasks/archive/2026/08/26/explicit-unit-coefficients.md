# Make implicit unit coefficients explicit in basis-blade sums (`e_1` → `1 * e_1`)

**Created:** 2026-08-26 · **Completed:** 2026-08-26

## Goal

For educational clarity, every coordinate term in a multivector sum was made to read as
`coefficient * basis`: `e_1 + 3 * e_2` → `1 * e_1 + 3 * e_2`, `2 * e_1 + e_2` → `2 * e_1 + 1 * e_2`,
so a student sees each coordinate the same way instead of guessing that a bare `e_1` means
`1 * e_1`. The change is purely cosmetic (`1 * e_1 == e_1`). It was run as a trial: Phase 1 first,
the maintainer reviewed the look, and only then were Phase 2 and the `CLAUDE.md` update done.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-26)

1. **All multi-term sums**, not only the mixed case: `e_1 + e_2` → `1 * e_1 + 1 * e_2`.
2. **Negatives too:** `2 * e_1 - e_2` → `2 * e_1 - 1 * e_2` (the `-` operator is kept); a lone
   `-e_2` term → `-1 * e_2`.
3. **Final rule, broadened at review** after the maintainer flagged the list-element inconsistency:
   make the implicit `1` explicit wherever a bare blade is a **coordinate vector** — (a) sum terms,
   (b) list/tuple elements, and (c) the vector args of `area`/`volume`/`signed_area`/`signed_volume`.
   A blade used as a **direction** stays bare (`cls.i(e_1, e_2)`, `plane_rotation(…)`,
   `rotor_from_vectors(…)`, `project(onto=e_1)`, `coefficient(e_1)`). The original decision 3
   ("standalone single terms stay bare") was the agent's recommendation under the maintainer's
   "whatever makes a cleaner API", and was superseded by this rule.

Scope: `tests/`, `notebooks/`, and `src/gacalc/*.py` docstrings/doctests, in every spelling of a
basis blade (`e_1`, `g2.e_1`, `Vector.e_1`, `G.e_123`). Left alone: the generated `g1`/`g2`/`g3`
modules (generated docstrings come from `base.py` via `inspect.getdoc`, so they were fixed at the
source), non-GA arithmetic, and `coeff_e_1=...` keyword calls. `book/` (textbook LaTeX math, not
gacalc code) and `README.md` (already explicit) needed nothing.

## What changed

- An AST codemod, `add_explicit_unit_coefficients.py` (removed at archive; in git history), walked
  `ast.BinOp(Add/Sub)` chains and inserted `1 * ` by source span, so formatting and comments were
  preserved; it also rewrote single-line `>>>` doctest inputs. A blind regex was rejected because it
  could not tell GA sums from non-GA `+`/`-`, strings, or comments.
- Phase 1 (`tests/` + `notebooks/`): 127 unit coefficients across 12 files. Phase 2 extended it to
  `src/gacalc/` docstrings and the broadened rule; ~235 unit coefficients in total over three passes.
- `CLAUDE.md`'s "Build vectors from the basis constants" convention was updated to state all three
  rules and the direction-stays-bare carve-out.
- The codemod was treated as one-shot (new code follows the convention by hand) and was `git rm`'d
  at archive rather than promoted to `tools/`.

## Verification

410 tests green with behaviour unchanged; ruff + ty clean; the codemod was idempotent (a second run
was a no-op, so `1 * e_1` never became `1 * 1 * e_1`).
