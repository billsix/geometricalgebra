# `src/` low cleanup: history-narrating docstrings, docstring notation, dead code, moved-task citations

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 3
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §4.3, §2.4

## BLUF

Fix the low-severity, behaviour-preserving findings in the hand-written library. These are docstrings
and comments that narrate history, docstring math that breaks the notation rules, dead code, a few
wrong comments, and citations of tasks that have moved to the archive. Done means each item below is
fixed or dropped with a reason, and `make format` and `make test` pass. The behaviour-changing §4.3
findings are a separate task, `tasks/library-low-behavior-traps.md`.

## Context

Read first:
- `CLAUDE.md` › "Math notation for readers" and "Coding standard";
- the cross-project rule "Comments and docstrings describe the present, not the history".

Docstrings in `base.py` are copied into the generated `g*.py` by `inject_method_docstrings`
(`tasks/reference/generated-docstrings.md`), so a fix in `base.py` also fixes `g1.py`–`g3.py`. Never
edit the generated files.

**History narration** (re-checked 2026-11-09; line numbers drift, so match on content):
- `base.py:225` "Phase 1 (2026-08-15) computed…"
- `base.py:1490` "This replaces the older…"
- `base.py:2379` "An earlier version returned the hyperbolic form…"
- the `normalize` docstring and "the previous…" (record: `base.py:529`)
- the `transforms.py` module docstring ("removed long before…", "backward compatibility")
- `frame.py`/`measure.py` "contrast the blade-square-sign task"
- the `nbplotutils` helpers `_to_xy`, `_draw_labelled_triangle`, `_current_axes`, `_blade_terms`
  ("Was written inline…")

**Docstring notation:**
- `base.py` `2 + 2cos θ = 4cos²(θ/2)` (record: `:2168`), and the middle dot used as multiplication
  (record: `:424`)
- `unit_pseudoscalar`'s `n(n-1)`
- `exp`'s `cosh|A| + sinh|A| Â`
- `measure.py` `a_1 b_2 - a_2 b_1`
- `frame.py` eq 3.2 written `reverse(A_{k-1}) · A_k` although the code uses `*`; eq 3.7 and
  `R⁻¹ Qᵀ y` use juxtaposition
- `functions.py` `Linearity`'s `A x`
- `vectorcalc.py`'s `⟨a b⟩`
- `versor_from_vectors` says "Geometric products are juxtaposition, as elsewhere"

**Dead code:**
- `MultiVectorBase.identity` (`base.py:2066`) is unused and duplicates `functions.identity`. Grep
  `notebooks/`, `book/` and `tests/` before deleting it.
- `_coerce`'s `case sympy.Expr()` arm is identical to its default arm.
- `nbplotutils.py` builds and discards `np.array(...buffer_rgba())`.
- a commented-out `ax.annotate` block
- unused `color`/`xcolor`/`ycolor` parameters in the triangle/ndc/screen/basis helpers
- `draw_ndc` duplicates `_draw_labelled_triangle`

**Wrong text:**
- `gn.py:76` "G and G will be specialized…" is garbled and in the future tense.
- `measure.py` (record: `:239`) says `max_grade()` raises on zero, but it returns 0.
- `nbplotutils.py` shows students "additon".
- `gn.py`'s `decrease_grade` picks `identity()` as a function, where a plain `if` reads better for a
  student.

**Moved-task citations (§2.4, `src/` part):** `base.py:993,1035` →
`tasks/investigate-dot-product-grade-0.md`, `base.py:2699` → `tasks/validate-blade-dict-keys.md`, and
`vectorcalc.py` → `tasks/custom-symbols-and-vector-calc.md`. Repoint each to its archive path, or to
the reference doc that now holds the decision.

**Out of scope:** the unannotated bindings in §4.3 belong to `tasks/annotation-auditor-floor-drift.md`.

## Plan

- [ ] Rewrite the history docstrings and comments to describe current behaviour. Where the history
  matters, it goes in the commit message.
- [ ] Fix the docstring notation per the rules. Doctest lines are exempt.
- [ ] Remove the dead code, checking each for callers first.
- [ ] Fix the wrong text and repoint the citations (`grep -rn "tasks/[a-z0-9-]*\.md" src` and check
  that each path exists).
- [ ] `make generate`, then `make format` and `make test`. Spot-check that a fixed docstring reaches
  `g3.py`.

## Open questions

None.
