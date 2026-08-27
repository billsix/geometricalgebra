# Document the code-generation flow (sympy → AST), starting from Gn

**Status:** blocked
**Priority:** 6
**Difficulty:** 3
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** maintainer answers the Open question below (contributor-facing doc update vs a new
reader/book-facing explainer).
**Recheck:** the Open question below is answered (maintainer-gated; `/recheck-blocked` surfaces it).

## Goal

Maintainer's idea, verbatim: *"For the reference docs, as an example for the code generation. I'm
familiar with lisp macros, and I had you make that code with this idea. I want the reference docs to
explain the whole flow ... starting with the sympy code for gn that is used to define everything. It's
not clear ... where everything flows from there. It's not clear ... if it's reading in code and then
processing it like lisp does, or if instead, it's just generating everything from the sympy. The
reference docs should start with some ideas, embed some examples or code references to unit tests, in
the begin doc region and doc region sort of way that I have done other code."*

## Context (investigation 2026-08-27) — the core confusion is answerable NOW

- **It generates FROM sympy; it does NOT re-read/process existing source Lisp-style.** The generator
  (`tools/gen_specialized.py` ~2300 lines + `tools/astbuild.py` ~470 + `tools/check_doc_regions.py`)
  runs `Gn` on **sympy symbols** to capture each formula, then builds Python **`ast` nodes** →
  `ast.unparse` (no string/template layer). Outputs `src/gacalc/g1.py|g2.py|g3.py` are gitignored build
  artifacts. So: sympy-defines → AST-emits; the "Lisp reads code" mental model is not what happens.
- **Mostly already documented** — `tasks/reference/code-generator-architecture.md` (the contributor map,
  last updated 2026-07-21) + `tasks/reference/generated-product-typing.md` + the `tools/gen_specialized.py`
  module docstring (narrative front door with an ASCII pipeline diagram + doctest'd worked trace). The
  string→AST rationale (the "Lisp/code-as-data" idea) is archived at `2026/06/07/codegen-via-python-ast.md`.
  Doc-region marker machinery: `astbuild.py` + `check_doc_regions.py`; markers emitted per
  `2026/07/21/emit-doc-region-markers.md`.

## Plan (draft)

- [ ] **UPDATE `tasks/reference/code-generator-architecture.md`** to add, up front: the explicit
      "generates from sympy vs Lisp-reads-code" clarification, starting from the `Gn`-on-symbols step;
      and the ideas-first framing with begin-doc-region/doc-region-embedded unit-test references.
- [ ] If a reader/book-facing explainer is wanted (Q1), draft that separately (the existing doc is
      contributor-facing).

## Open questions

1. **Audience** — is the wanted doc **contributor-facing** (extend the existing
   `code-generator-architecture.md` + module docstring), or **book/reader-facing** (a chapter explaining
   generation as a teaching example)? *(Recommend: update the contributor doc for the clarification; add
   a reader-facing explainer only if you want it in the book.)*
