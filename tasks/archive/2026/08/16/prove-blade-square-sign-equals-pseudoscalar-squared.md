# Prove the closed form == the pseudoscalar squaring, then optimize the helper to it

**Created:** 2026-08-15 · **Completed:** 2026-08-16

Phase 2 of `tasks/archive/2026/08/15/name-blade-square-sign.md`. Phase 1 had put the
**obviously correct** implementation in first: `pseudoscalar_squared_sign(r)` in `base.py` returned
`int(Gn.unit_pseudoscalar_squared(r).scalar_part())`, actually squaring the `r`-dimensional unit
pseudoscalar (in `Gn`, via a deferred import, since only a full algebra can build it). This task
proved the closed form equal to that and substituted it as the optimized version: "make it correct,
then make it fast".

## What was done

1. **Proof.** For `I_r = e_1 e_2 … e_r`, `I_r² = (−1)^(r(r−1)/2)` (Euclidean): reversing `I_r` costs
   `r(r−1)/2` adjacent transpositions, each `e_i e_j → −e_j e_i`, and each `e_i² = +1`. At the
   maintainer's request this became a full reference doc rather than a short note,
   `tasks/reference/pseudoscalar-square-sign.md`, hand-counted for grades 1–5 in ASCII, then the
   induction and the reversal one-liner, written for a high-school / early-college reader.
2. **Permanent equivalence gate:** `tests/test_pseudoscalar_square_sign.py` (3 tests) asserts over
   `r = 0..12` that `Gn.unit_pseudoscalar_squared(r).scalar_part() == (−1)^(r(r−1)/2)`. It squares
   independently, so it still guards the equivalence after the helper *became* the closed form.
3. **Optimization.** The helper body became `return (-1) ** ((r * (r - 1)) // 2)` and the deferred
   `from gacalc.gn import Gn` was removed, so the runtime callers went from squaring a pseudoscalar to
   O(1) and the `base → gn` coupling disappeared. Name and signature were unchanged. The old squaring
   line was kept as an in-code comment (William Emerison Six <billsix@gmail.com>, 2026-08-16), so a
   student sees that the closed form and the squaring are the same calculation.
4. **Book chapter** (the maintainer's request, 2026-08-16): `book/docs/blade-square-sign.rst`
   ("Squaring a Blade: The Sign, by Counting Flips"), in the `index.rst` toctree after
   `geometric-product`. The reference doc stays the contributor source of truth; the chapter is its
   reader-facing `.rst` sibling. Part 1 covers the blades (two rules, grades 1–5 in ASCII literal blocks
   with the running sign, the triangular-number `list-table`, the induction, the reversal `.. note::`).
   Part 2 covers coefficients in three visible steps, as the maintainer specified: scalars to the front
   and multiplied (`(a e_1)(b e_2)(c e_1) = a·b·c · e_1 e_2 e_1`), the blade rules on the basis part with
   the `+`/`−` shown on the right-hand side (`e_1 e_2 e_1 → −e_2`), then the sign in front
   (`−abc e_2`); it holds for symbols and numbers alike. Math via `.. math::`/`:math:`, ASCII-only
   diagrams for lualatex-PDF safety, and no notebook cell (the computational check is the unit test).
   Part 2 overlaps the general multiplication explanation of
   `tasks/archive/2026/10/09/redo-gn-multiplication-explanation-as-markdown.md`, and the two were
   cross-linked so they don't duplicate.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-08-16)

- **How far to optimize:** substitute the closed form everywhere, keeping the squaring line as a
  comment; the equivalence test is the living cross-check.
- **Proof write-up:** a full reference doc (above), referenced by the test.

## What got faster

Of the 4 call sites, the two generated `reverse()` emitters evaluate the helper at code-gen time and
bake a `±1` constant, so their output did not change at all. Only `Gn.reverse()` and `exp()` run the
helper per call, and they are where the optimization paid off. The change is a two-way swap of one
function body; git history records both forms.

## Verification

Host: 353 tests passed (including `reverse`/`exp`/conformance/graded and the `base.py` doctests); the
helper returned the same `±1` as the independent squaring for r = 0..12; ruff `check`/`format --check`
and `ty check src` clean; the generator regenerated with the baked `reverse` constant unchanged. The
container gate (`make test` / `make format` / `make check-generated`) was left to run at commit. The
book chapter built warning-free with a host `sphinx-build` (notebooks disabled); the only warnings
were the pre-existing `api.rst` autodoc `|A|`-substitution errors from `base.py` docstrings.
