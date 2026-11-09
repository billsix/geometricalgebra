# Trim geometricalgebra's CLAUDE.md (74,732 B ≈ 18.7K tok, loaded every session)

**Created:** 2026-09-13 · **Completed:** 2026-09-13 (archived 2026-09-14)
**Source:** github.com/billsix/runCrushInContainer
`tasks/archive/2026/09/14/investigate-context-bloat-geometricalgebra.md` (the diagnosis); measurement
method in github.com/billsix/runCrushInContainer `tasks/reference/crush-context-assembly.md`

## Why

gacalc's `CLAUDE.md` was 74,732 B ≈ 18.7K tokens (907 lines, no `@`-imports) — spliced into every
session and turn, ~47% of Crush's system prompt, the largest of the maintainer's repos. The fix was
the maintainer's own convention: keep `CLAUDE.md` lean (module map, commands and named gates, the
invariant conventions the agent must obey, one-line pointers) and push rationale, mechanics, caveats
and history into `tasks/reference/` docs read on demand. The biggest sections were Architecture
(22.6 KB), Coding standard (17.3 KB), Module layout (9.6 KB), Dev workflow (9.3 KB) and Code
generation (7.2 KB).

## Decisions

- **Moderate target (~17–18 KB, ~4.5K tokens), not the more aggressive ~3K cut:** the Operators
  cheat-sheet and the full `make` command + gate list earn their inline place every session.
- **The coding standard's judgment-call prose went to a new shared cross-project doc**,
  github.com/billsix/runClaudeInContainer `tasks/reference/python-coding-standard.md`, rather than
  being folded into the 60 KB `design-decisions.md`; it cross-links
  `tasks/reference/conditional-refactoring-rules.md` and `tasks/reference/type-annotation-exemptions.md`.
  (gacalc's own worked examples later got `tasks/reference/python-coding-standard-gacalc.md`.)
- **Method:** before moving any paragraph, check whether its destination doc already holds it; if so
  collapse it to a pointer with no copy, otherwise append it first. Guardrails the agent follows while
  writing code stay inline as terse one-liners; their rationale moves. Every outbound `tasks/…`
  pointer is preserved.

Per section: intro, Operators and the Dev-workflow command list stayed (trimmed); Module layout kept a
one-line-per-file map plus the vendored-Emacs and acyclic-layering one-liners; Architecture kept only
the interchange-primitives contract and the terse conventions; Code generation kept the
generate-first and "a correct generator change is a `tools/`-only diff" guardrails; Coding standard
kept the (a)/(b) headline and the repo-specific invariants (`m`/`b`, externally-defined names,
line length is the formatter's job, `cls`, `n` never `grade`); Performance became one line;
Assessment kept the two genuinely open limits; Future directions kept only the paravectors note.

## Result

- **CLAUDE.md: 74,732 B → 21,801 B** (906 → 288 lines), a ~70.8% cut — above the 17–18 KB
  projection because the moderate target kept the Operators cheat-sheet, the full gate list, the
  interchange contract and the terse guardrails inline, as decided.
- **New shared doc:** the Python coding standard above (16,587 B), harvested verbatim from the
  "Coding standard (Python)" section; not auto-loaded (modelviewprojection was to merge its deltas
  later).
- **Appended before removal** (prose found only in `CLAUDE.md`): `tasks/reference/design-decisions.md`
  › "Packaging & dev workflow" gained why the dev gate skips the generated `g*.py` and how to
  type-check them in full context, the Releasing & PyPI-403 catalogue with the credential resolution
  order, and the savefig-inside-`with` verification lesson; `tasks/reference/book-and-docs-pipeline.md`
  gained the JupyterLab bake settings (jupytext default viewer, labextension announcements disabled).
- **Collapsed to pointers with no copy** (verified already covered): every Architecture caveat and
  deep mechanic → `design-decisions.md`, `transform-and-composable-function-layer.md`,
  `unit-bivector-and-rotors.md`, `blade-dict-interchange.md`, `generated-product-typing.md`; codegen
  mechanics and doc-region naming → `code-generator-architecture.md`; Odd_3 →
  `graded-subspaces-vs-subalgebras.md`; the ty full-context detail was already in
  `generated-product-typing.md` › "High-dimension ty findings".

## Verification

All 14 inbound `tasks/reference/` and archive pointers in the trimmed `CLAUDE.md` were checked to
resolve.
