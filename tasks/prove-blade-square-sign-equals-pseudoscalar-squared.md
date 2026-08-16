# Prove the closed form == the pseudoscalar squaring, then optimize the helper to it

**Status:** in-progress. **Phase 1 (`tasks/archive/2026/08/15/name-blade-square-sign.md`)
is DONE** — the named helper computes the sign the slow, obviously-correct way (actually squaring the
unit pseudoscalar). **Proof step DONE 2026-08-16** (William Emerison Six <billsix@gmail.com>): the
hand-counted + inductive proof is written as a reference doc
(`tasks/reference/pseudoscalar-square-sign.md`), and the permanent equivalence gate is
`tests/test_pseudoscalar_square_sign.py` (3 tests, green — squares `I_r` in `Gn` independently and
matches `(−1)^(r(r−1)/2)` for r=0..12). **Optimization DONE 2026-08-16** — the helper body is now the closed form
`(-1) ** ((r * (r - 1)) // 2)`, the deferred `from gacalc.gn import Gn` is removed (base→gn coupling
gone), and the old squaring line is kept as an in-code comment so it reads as a proof; verified (353
tests + base.py doctests green, ruff/ty clean; helper == independent squaring for r=0..12). Staged for
Bill's commit. **Remaining: only the reader-facing rst book chapter** (its own short chapter; see the
Book chapter section below). Created 2026-08-15 (William Emerison Six <billsix@gmail.com>).
**Priority:** 6
**Difficulty:** 3

## Direction (corrected 2026-08-15)

Phase 1 put the **obviously-correct** implementation in first: `pseudoscalar_squared_sign(r)` in
`base.py` returns `int(Gn.unit_pseudoscalar_squared(r).scalar_part())` — it *actually squares* the
`r`-dimensional unit pseudoscalar (in `Gn`, via a deferred import, since only a full algebra can
build it). This task proves the closed form equals that and swaps the closed form in as the
**optimized** version — the "make it correct, then make it fast" order.

## Goal — prove, then optimize (and it's fully reversible)

1. **Prove the equivalence. [DONE 2026-08-16.]** For the `r`-dimensional unit pseudoscalar
   `I_r = e_1 e_2 … e_r`, `I_r² = (−1)^(r(r−1)/2)` (Euclidean): reversing `I_r` costs `r(r−1)/2`
   adjacent transpositions, each `e_i e_j → −e_j e_i`, and each `e_i² = +1`. Written up as a
   hand-countable proof (grades 1–5 by hand with ASCII, then the induction, then the reversal
   one-liner) in `tasks/reference/pseudoscalar-square-sign.md`, per Bill's request (a full reference
   doc, not a 3-line note). Landed as the permanent gate `tests/test_pseudoscalar_square_sign.py`,
   asserting over `r = 0..12` that `Gn.unit_pseudoscalar_squared(r).scalar_part() == (−1)^(r(r−1)/2)`
   — an *independent* squaring, so it still guards the equivalence after step 2 makes the helper *be*
   the closed form. (3 tests, green.)
2. **Substitute the optimized form. [DONE 2026-08-16.]** Helper body is now
   `return (-1) ** ((r * (r - 1)) // 2)`; the deferred `from gacalc.gn import Gn` is removed, so the
   runtime callers (`Gn.reverse()`, `exp()`) go from squaring-a-pseudoscalar to O(1) and the `base →
   gn` coupling disappears. Name/signature unchanged — only the body. The old slow line is kept as an
   in-code comment (Bill, 2026-08-16) so a student sees the closed form and the pseudoscalar-squaring
   are the same calculation.
3. **Verify. [DONE 2026-08-16 on host.]** Full suite 353 passed (incl. `reverse`/`exp`/conformance/
   graded and `base.py` doctests); the helper returns the same `±1` as the independent squaring for
   r=0..12; ruff `check`/`format --check` and `ty check src` clean; generator regenerated fine (the
   baked `reverse` constant is unchanged). **Container gate** (`make test` / `make format` /
   `make check-generated`) is the belt-and-suspenders to run at/after commit.

## Scope — what actually gets faster (the maintainer's gen-time-constant point)

The sign is used at 4 sites, but they don't all pay at runtime:

