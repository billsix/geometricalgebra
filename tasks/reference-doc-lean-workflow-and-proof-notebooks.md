# Write a reference doc: the Lean → symbolic-test → student-proof-notebook workflow

**Status:** proposed — needs go-ahead
**Priority:** 6
**Difficulty:** 4
**Created:** 2026-09-30 **Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>)

## BLUF

Author a reference doc — `tasks/reference/lean-python-notebook-workflow.md` — that states, once
and durably, the project's *whole* method and its purpose: read Hestenes / MacDonald → write
working Python (numeric AND symbolic) → gain confidence via Lean (matched against others' proofs)
→ surface that confidence to learners as **student-verifiable** percent-format Jupyter proof
notebooks, for a "Geometry 2" pre-linear-algebra book. It must nail the two things NOT yet
written down anywhere: (i) the **Lean-theorem ↔ Python-symbolic-test correspondence and how to
manage drift** between them, and (ii) the **"verify, don't derive"** proof-notebook methodology.
"Done" = the reference doc exists, cross-linked, with a one-line pointer added to `CLAUDE.md`.
This is the *author-facing rationale* doc; the *mechanism* of generating a notebook is the
separate task `tasks/investigate-lean-to-python-proof-notebooks.md`.

## Context — the maintainer's stated purpose (paraphrased from his own notes)

> "My purpose in using Lean is not to prove anything new. I read Hestenes (or others) and make
> working Python for it — using sympy heavily, but it must work with numbers too — then use it for
> computer-graphics work like modelviewprojection. But Hestenes moves fast and is very generic;
> MacDonald goes slower. I want a 'Geometry 2' for high-school / intro-college students, a
> pre-linear-algebra course. I base my symbolic unit tests on what the books state, but I don't
> know if my Python is correct or if I've read the books right (e.g. am I doing projection
> right?). Lean makes my math solid; I don't expect students to read Lean. So: Lean checks the
> idea; those Lean tests should map to symbolic unit tests (with comments managing drift); and the
> end result is percent-format notebooks that show proofs students can *verify* (not derive,
> because that work is tedious) — like proving 𝒢₂ associativity by showing every component-wise
> product and how terms cancel."

## What already exists (so the doc EXTENDS, does not repeat)

- **`show_mult(a, b)` already does the term-by-term display he wants** — `show_mult` in
  `src/gacalc/nbplotutils.py`: it prints the full distributive expansion of `a*b` (a table of every
  blade-term × blade-term, then the sum) as LaTeX. Helpers: `_blade_terms`, `_expand_numerators_dict`.
  It is imported by the demo notebooks (`notebooks/displaymv.py`, etc.).
- **The 𝒢₂-associativity-by-`show_mult` demo already exists** — the `show_mult(g2_1, g2_2)` …
  `((g2_1*g2_2)*g2_3) - (g2_1*(g2_2*g2_3))` associativity cells in `notebooks/displaymv.py`
  (shows `(g2_1*g2_2)*g2_3 − g2_1*(g2_2*g2_3) == 0` with the expansions). So the *technique* is
  proven; what's missing is the doc that frames it as the method and ties it to Lean.
