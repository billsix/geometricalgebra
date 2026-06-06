# Sequence the active tasks/ backlog (dependencies + line-churn coordination)

**Status:** in-progress — executing the decided order (gates resolved 2026-06-06)
**Started:** 2026-06-06

## Goal

There are nine in-flight task docs in `tasks/`. Several have **hard dependencies** on each other (one
is an open decision that gates another) and several **edit overlapping lines** in the same files
(`base.py`, the generator, the test suite), where their own notes already warn about churning the
same code twice. Decide an order so we don't (a) build something a pending decision might moot, or
(b) have two annotation/refactor passes fight over the same lines. Output is a decided sequence
recorded here; no source changes in this task itself.

## The active backlog (snapshot 2026-06-06)

1. `add-python-types.md` — **in-progress** — annotate local variables in source + generator.
2. `basis-vector-construction.md` — proposed — rewrite test/bench dict-literals as basis combinations.
3. `clarify-2d-only-transforms.md` — not started, low pri — guard/clarify the planar 2D transforms.
4. `codegen-checkin-strategy.md` — **open decision** — check in generated code vs. generate at runtime.
5. `display-simplify.md` — not started — simplify G1/G2/G3 coefficients on display.
6. `future-annotations-drop-forward-ref-quotes.md` — not started — `from __future__ import
   annotations`, drop forward-ref quotes.
7. `generalize-reject-reflect-higher-grade.md` — not started — reject/reflect for grade-3+ blades.
8. `regen-diff-ci-guard.md` — **ready to implement** — CI guard that committed `g*.py` matches the
   generator.
9. `transform-type-roundtrip-tests.md` — not started — tests that transforms preserve representation.

(Plus the two doc tasks created alongside this one: `refresh-claudemd-known-issues.md` and
`document-rotor-methods.md` — pure docs, can land anytime, but both edit CLAUDE.md so do them together.)

## Dependencies & conflicts found

### A. Decision gate: #4 blocks #8
`regen-diff-ci-guard` (#8) is "ready to implement" but its whole premise is that generated code is
**checked in** — it regenerates and `git diff --exit-code`s `g1/g2/g3.py` + `scalar.py`.
`codegen-checkin-strategy` (#4) is an open decision about whether to *keep* checking generated code in
at all (vs. generate at runtime/build time). If #4 flips to runtime generation, #8 becomes
meaningless. **#4 must be decided before #8 is built.** (#8's own doc already says it "assumes" the
checked-in model.)

### B. Line-churn cluster on annotations/syntax: #1, #6, #2
These three rewrite overlapping regions and each flags the coordination risk in its own notes:
- `add-python-types` (#1) adds local-variable annotations across `base.py` / `gn.py` /
  `transforms.py` and the generator's emitted locals.
- `future-annotations-drop-forward-ref-quotes` (#6) adds `from __future__ import annotations` and
  strips `"AbstractMultiVector"` quotes — changes annotation *semantics* module-wide.
- `basis-vector-construction` (#2) rewrites test/bench value construction; touches the same test
  lines #1 would annotate.
`#1`'s notes explicitly say "coordinate with use-match-and-modern-python so the two passes stay
consistent and don't churn the same lines twice"; `#6` was *split out* of that same modern-python
pass. **Order within the cluster matters:** do the semantics change (#6) first so #1 annotates the
final form, and decide #1-vs-#2 ordering for the test files.

### C. Anything touching the generator must precede #8
#1 modifies `tools/gen_specialized.py` (emitted-local annotations) and therefore the generated
`g*.py`. If the regen-diff guard (#8) lands first, #1's regen will trip it (expected, but noisy).
Any generator-affecting task (#1, and #5 if it overrides `_repr_latex_` via the generator) should
settle **before** #8 is switched on, or #8's first run will demand a regen commit.

### D. Independent / low-coupling (can slot anywhere)
- `generalize-reject-reflect-higher-grade` (#7) — localized to `base.py` `reject`/`reflect` + new
  tests; user wants to re-read Hestenes first (a *content* gate, not a code dependency).
- `transform-type-roundtrip-tests` (#9) — adds a new test file; only collides with #2 if both edit
  the same fixtures. Pairs naturally with `clarify-2d-only-transforms` (#3), which also wants
  transform tests (planar guard round-trips).
- `display-simplify` (#5) — generated-code change (override `_repr_latex_` on G1/G2/G3) → see C.

## Proposed sequence (for discussion, not yet approved)

1. **Land the two doc tasks** (`refresh-claudemd-known-issues`, `document-rotor-methods`) — zero code
   risk, removes misleading docs first.
2. **Decide #4** (codegen check-in strategy). Everything generator-related hangs off this.
3. **#6** (future annotations) — the module-wide semantics change, done before annotating locals.
4. **#1** (local annotations) — annotate the post-#6 form; includes the generator's emitted locals.
5. **#2** (basis-vector construction in tests/bench) — after #1 so test annotations and value
   rewrites don't collide; or interleave per-file if that reads better.
6. **#8** (regen-diff guard) — only after #4 is "keep checked-in" and after generator-touching tasks
   (#1, #5) settle, so the first guard run is clean.
7. **#9 + #3** (transform round-trip tests, then planar-guard + its tests) — share fixtures; do #9's
   type round-trips first, then #3 adds the planarity-guard tests on top.
8. **#5** (display simplify) and **#7** (reject/reflect higher grade) — independent; schedule by
   appetite. #7 waits on the author's Hestenes re-read.

## Decisions & progress (2026-06-06)

Gates resolved; order locked. (Numbers below are the "active backlog" indices above.)

- **Done — the two doc tasks** (`refresh-claudemd-known-issues`, `document-rotor-methods`): complete,
  archived under `tasks/archive/2026/06/06/`.
- **#4 codegen-checkin → Option 1 (keep generated code checked in).** Decided because the library is
  *pedagogical* and a `pip install`ed student must be able to read the specialized closed forms;
  runtime generation (option 2) produces no readable source. Archived. **This unblocks #8.**
- **#6 future-annotations → do it; `base.py` complete.** `from __future__ import annotations` added,
  forward-ref quotes dropped (alias stays quoted — runtime), 141 tests + `ty` clean. The `gn.py` +
  generator portion is **folded into #1** (recorded in that task's notes). Archived.

**Remaining order:** **#1 → #2 → #8 → #9 + #3 → #5 / #7.**

Next up: **#1 `add-python-types`** (now also carrying the `gn.py` / generator future-annotations work).

Answering this task's own meta-question: the sequence **stays here** as the living execution tracker
(updated as tasks land), rather than being promoted into CLAUDE.md — it's working state, not a stable
convention.

## Open questions

- Is the #4 decision actually ready to make now, or does it need a runtime-generation prototype first
  (its own doc offers to prototype `g2.py` as a dynamic builder for comparison)? That prototype, if
  wanted, is the real blocker.
- Within cluster B, is #6 worth doing at all? Its own "Open questions" asks exactly that (the
  forward-ref quotes are already few). If #6 is dropped, #1 proceeds without waiting.
- Do #2 and #9 actually collide in practice, or are they in different test files (`test_graded` /
  `test_conformance` / `test_multivector` vs. a new `test_transforms.py`)? If disjoint, they
  parallelize.
- Should this sequencing live here as a task, or be promoted into a short "backlog order" note at the
  top of CLAUDE.md / a `tasks/README.md` so it's visible without opening this file?
