# Apply the 2026-11-06 naming and scope rules across geometricalgebra

**Status:** proposed — needs go-ahead (open questions below)
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-11-06 (William Emerison Six <billsix@gmail.com>): "make a task to search through all of
geometricalgebra and see if there is programming advice that we added that should be applied to the
codebase, to refactor it".

## BLUF

The 2026-11-06 refactor of `Frame.to_invertible_function` produced five coding rules, now in the shared
Python standard. So far they have been applied to that one method (and to `measure.signed_content`).
This task searches the rest of gacalc for places that break them, records every candidate in a worklog,
and refactors the ones that should change, with no change in behaviour. Done = every candidate is either
refactored or recorded as left alone with its reason, `make test` and `make format` pass, and
`tools/check_annotations.py` shows no new rows.

## Context (read first)

- **The rules**, in the shared `python-coding-standard.md` (github.com/billsix/runClaudeInContainer
  `tasks/reference/`; mounted at `~/.claude/reference/`), sections "Inline a value used once, and name
  it in a comment instead of a binding" and "What earns an extraction":
  1. **Inline a binding used once**, even one that exists to explain the expression; put a comment above
     the inlined subexpression that describes it and gives it its name.
  2. **Two uses do not automatically earn a name**: check whether one expression absorbs them (e.g.
     `getattr(obj, name, fallback)` in place of a `None` check plus ternary), or whether a cheap
     expression can be repeated. Keep the name when repeating the expression reads worse or recomputes
     something expensive.
  3. **Declare a name at the point of use**, not many lines earlier.
  4. **Nest a helper with one caller inside that caller.**
  5. **When nesting, shadow deliberately**: the helper's parameter takes the caller's name when it means
     the same thing, and the shadowing is verified (the helper never needs the outer value; none of its
     other names hide an enclosing binding).
- **The worked example to imitate:** `tasks/reference/python-coding-standard-gacalc.md`, "Inline once,
  declare at use, nest and shadow".
- **Rules from the same session that are NOT in scope here:**
  - The shared "must be a vector" check (`MultiVectorBase.require_vector`/`require_vectors`) was already
    applied everywhere (`tasks/archive/2026/11/06/reuse-existing-vector-check.md`).
  - Head-first recursion is not yet a rule; it waits on `tasks/frame-inverse-head-first-recursion.md`
    (unblocked 2026-11-07, not yet done).
- **Rules that compete with these, and win:** an externally-defined name is never renamed; "annotate
  every binding" still applies to every name that survives; `m`/`b`/`n`/`cls` naming; Hestenes
  variable notation (`tasks/reference/hestenes-variable-notation.md`).

## Scope

- **In:** the hand-written Python in `src/gacalc/` (except the generated `g*.py`), `tools/` (including
  `tools/gen_specialized.py` and `tools/astbuild.py`), `tests/`, `notebooks/`, `book/docs/notebooks/`,
  and `book/figures/epix/`.
- **The generated `g1`–`g5`:** never edited by hand. A rule broken in emitted code is fixed in the
  generator, and only if the change improves the emitted source a reader sees (Open Q3).
- **Out:** the vendored Emacs tree under `entrypoint/` (off-limits), and `proofs/` (Lean; a different
  language with its own conventions).

## Plan

1. **Discover with a script, not by reading every file.** Write
   `tasks/adhoc/apply-2026-11-06-naming-and-scope-rules/discover.py`, an `ast` walk over the in-scope
   paths (repo-relative paths) that reports:
   - a local assigned once and loaded once (rule 1), with the line distance between the two (rule 3);
   - a local assigned once and loaded exactly twice, flagged for a look (rule 2);
   - a local whose first load is far from its assignment, e.g. more than 10 lines (rule 3);
   - a module-level or enclosing-scope function called from exactly one function (rule 4);
   - a nested function whose parameter names differ from an enclosing local holding the same kind of
     value, as a lead for rule 5 (a judgment call, so a lead only).
   Write the results to `tasks/adhoc/apply-2026-11-06-naming-and-scope-rules/data/candidates.txt` (a
   committed snapshot worklog).
2. **Triage the worklog** into: refactor; leave alone (with the reason, e.g. a loop accumulator, a value
   bound for a debugger or a doctest, a name a test asserts on, a public parameter, an annotation that
   carries information the inline form would lose); and ask the maintainer. Record the counts here.
3. **Refactor in small batches, one module (or a few related ones) per commit**, matching the worked
   example: inline with a naming comment, absorb double uses, move declarations down, nest one-caller
   helpers and verify the shadowing. Re-run `tools/check_annotations.py`, `ruff`, and `ty` after each
   batch.
4. **Gates:** containerized `make test` and `make format`; `make check-generated` and
   `make check-regions` if the generator or any doc-region-marked code was touched (book listings
   include code by marker; a refactor that moves marked code moves its markers).
5. Record in this doc what was changed, what was left alone and why, and any rule the survey showed
   needs a sharper wording; feed that back to the shared standard (github.com/billsix/runClaudeInContainer,
   mirrored in github.com/billsix/runCrushInContainer).

## Open questions

1. **Survey first, or survey and apply?** (a) Run the discovery and triage, then stop and show you the
   worklog before any refactor, or (b) apply the clear cases straight away and bring you only the
   judgment calls. I recommend (a) for the first module or two, so you can calibrate the triage, then
   (b) for the rest.
2. **Does a nested helper need a stated reason to stay at module level?** Rule 4 says to nest a
   one-caller helper. A module-level private helper with one caller in the library may still be imported
   by a test, which nesting would break. Recommended: a helper a test imports counts as having a second
   caller and stays at module level (the discovery script checks `tests/` imports before flagging).
3. **The generator's emitted code** (`g1`–`g5`): apply the rules to what `tools/gen_specialized.py`
   emits too, or only to the generator's own source? Recommended: only the generator's own source in
   this task. The emitted locals are systematic CSE temporaries, and changing the emitted shape would
   ripple through `make check-generated` and the doc regions for little reader benefit.
4. **The book notebooks** (`book/docs/notebooks/`) are student-facing, and a name bound once can be
   there to show the student a step (`a_par: Vector = …` printed in the next cell). Include them, or
   exempt any binding a notebook displays or explains? Recommended: include them, but exempt a binding
   that a notebook cell displays or the page's prose names.