- **Generated `reverse()` (both emitters in `tools/gen_specialized.py`)** — the generator evaluates
  the helper at **code-gen time** and bakes a `±1` **constant** into the emitted code. So the
  generated classes cost **nothing** at runtime *regardless* of the helper's body; this substitution
  doesn't change their generated output at all (same constant, just computed by formula instead of by
  squaring at gen-time).
- **`Gn.reverse()` and `exp()`** (non-generated, runtime) — these are the *only* callers that
  actually run the helper per call. They are where Phase 1's squaring is slow and where this
  optimization pays off.

## Book chapter (rst) — its own short chapter (Bill, 2026-08-16)

The reader-facing version of this proof becomes **its own short chapter** in the Sphinx book
(`book/docs/`, "Plotting On Crappy Graph Paper"), added to the `index.rst` toctree. **Keep both**:
`tasks/reference/pseudoscalar-square-sign.md` stays the contributor/agent source of truth (markdown),
and the book chapter is a reader-facing `.rst` sibling — ASCII diagrams in literal blocks, the inline
and display math upgraded to `:math:` / `.. math::` (LaTeX) so it typesets in HTML + PDF (lualatex).
**No notebook cell** — the computational check is the unit test, not in-book.

Chapter structure (two parts):

1. **Start with just the blades.** Port this doc's hand-counted proof: the three rules; grades 1–5
   move-by-move in ASCII with the running sign; the triangular-number tally; then the induction and
   the reversal one-liner. The pure-`e_i` case.
2. **Then a section: symbols (coefficients) × each basis vector.** Generalize to a product whose
   factors carry scalar/symbolic coefficients, e.g. `(a e_1)(b e_2)(c e_1)`, in three visible steps —
   the pedagogy Bill specified:
   - **Scalars to the front, all multiplied together** (coefficients commute past everything):
     `(a e_1)(b e_2)(c e_1) = a·b·c · e_1 e_2 e_1`.
   - **Then the normal blade rules** (swap/annihilate) on the basis part, tracking the sign, **with the
     `+`/`−` shown on the right-hand side** (the notation Bill liked): `e_1 e_2 e_1 → −e_2`.
   - **Then the sign goes in front of the scalars:** `−(a·b·c) · e_2 = −abc e_2`.

   Worked so it holds for symbols and numbers alike (a coefficient is just a number that commutes).

This second section overlaps `tasks/redo-gn-multiplication-explanation-as-markdown.md` (scalars-to-front
/ rules / sign is the general multiplication mechanism); coordinate the two so the chapter and that
explanation don't duplicate — cross-linked there.

**DONE 2026-08-16.** Written as `book/docs/blade-square-sign.rst` ("Squaring a Blade: The Sign, by
Counting Flips"), added to the `index.rst` toctree after `geometric-product`. Both parts present:
part 1 (blades — two rules, grades 1–5 in ASCII literal blocks with the running sign, the
triangular-number table via `list-table`, the induction, and the reversal `.. note::`); part 2
(numbers/symbols — the three-step `(a e_1)(b e_2)(c e_1) → −abc e_2`). Reader-facing math via
`.. math::`/`:math:`, ASCII-only diagrams for lualatex-PDF safety, no notebook (per Bill). Verified
warning-free with a host `sphinx-build` (notebooks disabled): cross-refs, math, table, and toctree all
resolve; the only build warnings are pre-existing `api.rst` autodoc substitution errors in `base.py`
docstrings (`|A|`-as-substitution), unrelated to this chapter.

## Undo / reversibility

This is a clean two-way swap of one function body (Phase 1 ↔ Phase 2): slow squaring ↔ closed form.
Either direction is a one-function edit plus a re-run of the gates; nothing else moves. Git history
(the Phase-1 commit and this one) records both forms.

## Open questions (for Bill) — RESOLVED 2026-08-16

1. **How far to optimize.** → Substitute the closed form **everywhere**, keeping the old
   pseudoscalar-squaring line as a comment (Bill wants the equivalence visible in the code for a
   student). The permanent equivalence test from step 1 is the living cross-check.
2. Should the proof also live as a written note in `tasks/reference/`? → **Yes — a full reference
   doc**, not a 3-line note: `tasks/reference/pseudoscalar-square-sign.md`, hand-counted for grades
   1–5 with ASCII plus both proof routes, written for a high-school / early-college reader. The test
   references it.
