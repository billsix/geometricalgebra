# Grassmann absolute/relative units — concept, citation, and runtime tests

**Status:** blocked
**Priority:** 7
**Difficulty:** 3
**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>)
**Blocked on:** maintainer provides the source citation (1800s book/author/page — likely Grassmann) and
the precise definitions/predicate to test.
**Recheck:** the Open questions below are answered — specifically the book citation and the exact
predicate (maintainer-gated; `/recheck-blocked` surfaces it).

## Goal

Maintainer's idea, verbatim: *"Make run time tests for absolute unit, relative unit, reference. The
original guys work from the 1800s, ask me about the book name, author, and page number, and then do.
1 * e_1 is an absolute unit. a relative unit is 3 * e_1 + 4 * e_2. the base types with a coefficient of
1 are absolute units. but, ask for me the definition from the book, I think by Grassmann."*

Introduce the absolute-unit / relative-unit / reference concepts (from the 1800s source), and add
runtime tests for them.

## Context (investigation 2026-08-27)

- **Genuine gap** — no reference doc or code mentions "absolute unit"/"relative unit"/Grassmann's
  terminology (confirmed by repeated greps across active/reference/archive).
- The only adjacent work is display convention: `2026/08/26/explicit-unit-coefficients.md` made
  `e_1` render as `1*e_1` (~235 sites) — that's *display*, not the Grassmann *concept* or tests for it.
- The maintainer's own examples: `1*e_1` = absolute unit; `3*e_1 + 4*e_2` = relative unit; "base types
  with coefficient 1 are absolute units." A third category, "reference," is named but not defined.

## Plan (draft — blocked on the citation)

- [ ] Get the exact 1800s citation and definitions (Q1).
- [ ] Write a short reference doc: Grassmann's absolute/relative-unit definitions + citation.
- [ ] Add runtime tests / possibly an `is_absolute_unit()` predicate once the definition is pinned (Q2).

## Open questions

1. **Citation** — which 1800s source and exact page? Grassmann's *Ausdehnungslehre* (1844 or 1862
   edition)? (You asked me to ask you for the book name, author, and page number.)
2. **Predicate** — what should a method/test assert about absolute vs relative units (e.g. an
   `is_absolute_unit()` returning true for a basis blade with coefficient 1)? And what is the third
   category, **"reference"** — what distinguishes it from absolute and relative units?
