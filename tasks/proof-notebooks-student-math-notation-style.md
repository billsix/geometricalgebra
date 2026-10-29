# Every proof gets a student-followable Python notebook that renders math notation

**Status:** proposed — needs go-ahead (on the plan + the granularity question below). This is an
**umbrella initiative**: a convention plus a **backfill** of the existing proofs. Standing preference
from William Emerison Six <billsix@gmail.com> (2026-10-29).
**Priority:** 5  (valuable, not blocking)
**Difficulty:** 6  (small per notebook, but there are many proofs to backfill — see the backlog)

## BLUF

The maintainer wants **every proof** to have a companion **Python notebook that a student can read,
follow, print, and check off** — where the Python is only the *engine* and the **rendered output is
ordinary math notation** (LaTeX/MathJax), walking the derivation **step by step** with the
intermediate pieces shown explicitly (e.g. a product expanded into its **pairwise term products,
each printed as math**). Scope is **not** future-only:

- **every proof that exists right now gets one** (a backfill of the current corpus);
- **every update to an existing proof gets one** (add it if missing, refresh it if present);
- **every proof added in the future gets one.**

This doc captures the preference, the convention to adopt, and the backlog to work through.

## What the maintainer asked for (verbatim intent)

- "I want all proofs ... to have python notebooks that do the same thing, symbolically, in a way that
  a student can understand and follow, and print out and check stuff off as they verify it."
- "find notebooks I made that take multiplications, and show the pairwise multiplications, that print
  them all out in markdown in the notebook. that's the style I want, for students to learn from."
- "the output formulas should be normal math notation that a student can understand. So the python is
  just there to drive the math notation for a student."
- Scope correction: "it's not every future proof, it's every proof that exists right now gets one, and
  every update to an existing proof gets one, and ones added in the future get one."

## The style, from existing exemplars (read these first)

- **`notebooks/displaygraded.py`** — the clearest model of the *rendering* style: a `show(*values)`
  helper displaying each value as **LaTeX** via `IPython.display.Math` + `_repr_latex_()` (the student
  sees `A:\quad <math>`, not a Python repr), and a **Markdown multiplication table of pairwise
  products** built with `display(Markdown(...))` (around lines 217–223) — the "print the pairwise
  multiplications out in markdown" pattern the maintainer named.
- **`book/docs/notebooks/proof-projection.py`** (+ `proof-cross.py`, `proof-rotate-from-a-to-b.py`) —
  the existing proof-companion notebooks: they re-derive a chapter's result symbolically and check it.
  The target style **upgrades** these so the intermediate steps render as math, not just a final
  `.simplified() == …` check.
- The trio model named in `CLAUDE.md` ("Every piece of math comes in three forms"):
  `book/docs/proof-projection.rst` + `.../notebooks/proof-projection.py` +
  `proofs/GacalcProofs/StandardPosition.lean`.

## Style requirements (what "student-followable" means here)

1. **Output is math notation; Python is the driver.** Every displayed result is LaTeX/MathJax (via
   `_repr_latex_()` / `Math` / `Markdown`), reading like the textbook — never a bare value or `print()`.
2. **Show the steps, term by term.** Expand the derivation into its pieces and render each — a product
   as its table/sum of **pairwise blade products**, a distribution per-term — so each step is
   independently checkable, not one opaque equality.
3. **Printable and checkable.** Reads top-to-bottom as a worksheet a student can print; each verifiable
   step is phrased so the student can tick it off (an explicit "✓ check: …" / checkbox markdown item).
4. **Symbolic and general** where possible (the `sym_vec*` vectors), with the cross-construction
   `(a − b).simplified() == 0` idiom where `==` would be structural.
5. **Cite the Lean theorem** it mirrors, by name, so the three forms cross-reference.

## Backlog (the current corpus, measured 2026-10-29)

- **32 Lean proof files** under `proofs/GacalcProofs/`.
- **4 book proof-chapters**: `proof-projection.rst`, `proof-cross.rst`, `proof-rotate-from-a-to-b.rst`,
  `proof-rotate.rst`.
- **3 existing proof-companion notebooks**: `proof-projection.py`, `proof-cross.py`,
  `proof-rotate-from-a-to-b.py` — so **`proof-rotate.rst` has no companion notebook yet**, and the 3
  that exist predate this style (to be upgraded to the full math-notation / step-by-step form).

The gap between **32 Lean proofs** and **3–4 book proofs** is why the *granularity* question below must
be settled before enumerating the backfill as step-tasks.

## Proposed adoption (needs go-ahead)

- **Refine the `CLAUDE.md` "Every piece of math comes in three forms" convention** so form 2 (symbolic
  Python) explicitly means a **student-followable, math-notation-rendering** worksheet in the style
  above — and record that **every proof (existing, updated, or new) carries one** (dropping the current
  "not a backfill order" caveat for this specific form). Point at this doc for the detail.
- **Backfill as step-tasks** once granularity is set: one per proof needing a notebook, plus upgrading
  the 3 existing ones; track against the backlog here.
- **Lift the shared display helpers** (`show`, `kind`, the pairwise product-table builder), today
  defined inside `displaygraded.py`, into an importable place so every proof notebook reuses them.

## Open questions

1. **Granularity — what is "a proof"?** One notebook per **book proof-chapter** (≈4, the natural
   student unit), per **named Lean result/theorem**, or per **Lean file** (32)? Recommendation: anchor
   notebooks to **book proof-chapters / named results a student would study**, not 1:1 with every Lean
   lemma file — many of the 32 files are small supporting lemmas. Confirm the unit so the backfill can
   be enumerated.
2. **The 3 existing proof notebooks** — upgrade them in place to the new style as part of the backfill,
   or leave them and only add missing ones? Recommendation: upgrade in place (they are the exemplars
   students will hit first).
3. **Shared helpers** — lift `show`/`kind`/product-table into an importable module (a `notebooks/`
   helper or `src/gacalc/`), so notebooks import rather than re-copy them? Recommendation: yes.