- **The workflow + completeness gate are documented** — `tasks/reference/lean-for-gacalc.md`
  (esp. its section "The one thing to understand first: what a Lean proof does and does NOT check":
  "Lean checks the *idea*, the tests check the *code*, and verifying Python matches
  Lean is a larger effort **out of scope**"). **Cite this framing; do not restate it.**
- **The proof-notebook mechanism is a separate proposed task** —
  `tasks/investigate-lean-to-python-proof-notebooks.md` (P7/D7). Its crux (its "Context / the real
  question to answer first" section): a
  `ring` / `ext <;> ring` Lean proof is **opaque** — no human-readable step trace to transcribe —
  so its recommended option is to generate the symbolic expansion in sympy (the `show_mult` path)
  and use Lean only to *certify* the identity. **This doc supplies the "why"; that task supplies
  the "how" — link them, don't merge.**
- **The book "Geometry 2"** (`book/docs/`, `project = "Geometry 2"` in `book/docs/conf.py`) has an
  explicit proof-placement rule (`tasks/reference/book-outline.md`, the "Proofs → separate `.rst`"
  rule): "**Proofs → separate `.rst`; uses →
  main docs; calculations → notebooks.**" There is NO dedicated `notebook-proofs/` directory yet;
  proofs live inline or as `.rst` pages (`book/docs/proof-rotate.rst`). The doc should record
  where a student proof-notebook lands relative to this rule.

## The genuine gaps this doc must fill

1. **Lean ↔ Python correspondence + drift management.** No doc maps a Lean theorem name → the
   Python symbolic test that mirrors it, and there's no drift-detection convention. Propose the
   convention (e.g. a comment tag on each side naming its twin — `# lean: GacalcProofs.G3.reverse_mul`
   in the test and a mirror note in the `.lean`), and how a reviewer spots drift. This is the
   maintainer's "comments mapping the two back and forth."
2. **"Verify, don't derive" methodology.** Write down the pedagogy: the student's job is to
   *check* each mechanical step (the `show_mult` table), not produce it; the notebook shows terms
   cancelling. State what makes a proof-notebook student-verifiable (canonical form not decimals,
   each step one distributive/anticommute move, the final residual `== 0`).
   - **KNOWN GAP the methodology must fix (maintainer, 2026-09-30):** `show_mult` shows the two
     product expansions, but the associativity demo (the `displaymv.py` associativity cells) then just
     evaluates `(g2_1*g2_2)*g2_3 − g2_1*(g2_2*g2_3)` and prints `0` — "it doesn't show shit, it
     just shows 0." Showing the multiplication steps is not showing the *cancellation*. The
     methodology (and a companion display helper alongside `show_mult` in
     `src/gacalc/nbplotutils.py` — a `show_sub`/`show_cancellation`) must lay the two expansions
     out **term by term** and visibly cancel matching terms to zero, so the student watches the
     terms disappear rather than being handed a bare `0`. This concrete requirement is folded into
     the notebook-mechanism task `tasks/investigate-lean-to-python-proof-notebooks.md` (2026-10-04).
   - **Concrete rendering idea (maintainer, 2026-09-30):** show the two expressions **side by
     side with labels**, and mark the cancelling parts with LaTeX `\underbrace{…}_{label}` (the
     "w-shape brace under an expression"; `\overbrace{…}^{label}` for above) — e.g. brace the
     `+t` in one and the `−t` in the other and label them "cancel". So the display helper emits
     matched `\underbrace` annotations over the paired terms rather than just evaluating the
     difference. (mathjax/myst_nb render `\underbrace`, so it works in the book notebooks.)

## Scope note — this is a reference doc, not the notebook machinery

Per the sandbox-global `~/.claude/reference/reference-doc-conventions.md`, a reference doc "states
what is TRUE, not what to DO." Keep the *pipeline mechanics* (jupytext build, myst_nb kernel-in-venv gotcha —
`tasks/reference/book-and-docs-pipeline.md`) out of it by reference. This doc is the durable
statement of intent + the two conventions above.

## Open questions

1. **One doc or two?** Fold "Lean↔Python drift" and "student proof-notebook methodology" into one
   `lean-python-notebook-workflow.md`, or split (a workflow/drift doc vs a pedagogy doc)? My lean:
   one doc, two sections — they're the same story told author-side then student-side.
2. **Drift-tag convention:** comment tags on both sides (my lean), a central mapping table in the
   doc, or a checked `tools/` script that greps for orphaned tags? (A script could become a gate
   later — don't auto-wire it.)
3. ~~Does the "bootstrapping" theme belong in this doc or its own?~~ **Resolved by events:** it has
   its own reference doc, `tasks/reference/reduction-to-standard-position.md` (the work is archived at
   `tasks/archive/2026/10/04/reduce-to-standard-position.md`); this doc just links it as the
   pedagogy's backbone.
