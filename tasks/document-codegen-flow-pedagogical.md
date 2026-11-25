# Document the code-generation flow (sympy → AST), starting from Gn

**Status:** go-ahead 2026-11-25 (question answered, see Decisions); not started. Was blocked on the Open question.
**Priority:** 6
**Difficulty:** 3
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>) — citations re-verified; stale line
counts/dates dropped.
## BLUF

Maintainer's idea, verbatim: *"For the reference docs, as an example for the code generation. I'm
familiar with lisp macros, and I had you make that code with this idea. I want the reference docs to
explain the whole flow ... starting with the sympy code for gn that is used to define everything. It's
not clear ... where everything flows from there. It's not clear ... if it's reading in code and then
processing it like lisp does, or if instead, it's just generating everything from the sympy. The
reference docs should start with some ideas, embed some examples or code references to unit tests, in
the begin doc region and doc region sort of way that I have done other code."*

## Context (investigation 2026-08-27) — the core confusion is answerable NOW

- **It generates FROM sympy; it does NOT re-read/process existing source Lisp-style.** The generator
  (`tools/gen_specialized.py` + `tools/astbuild.py` + `tools/check_doc_regions.py`)
  runs `Gn` on **sympy symbols** to capture each formula, then builds Python **`ast` nodes** →
  `ast.unparse` (no string/template layer). Outputs `src/gacalc/g1.py|g2.py|g3.py` are gitignored build
  artifacts. So: sympy-defines → AST-emits; the "Lisp reads code" mental model is not what happens.
- **Mostly already documented** — `tasks/reference/code-generator-architecture.md` (the contributor map)
  + `tasks/reference/generated-product-typing.md` + the `tools/gen_specialized.py`
  module docstring (narrative front door with an ASCII pipeline diagram + doctest'd worked trace). The
  explicit "generates from sympy, does not read code Lisp-style" sentence is still absent from the
  contributor map (verified 2026-10-04: no "Lisp" in that doc), so the Plan below is still open. The
  string→AST rationale (the "Lisp/code-as-data" idea) is archived at `tasks/archive/2026/06/07/codegen-via-python-ast.md`.
  Doc-region marker machinery: `astbuild.py` + `check_doc_regions.py`; markers emitted per
  `tasks/archive/2026/07/21/emit-doc-region-markers.md`.

## Plan (draft)

- [ ] **UPDATE `tasks/reference/code-generator-architecture.md`** to add, up front: the explicit
      "generates from sympy vs Lisp-reads-code" clarification, starting from the `Gn`-on-symbols step;
      and the ideas-first framing with begin-doc-region/doc-region-embedded unit-test references.
- [ ] If a reader/book-facing explainer is wanted (Q1), draft that separately (the existing doc is
      contributor-facing).

## Open questions (answered 2026-11-25, see Decisions)

1. **Audience** — is the wanted doc **contributor-facing** (extend the existing
   `code-generator-architecture.md` + module docstring), or **book/reader-facing** (a chapter explaining
   generation as a teaching example)? *(Recommend: update the contributor doc for the clarification; add
   a reader-facing explainer only if you want it in the book.)*

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-25)

1. The audience is contributors: update `code-generator-architecture.md` (and the module docstring) to answer the core confusion. A reader-facing book explainer is added only if the maintainer asks for one later.

The block is cleared. The decision was the maintainer's "go with your suggestions" on the recommendation above.
