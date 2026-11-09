# Archive hygiene: done-record rewrites, "superseded" notes, and dangling references across `tasks/archive/2026/`

**Status:** proposed — needs go-ahead
**Priority:** 8
**Difficulty:** 6
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §10.1, §10.2, §10.3
**Decision** (William Emerison Six <billsix@gmail.com>, 2026-11-09): do the full done-record rewrite,
not only the status lines.

## BLUF

About 130 of the ~295 archived task docs still carry plan scaffolding, 6 state decisions that were
later reversed without saying so, and about 100 references in the archive dangle. Rewrite each
scaffolded doc into a lean, past-tense done-record, add a "superseded" note to each reversed decision,
and repoint or drop every dangling reference. Work in three phases by window, each its own commit.
Done means a re-run of the record's §10 checks finds nothing.

## Context

Read first:
- the done-record rules in github.com/billsix/runClaudeInContainer
  `tasks/reference/task-doc-conventions.md` ("Archiving");
- the record's §10 in full (`tasks/review/2026/11/08/repo-review.md`), whose lists are the worklist.

A done-record has one past-tense voice. It drops Plan, Open questions, "Context (read first)",
unchecked boxes and the stale `Status:` line, and keeps what was decided and why. Use
`tasks/archive/2026/11/09/backlog-hygiene.md` as a model.

- **§10.1 scaffolding, by window:**
  - **June–July** (100 docs): 47 still have Open questions, 40 a Plan, 25 unchecked boxes, 19 an
    "(original plan below)" section, and none has a BLUF. Several have Status lines frozen before
    commit ("awaiting author commit", "ready to tag v0.0.8", "ready to archive").
  - **August–September** (76 docs): 42 keep scaffolding. The worst is `08/15/redo-exp-book-referenced.md`
    (439 lines, "in progress"); the rest of the list is in the record.
  - **October–November** (~119 docs): a short list of unchecked plans and "Context (read first)" docs,
    two stale "Ready to archive", and 22 `10/09` docs with an empty "Open questions: None.".
- **Bare "Bill":** 159 times across 52 files. Rewrite each to "the maintainer" in prose, or
  `William Emerison Six <billsix@gmail.com>` in a stamp, during each doc's rewrite. Leave authorship
  credits as written.
- **§10.2, add a "superseded" note** (one line, pointing at the reversing doc):
  - `06/06/codegen-checkin-strategy.md`, reversed by `06/07/build-time-codegen-dist.md`;
  - `06/06/regen-diff-ci-guard.md`, superseded by gitignored output plus a determinism check;
  - `06/06/clarify-2d-only-transforms.md`, reversed when `rotate_90_degrees` returned g2-only on
    2026-09-06;
  - `06/06/add-python-types.md`, superseded by "annotate every binding";
  - `06/06/graded-blade-subtypes.md`, whose `Vector2`/`Rotor2`, shared `scalar.py` and "no Odd type"
    all changed later;
  - `06/06/inverse-exact-reciprocal-fix.md`, superseded by the 06/13 numeric-magnitude work.
- **§10.3 dangling references:**
  - **SHAs** (all 7 re-checked 2026-11-09 with `git cat-file -e`, all gone): `6c88fae` (likely now
    `9e28603`), `237ede7` (likely `a0bedea`), and `e6e1643`, `e5e829f`, `257b40a`, `bf026eb`,
    `76ac097` in `10/09/coordinate-proofs-alongside-early-results.md`. Find each replacement by subject
    and date (`git log --oneline`), or drop it.
  - **~100 `tasks/<slug>.md` pointers** that have moved: repoint each to its `tasks/archive/…` path.
    Cite mvp tasks by URL (github.com/billsix/modelviewprojection), and say so where one resolves
    nowhere (`tasks/show-mult-expand.md`).
  - **Wrong paths:** `tasks/archive/specialized-multivectors.md`, `…/06/05/…` (the real one is
    `…/06/03/…`), and `unit-bivector-and-versors.md` (the real file is `unit-bivector-and-rotors.md`).
  - **Container-absolute paths:** `/mvp/tasks/gacalc-math-migration.md` (×2), `/mvp/venv` and
    `/foo/opt/modelviewprojection`. Replace each with a URL.
  - **Others:** a missing `entrypoint/README` cited by `06/07/emacs-package-install-strategy.md:111`,
    and path-less wiki-links in 15 June–July docs.
- **Bulk-op method:** discover with `rg`, log the worklist to `tasks/adhoc/archive-hygiene/data/`, save
  the discovery command as `discover.sh`, and verify each phase by re-grep. The rewrites themselves
  are judgment work, so do them by hand, not by codemod. Don't archive or rename any doc.

## Plan

- [ ] Phase 1, June–July: the §10.1 rewrites, the six §10.2 notes, and the §10.3 fixes in this window.
  Commit.
- [ ] Phase 2, August–September: the same. Commit.
- [ ] Phase 3, October–November: the same. Commit.
- [ ] Gate: no archived doc has `^## Plan`, `^## Open questions`, `- [ ]` or a `**Status:**` line;
  every SHA resolves; every `tasks/…` path in the archive exists; no bare `Bill` outside authorship
  credits. Then `git rm` the adhoc worklist in the archive commit.

## Open questions

None.
