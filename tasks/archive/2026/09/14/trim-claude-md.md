# Trim geometricalgebra's CLAUDE.md (74,732 B ≈ 18.7K tok, loaded every session)

**Status:** Done — trimmed 2026-09-13 (archived 2026-09-14)
**Priority:** 2
**Difficulty:** 3

## Result (2026-09-13)
- **CLAUDE.md: 74,732 B → 21,801 B** (906 → 288 lines), a **~70.8%** reduction in per-turn
  context cost. (Slightly above the ~17-18 KB projection because MODERATE kept the Operators
  cheat-sheet, the full `make` command + gate list, the interchange-primitives contract, and the
  terse conventions/guardrails inline, as decided.)
- **New shared doc:** `runClaudeInContainer/tasks/reference/python-coding-standard.md` (16,587 B)
  — the whole "Coding standard (Python)" section harvested verbatim into a coherent cross-project
  reference (modelviewprojection will merge its deltas later). NOT auto-loaded.
- **Appended (unique, not-already-present prose) before removal from CLAUDE.md:**
  `design-decisions.md` › "Packaging & dev workflow" gained (1) why the dev gate skips the generated
  `g*.py` + how to type-check them in full context, (2) the Releasing & PyPI-403 catalogue + credential
  resolution order, (3) the savefig-inside-`with` verification lesson; `book-and-docs-pipeline.md`
  gained the JupyterLab bake settings (jupytext default-viewer, labextension announcements disable).
- **Collapsed to pointers with NO copy** (verified already covered): Architecture deep mechanics +
  every caveat (frozen/slots, frozen≠hashable, coefficient views, custom blade symbols, `Coef` vs
  `numbers.Real`, magnitude preservation, project/reject narrowing, rotor sandwich, plane_rotation,
  to_matrix/to_matrix_template, composable-function hierarchy, quarter turn, exp) → `design-decisions.md`
  / `transform-and-composable-function-layer.md` / `unit-bivector-and-rotors.md` /
  `blade-dict-interchange.md` / `generated-product-typing.md`; Code-generation mechanics + doc-region
  naming → `code-generator-architecture.md`; Odd_3 → `graded-subspaces-vs-subalgebras.md`; the
  ty-full-context / single-file-invalid detail was already in `generated-product-typing.md` › "High-
  dimension ty findings". All 14 inbound `tasks/reference/` + archive pointers in the trimmed
  CLAUDE.md verified to resolve.

## BLUF
gacalc's `CLAUDE.md` is **74,732 B ≈ 18.7K tok** — spliced into the AI's context every
session/turn (~47% of Crush's system prompt), the largest of all the maintainer's repos.
The fix is the maintainer's own convention: keep `CLAUDE.md` lean (dir/module layout, the
build/run/test commands + named gates, the invariant conventions the agent must obey while
working, and one-line pointers) and push the design rationale / deep mechanics / caveats /
history into `tasks/reference/` docs read on demand. Target: trim to **≈17-18 KB (~4.5K
tok)**, a ~76% cut, moving the bulk of **Architecture** (22.6 KB) and the **Coding standard**
(17.3 KB) into reference docs that mostly **already exist**.

