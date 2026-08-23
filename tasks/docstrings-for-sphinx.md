# Add docstrings everywhere, rendered well by the book's autodoc

**Status:** proposed — open (rescoped 2026-08-13)
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-06-13
**Updated:** 2026-08-13 — rescoped. The Sphinx book now exists (`book/docs/`, stood up
2026-08-02), so this is no longer "should we stand up Sphinx?" but "complete/normalize the
package's docstrings so the book's autodoc renders everything well," coordinated with two
sibling docstring tasks (below) so it doesn't overlap them.

## Goal

Every public symbol the book's autodoc pulls in should have a good, Sphinx-rendering
docstring — complete, consistent, and in gacalc's math-notation voice. `base.py` is the
style reference (module/class/method docstrings with Hestenes notation); this task is the
*completeness and consistency* sweep across the rest.

## What changed since this was written (read first)

- **A Sphinx build now exists.** gacalc stood up `book/docs/` ("Geometry 2",
  HTML+PDF) on 2026-08-02, with an autodoc `api.rst` over `gacalc.base`,
  `gacalc.functions`, `gacalc.transforms`. The old open question "stand up Sphinx now or
  later?" is **answered — it exists.** Build mechanics: `tasks/reference/book-and-docs-pipeline.md`.
- **Two sibling tasks now own slices of "docstrings," so this one is scoped around them:**
  - `narrate-code-generator-in-docstrings.md` owns the **generator's narrative** (the story
    in `tools/gen_specialized.py` / `astbuild.py`). Not this task.
  - `generate-missing-docstrings.md` owns authoring the **generated classes' method
    docstrings** (via `base.py`/`gn.py` + the `inspect.getdoc` copy path). Not this task.
  - **This task owns the rest:** the completeness/consistency sweep across the hand-written
    modules the book's autodoc renders — `transforms.py`, `nbplotutils.py`, `gn.py`,
    `functions.py` — plus `base.py` polish, and the autodoc-surfaced rendering fixes below.

## Constraints specific to gacalc (read before editing)

- **Generated code.** The specialized reps (`g1`/`g2`/`g3`) are produced by
  `tools/gen_specialized.py`, and each generated method's docstring is **copied from the
  matching `MultiVectorBase` method** via `inspect.getdoc`. Improve those at the **source**
  (`base.py`/`gn.py`) and regenerate — never hand-edit the generated files. (That authoring
  is `generate-missing-docstrings.md`'s job; this task doesn't touch it.)
- **Docstrings are tests.** pytest runs `--doctest-modules` (`pythonpath = src`,
  `testpaths = src tests tools`), so every `>>>` example executes. Any example added must
  pass; run the suite after.
- **Voice.** Preserve the Unicode + LaTeX-ish math notation and the house rule that a
  rotation reads as an *explicit* rotation (`plane_rotation` / rotor vocabulary in
  `CLAUDE.md`) — don't flatten into generic linear-algebra phrasing.
- **Don't over-document.** Per the house standard, skip trivial one-liner helpers; focus on
  the public, autodoc-rendered symbols. (Comments explain *why* inline; docstrings state the
  contract of things a reader actually looks up.)

## Plan

- [ ] **Audit coverage** across the autodoc-rendered hand-written modules —
      `transforms.py`, `nbplotutils.py`, `gn.py`, `functions.py`, `base.py` — and list what
      lacks a docstring or has a thin one. (`base.py` is strong; `transforms.py` /
      `nbplotutils.py` are the likely gaps.)
- [ ] **Fix the autodoc-surfaced rendering issues** already found while standing up the book
      (from `book-and-docs-pipeline.md` "Open follow-ups"):
      - `|A|` in docstrings renders as RST `|substitution|` → ~12 "undefined substitution"
        warnings on `magnitude`/`inverse`/`cosine`/`normalize`/`rotor_from_vectors`. Escape
        (`\|A\|`) or use math/code roles.
      - `ₙ` (U+2099) is missing from GNU FreeSerif → that glyph drops from the PDF. Avoid
        `ₙ` in docstrings, or supply a font with coverage.
- [ ] **Pick the docstring style** — napoleon Google *or* NumPy — and apply it consistently
      with `base.py` (open question below).
- [ ] **Keep doctests green** — run `pytest` (includes `--doctest-modules`) in the container.

## Open questions

1. **napoleon style: Google or NumPy?** Confirm before the sweep — it sets the shape of
   every docstring touched.
2. **Scope of the sweep:** the autodoc-rendered core only (`base`/`functions`/`transforms`
   + `gn`), or also `nbplotutils.py` and the `tools/` helpers not covered by the narrative
   task?

## Notes / decisions

- Moved here from modelviewprojection per Bill's correction ("I meant gacalc, mainly").
- Rescoped 2026-08-13 (briefly archived, then reopened — Bill: "I was looking for many
  docstrings, keep the task open"): the book now exists, so the emphasis moved from "stand
  up Sphinx" to "make the package's docstrings complete + render well," and the
  generator-narrative and generated-method-copy slices were split out to the two sibling
  tasks so this one doesn't overlap them.

## See also

- `tasks/narrate-code-generator-in-docstrings.md` — the generator's own narrative (tools/).
- `tasks/generate-missing-docstrings.md` — authoring the generated classes' docstrings.
- `tasks/reference/book-and-docs-pipeline.md` — the Sphinx build + the autodoc follow-ups
  folded into the Plan above.
