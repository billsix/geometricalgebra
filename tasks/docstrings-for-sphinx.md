# Add docstrings everywhere, rendered well by the book's autodoc

**Status:** proposed — open (rescoped 2026-08-13; re-narrowed 2026-09-26)
**Priority:** 5
**Difficulty:** 6
**Created:** 2026-06-13
**Updated:** 2026-09-26 — re-narrowed after `generate-missing-docstrings.md` completed. That
sibling authored full docstrings on **every `base.py`/`gn.py` method** (and made the generator
emit one on every generated method), so this task's `base.py` / `gn.py` **coverage** is now
done. What remains here: the **hand-written modules not yet swept** (`transforms.py`,
`nbplotutils.py`, `functions.py`, `tools/` helpers), the two **autodoc rendering fixes** below,
and — if wanted — a **napoleon-Google consistency pass** over the now-complete-but-freeform
`base.py`/`gn.py` docstrings (they were written in freeform Hestenes prose, not Google sections).
Earlier history: rescoped 2026-08-13 once the Sphinx book existed (`book/docs/`, 2026-08-02).

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
  - `generate-missing-docstrings.md` — **COMPLETE (2026-09-26).** It authored full docstrings
    on every `base.py`/`gn.py` method and made the generator emit one on every generated method
    (see `tasks/reference/generated-docstrings.md`). So `base.py`/`gn.py` **coverage is done**;
    what it did NOT do is normalize their freeform-Hestenes docstrings to napoleon Google style.
  - **This task now owns:** (1) the completeness sweep across the still-unswept hand-written
    modules the book's autodoc renders — `transforms.py`, `nbplotutils.py`, `functions.py`
    (+ `tools/` helpers not owned by the narrative task); (2) the autodoc rendering fixes below;
    (3) optionally, a napoleon-Google **consistency** pass over the now-complete-but-freeform
    `base.py`/`gn.py` docstrings. `base.py`/`gn.py` *coverage* is no longer in scope.

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

- [ ] **Audit coverage** across the still-unswept hand-written modules — `transforms.py`,
      `nbplotutils.py`, `functions.py`, plus the `tools/` helpers not owned by the narrative
      task — and list what lacks a docstring or has a thin one. (`base.py`/`gn.py` are already
      100% covered by `generate-missing-docstrings.md`; `transforms.py` / `nbplotutils.py` are
      the likely gaps.)
- [ ] **(optional) napoleon-Google consistency pass** over `base.py`/`gn.py` — they are fully
      covered but in freeform Hestenes prose, not Google sections; normalize if the book wants it.
- [ ] **Fix the autodoc-surfaced rendering issues** already found while standing up the book
      (from `book-and-docs-pipeline.md` "Open follow-ups"):
      - `|A|` in docstrings renders as RST `|substitution|` → ~12 "undefined substitution"
        warnings on `magnitude`/`inverse`/`cosine`/`normalize`/`rotor_from_vectors`. Escape
        (`\|A\|`) or use math/code roles.
      - `ₙ` (U+2099) is missing from GNU FreeSerif → that glyph drops from the PDF. Avoid
        `ₙ` in docstrings, or supply a font with coverage.
- [ ] **Apply napoleon Google style** consistently with `base.py` (decided — see Open questions).
- [ ] **Keep doctests green** — run `pytest` (includes `--doctest-modules`) in the container.

## Open questions

All resolved (William Emerison Six <billsix@gmail.com>, 2026-09-26) — none open; the older
"stand up Sphinx now or later?" question is also moot (the book exists, see above).

1. ~~**napoleon style: Google or NumPy?**~~ **RESOLVED — Google.** Use napoleon Google style
   throughout, consistent with `base.py`.
2. ~~**Scope of the sweep:**~~ **RESOLVED — all of them.** The sweep covers the autodoc core
   (`base`/`functions`/`transforms`/`gn`) *and* `nbplotutils.py` *and* the `tools/` helpers not
   owned by the narrative task.

## Notes / decisions

- Moved here from modelviewprojection per Bill's correction ("I meant gacalc, mainly").
- Rescoped 2026-08-13 (briefly archived, then reopened — Bill: "I was looking for many
  docstrings, keep the task open"): the book now exists, so the emphasis moved from "stand
  up Sphinx" to "make the package's docstrings complete + render well," and the
  generator-narrative and generated-method-copy slices were split out to the two sibling
  tasks so this one doesn't overlap them.

## See also

- `tasks/narrate-code-generator-in-docstrings.md` — the generator's own narrative (tools/).
- `tasks/archive/2026/09/26/generate-missing-docstrings.md` — **COMPLETE + archived** —
  authored base/gn docstrings + made the generator emit one per generated method.
- `tasks/reference/generated-docstrings.md` — the generated-docstring mechanism, the doctest
  conventions (explicit unit coefficients, typed comparisons, annotations-not-assertions) this
  sweep should also follow, and the gotchas.
- `tasks/reference/book-and-docs-pipeline.md` — the Sphinx build + the autodoc follow-ups
  folded into the Plan above.
