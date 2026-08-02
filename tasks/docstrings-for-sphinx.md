# Add docstrings everywhere, rendered well by Sphinx

**Status:** proposed — not started
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-06-13

## Goal

Add/complete docstrings across the `gacalc` package so **everything** is
documented, written so it renders well in Sphinx. Today docs live in `README.md`
and there's **no Sphinx setup** — so part of this is deciding whether to stand up
an autodoc-based docs build, or at least make all docstrings Sphinx-ready for one.

`base.py` is already well-documented (module/class/method docstrings with math
notation) — use it as the style reference. This task is about *completeness*,
*consistency*, and *Sphinx-readiness* across the rest.

## Constraints specific to gacalc (read before editing)

- **Generated code.** The specialized representations (`g2`, `g3`, …) are produced
  by `tools/gen_specialized.py` (`tools/astbuild.py`), and each generated method's
  docstring is **copied from the matching source/template** (see `CLAUDE.md`).
  Add/improve docstrings at the **source/template** level and **regenerate** — do
  **not** hand-edit the generated files.
- **Docstrings are tests.** pytest runs with `--doctest-modules` (`pythonpath=src`,
  `testpaths = src tests`), so every `>>>` example in a docstring executes. Any
  examples added must pass; run the suite after.
- **Voice.** Preserve the existing math notation (Unicode + LaTeX-ish) and the
  house rule that a rotation reads as an *explicit rotation* (the rotor/
  `plane_of_rotation` vocabulary in `CLAUDE.md`) — don't flatten it into generic
  linear-algebra phrasing.

## Plan

- [ ] **Audit coverage.** Walk `src/gacalc/` — `base.py`, `g1.py`,
      `g2.py`, `g3.py` (each now also holds its per-algebra `ScalarN`; no `scalar.py`),
      `gn.py`, `transforms.py`, `nbplotutils.py` — and list what
      lacks docstrings or has thin ones. `base.py` is strong; the generated reps
      and `transforms.py` are likely where gaps are.
- [ ] **Decide the Sphinx story.** No `docs/`/`conf.py` exists today. Either (a)
      stand up a Sphinx docs build — `sphinx.ext.autodoc` + `sphinx.ext.napoleon`
      + math, an `api.rst` that `automodule`s the package, and a build path
      (Makefile target / container, per the family template) — or (b) keep README
      primary and just make docstrings Sphinx-ready. (Open question — Bill's call.)
- [ ] **Pick the style.** napoleon (Google *or* NumPy — confirm) for the new/edited
      docstrings, consistent with `base.py`.
- [ ] **Write docstrings at the right layer.** For generated reps, edit the
      source/template and regenerate; verify the docstrings propagate to `g2`/`g3`.
      For hand-written modules, add module → class → function docstrings directly.
- [ ] **Keep doctests green.** Ensure any examples are valid doctests; run
      `pytest` (which includes `--doctest-modules`) in the container.

## Notes / decisions

- Moved here from modelviewprojection per Bill's correction ("I meant gacalc,
  mainly") — the mvp docstrings task was removed. If mvp also wants a docstrings
  pass later, that's a separate (smaller) task.
- No Sphinx/docs build exists in gacalc yet; current docs are `README.md`
  (`CLAUDE.md` line ~9).
- `--doctest-modules` is on (`CLAUDE.md` line ~243): docstring examples are tests.
- Specialized reps are code-generated and docstrings propagate from the
  source/template (`CLAUDE.md` lines ~183, ~225) — edit + regenerate, never touch
  generated files.

## Open questions

- Stand up a full Sphinx docs build for gacalc now, or just make docstrings
  Sphinx-ready for a later docs setup?
- napoleon style: **Google** or **NumPy**?
- Scope: core algebra modules only, or also `tools/` and `nbplotutils.py`?