## Context
- **Why:** `CLAUDE.md` loads every session. Measured cost: this file = 74,732 B ≈ 18.7K
  tok/turn (47% of Crush's system prompt), the largest of the maintainer's repos. Method +
  numbers: runCrushInContainer `tasks/reference/crush-context-assembly.md`.
- **Current CLAUDE.md size:** 74,732 B ≈ 18.7K tok (907 lines).
- **@-imports:** **none.** This repo-local `CLAUDE.md` has no own-line `@path` import lines
  (unlike the global `~/.claude/CLAUDE.md`), so nothing is recursively spliced from it —
  the 18.7K is all in this one file.
- **Convention:** `CLAUDE.md` lean + `tasks/reference/<slug>.md` for detail (the maintainer's
  own rule, stated verbatim inside this very file: "Canonical home is this file" for the
  coding standard is itself the anti-pattern to reverse — the standard's *judgment-call* prose
  belongs in a reference doc, with `CLAUDE.md` pointing at it).
- **Measured section sizes** (bytes, `awk` over the file):

  | Section | bytes |
  |---|---|
  | intro (before first `##`) | 596 |
  | Module layout | 9,620 |
  | Architecture | 22,619 |
  | Operators | 3,052 |
  | Code generation | 7,197 |
  | Coding standard (Python) | 17,347 |
  | Dev workflow | 9,316 |
  | Performance | 363 |
  | Assessment / known issues | 939 |
  | Future directions | 2,588 |

- **Existing `tasks/reference/` docs** (destinations already in place — most MOVEs append to
  these rather than create new files): `approximate-float-equality.md`,
  `blade-dict-interchange.md`, `book-and-docs-pipeline.md`, `book-outline.md`,
  **`code-generator-architecture.md`** (32 KB — codegen home),
  `composable-function-algebraic-identity.md`, **`conditional-refactoring-rules.md`** (16 KB —
  conditional-rules home), `content-area-volume.md`, `contraction-and-dot-definitions.md`,
  **`design-decisions.md`** (60 KB — the big design-rationale home), `dot-wedge-projection-rejection.md`,
  `galgebra-comparison.md`, `generated-algebra-generation-cost.md`,
  **`generated-product-typing.md`** (26 KB), `geometric-product-associativity.md`,
  `graded-subspaces-vs-subalgebras.md`, `openstax-math-pedagogy.md`, `pseudoscalar-square-sign.md`,
  `symbolic-equality.md`, **`transform-and-composable-function-layer.md`**,
  `type-annotation-exemptions.md`, `unit-bivector-and-rotors.md`.
- **New reference docs this plan proposes** (only where no home exists):
  `tasks/reference/python-coding-standard.md` (the coding-standard judgment-call prose).

## Method (for whoever executes this)
1. For each MOVE, **verify the content is not already in the destination reference doc**
   before copying — much of the Architecture / Code-generation prose is a *duplicate* of what
   `design-decisions.md`, `generated-product-typing.md`,
   `transform-and-composable-function-layer.md`, `unit-bivector-and-rotors.md`,
   `blade-dict-interchange.md`, and `code-generator-architecture.md` already hold. Where it is
   already there, the CLAUDE.md text just becomes a one-line pointer (no copy needed). Where it
   is genuinely only in CLAUDE.md, append it to the named doc (or create the one new doc).
2. Preserve every existing outbound pointer (`tasks/reference/…`, `tasks/archive/…`) — when a
   paragraph collapses to a pointer, keep its `tasks/…` cross-links in the destination doc.
3. **Guardrails and conventions the agent must follow while writing code STAY** as terse
   one-liners (they steer behaviour every session); their *rationale/worked-examples* MOVE.
4. Do NOT edit source, do NOT `git add`/commit — that is the execution task, not this plan.

## Stay vs move (section-by-section)

| CLAUDE.md section (heading) | ~bytes | Verdict | Destination |
|---|---|---|---|
| intro ("# gacalc" what-this-is) | 596 | STAY (trim to ~1 short para) | CLAUDE.md |
| Module layout | 9,620 | TRIM — keep a lean one-line-per-file dir map; MOVE the deep per-file design records (𝒢₂ quarter-turn narrative, `Odd_3` subspace detail, the multi-para Layering *relaxation* narrative + the `to_matrix` reach-up rationale, the vendored-Emacs *why*) | CLAUDE.md keeps the file list + the one-line "vendored Emacs tree is off-limits" guardrail + a one-line acyclic-layering invariant; rationale → `design-decisions.md` (layering), `graded-subspaces-vs-subalgebras.md` (Odd_3, already there), `tasks/archive/2026/09/06/add-quarter-turn-to-g2.md` (quarter turn, already linked) |
| Architecture | 22,619 | MOVE (biggest offender) — keep only the *interchange-primitives contract* (what a concrete class must supply) and the terse *conventions* (build vectors from basis constants; make unit `1` explicit; no local aliases for named blades; express rotations via the factories, never hand-built); MOVE all deep mechanics + every "Caveat —" block (frozen+slots quirk, frozen≠hashable, coefficient-view `Gn` re-simplify, custom blade symbols, `Coef` vs `numbers.Real`, magnitude numeric-preservation, project/reject grade-narrowing, rotor sandwich derivation, quarter-turn exactness) | CLAUDE.md keeps ~4 short guardrail lines + pointers; rationale → **`design-decisions.md`** (frozen/immutability, Gn/G, coefficient type, magnitude preservation, terminology, custom blade symbols), **`transform-and-composable-function-layer.md`** (composable-function hierarchy, rotations/rotors, quarter turn), **`unit-bivector-and-rotors.md`** (`i`/plane), **`blade-dict-interchange.md`** (iteration/coefficient readback, already there), **`generated-product-typing.md`** (project/reject narrowing, already there) |
| Operators | 3,052 | STAY (a genuine every-session cheat-sheet) — lightly TRIM the deep parentheticals (the multi-line `i`/`.i()` classmethod-vs-instance explanation, the `exp()` Minkowski-boost aside) to a symbol + one-clause gloss + pointer | CLAUDE.md; deep glosses → `unit-bivector-and-rotors.md`, `contraction-and-dot-definitions.md` (both already exist) |
| Code generation | 7,197 | MOVE — keep the **"generate first, study real files, then fix the generator, never hand-edit output"** guardrail and the **"a correct generator change shows as a `tools/` diff and nothing under `src/gacalc/`"** review note (both are behaviour-steering, every session); MOVE the AST/`astbuild`/`cse` mechanics, the doc-region-marker naming design, the where-generation-happens dist/wheel detail | CLAUDE.md keeps ~2 guardrail lines + pointer; mechanics → **`code-generator-architecture.md`** (already the home), generation-cost → `generated-algebra-generation-cost.md` (already there) |
| Coding standard (Python) | 17,347 | MOVE the bulk — keep the split's headline ("(a) ruff enforces mechanically — green ruff is authority; (b) judgment calls") + the handful of **repo-specific invariants** the agent must obey (the protected `m`/`b` names; externally-defined names win over house style; line-length is the formatter's job not a design input; `cls` for a class-object local; dimension is `n` never `grade`); MOVE the full (b) prose (naming grammar, expressions/CQS, reduce-with-`sum`, idioms checklist, type-annotation policy, generics parameterization, inline-once, extraction rules, comments, modern-Python list) | CLAUDE.md keeps ~8-10 lines + pointers; full prose → **new `tasks/reference/python-coding-standard.md`**; conditional Rules A-E already in **`conditional-refactoring-rules.md`** (cross-link, don't duplicate); annotation exemptions already in `type-annotation-exemptions.md` |
| Dev workflow | 9,316 | STAY the commands + named gates (TRIM) — keep `make test` / `make shell` / `make dist` / `make upload` / `make release` / `make check-generated` / `make docs` / `make check-changelog` + `entrypoint/format.sh` (ruff+ty+changelog gate) with one-line each; MOVE the deep rationale (why generated code is skipped by the gate, the full single-file-`ty`-is-invalid explanation, the PyPI-403 troubleshooting catalogue, the jupytext/labextension bake details, the savefig-inside-`with` verification lesson) | CLAUDE.md keeps the command list + gate names; rationale → **`design-decisions.md`** (gate-skips-generated, ty full-context), **`book-and-docs-pipeline.md`** (docs build, already there); PyPI-403 + release auth → `design-decisions.md` or a short `releasing-and-pypi.md` note (see Open questions) |
| Performance | 363 | TRIM to a one-line pointer ("specialized classes are 15-35× (numeric) / thousands× (symbolic) faster than `Gn`; `python tools/bench.py`") | CLAUDE.md one line; any detail → `design-decisions.md` |
| Assessment / known issues | 939 | TRIM — keep the two genuinely-open limits as one line each (fixed Euclidean signature; self-flagged `inverse`/`is_parallel_to` uncertainty); drop the resolved-item narration | CLAUDE.md (short open-issues list per the "open-issues only genuinely open" rule) |
| Future directions | 2,588 | MOVE — the "graded subtypes — built" block is history (a resolved future-direction), collapse to one line + pointer; keep only the still-undecided **paravectors** note (one line) | CLAUDE.md one line (paravectors); the built-graded-subtypes history → `design-decisions.md` / already-linked archives |

## Projected result
- **Trimmed CLAUDE.md ≈ 17-18 KB (~4.5K tok)** — down from 74,732 B / 18.7K tok, a **~76%
  reduction** in per-turn context cost.
- **New reference doc:** `tasks/reference/python-coding-standard.md` (the coding-standard
  judgment-call prose).
- **Updated (appended-to) reference docs, only where content isn't already present:**
  `design-decisions.md`, `transform-and-composable-function-layer.md`,
  `code-generator-architecture.md`. Most Architecture / Code-generation prose is expected to be
  a *duplicate* of existing docs and collapses to pointers with **no copy** — verify per the
  Method step 1.
- **CLAUDE.md retains, in lean form:** the what-this-is paragraph; the one-line-per-file module
  map; the interchange-primitives contract; the terse coding + rotation + basis-constant
  conventions; the generate-first / `tools`-diff guardrails; the vendored-Emacs off-limits rule;
  the full `make` command + gate list; the two open issues; and one-line pointers into
  `tasks/reference/`.

## Open questions (for the maintainer)
1. **Coding-standard reference doc — new file, or fold into an existing one?** The (b)
   judgment-call prose (~10 KB) has no single reference home today (only the *conditional*
   subset lives in `conditional-refactoring-rules.md`). Recommendation: **create
   `tasks/reference/python-coding-standard.md`** and cross-link it to
   `conditional-refactoring-rules.md` and `type-annotation-exemptions.md`, rather than bloating
   the 60 KB `design-decisions.md`. OK to proceed on that, or would you prefer it folded into
   `design-decisions.md`?
2. **Target leanness — ~4.5K tok (this plan) or push harder to ~3K?** The ~17-18 KB target
   keeps the Operators cheat-sheet and the full Dev-workflow command list inline (both are
   high-value every session). A more aggressive cut would pointer-ize Operators too.
   Recommendation: **keep the ~4.5K target** — Operators and the command list earn their inline
   place. Want the more aggressive cut instead?

## Related
- runCrushInContainer `tasks/reference/crush-context-assembly.md` — the measurement + method.
- runCrushInContainer `tasks/investigate-context-bloat-geometricalgebra.md` — the diagnosis this
  follows from.
- This repo's own convention (inside `CLAUDE.md` and `~/.claude/CLAUDE.md`): "keep `CLAUDE.md`
  lean and push detail into `tasks/reference/`."
