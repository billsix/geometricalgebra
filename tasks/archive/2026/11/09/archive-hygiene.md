# Archive hygiene: done-record rewrites, "superseded" notes, and dangling references across `tasks/archive/2026/`

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** `tasks/review/2026/11/08/repo-review.md` §10.1, §10.2, §10.3
**Decision** (William Emerison Six <billsix@gmail.com>, 2026-11-09): do the full done-record rewrite,
not only the status lines.

## What changed

All 294 archived task docs dated before 2026-11-08 were rewritten by hand into past-tense
done-records (Status/Priority lines, Plan, Open questions, "Context (read first)", unchecked boxes
and "(original plan below)" text dropped; answered questions folded in as decisions; decisions,
rationale and verification facts kept). Docs dated 2026-11-08 or later were not touched, and no doc
was renamed or moved. The work was split into nine batches by date and done in three commits, one
per window:

| Window | Docs | Substantive / minimal | Superseded notes | Pointers fixed | SHAs | "Bill" replaced |
|---|---|---|---|---|---|---|
| June–July | 100 | 90 / 10 | 9 | ~100 | 3 repointed | ~105 |
| August–September | 76 | 64 / 12 | 1 | ~110 | 17 repointed, 1 dropped | ~75 |
| October – 2026-11-07 | 118 | 40 / 78 | 1 | ~110 | 14 repointed, 12 dropped | 1 |

Line counts: June–July went from about 11,600 to 5,650, August–September from 7,700 to 4,000, and
October–November from 8,500 to 6,400. The worst case, `tasks/archive/2026/08/15/redo-exp-book-referenced.md`,
went from 439 to 136 lines.

- **§10.2 superseded notes.** The six listed 06/06 docs each gained a one-line `**Superseded:**` note
  pointing at the reversing doc. Five more superseded notes (a header line, or a parenthetical in the first) were added where a batch found the same pattern:
  `07/18/python-programming-standard.md`, `07/21/emit-doc-region-markers.md`, `07/29/exp-for-rotors.md`,
  `09/27/minimal-nested-image.md` (its final implementation keys off `MINIMAL_IMAGE`) and
  `10/04/lean-lift-theorem-statements-to-objects.md`.
- **§10.3 references.** Moved `tasks/<slug>.md` pointers now cite their `tasks/archive/…` path;
  mvp, runClaudeInContainer, runCrushInContainer and epix-mirror docs are cited by GitHub URL plus
  their repo-relative path; wiki-links became repo-relative paths; `/mvp/…` and `/foo/opt/…` paths
  became URLs; pointers that resolve nowhere (`tasks/show-mult-expand.md`, `tasks/README.md`,
  `entrypoint/README`, mvp's `github-actions-format-ci.md`) say "(no longer exists)"; one-shot adhoc
  scripts are named bare with "(removed at archive; in git history)".
- **SHAs.** `6c88fae` → `9e28603` and `237ede7` → `a0bedea`, each checked by subject and date. The
  five dead SHAs in `10/09/coordinate-proofs-alongside-early-results.md` were dropped (`cc2ee40` kept).
  The workers also found SHAs that `git cat-file -e` accepts only because they survive locally as
  unreachable objects left by squashes. A fresh clone does not have them, so they were repointed to
  the reachable commit with the same subject and date (Odd_3's seven steps → `4e83680`, the 10/05 Lean
  commits → `dd68f6f`/`eca8310`/`ffa4c70`/`0ce631d`/`310d692`, the 10/08 branch commits → `95a941e`,
  `dbb8a1a`, `d7a067e`, `b28faa5`, `c23de63`, `26c9c8d`, `cfa2476`, and so on). Where no replacement
  exists, the hash was dropped: the 08/14 checkpoint `ac4ebfe`, the six quick-saves of
  `10/08/projection-standard-position-make-2d.md` (now "squashed into `000c759`"), and `bc5b32f`.
- **Names.** Bare "Bill" became "the maintainer" in prose and `William Emerison Six
  <billsix@gmail.com>` in dated stamps. The one in a verbatim quote (`10/09/coordinate-subscripts-indices-not-xyz.md`)
  became `[the maintainer]`.

## Method

`tasks/adhoc/archive-hygiene/discover.sh` produced the worklist; its pre-edit snapshot is in
`tasks/adhoc/archive-hygiene/data/` (`scaffolding.txt` 641 lines, `bill.txt` 298, `missing-paths.txt`
222, `dead-shas.txt` 26, `container-paths.txt` 9), with `pointer-map.txt` giving the replacement for
each known-missing path. Its SHA check was later tightened so that a SHA counts as dead unless it is
an ancestor of `HEAD`. `tasks/adhoc/archive-hygiene/gate.sh` re-runs discovery and applies the gate.

## Gate result (2026-11-09, after the phase-3 commit)

- No archived doc dated before 2026-11-08 has `^## Plan`, `^## Open questions`, `- [ ]`, a `**Status:**`
  line, "original plan" or "Context (read first)".
- No bare `Bill`; no `/mvp/` or `/foo/opt/` path.
- All 45 cited `tasks/…` paths that do not exist in this repo belong to another repo and carry its
  github.com URL on the same or the preceding (wrapped) line.
- Every gacalc SHA cited is reachable from `HEAD`. The 12 hashes that are not are all labelled in
  their sentence: four doc-region hashes (`07/21/emit-doc-region-markers.md`), galgebra `ff0a938`,
  epix-mirror `ebf3ca6…`/`275adef…`, multivariate-math `e9b088a`, and the image ID `b294e77bfbc7`.

## Exceptions left on purpose

- `[[…]]` in Python (`Callable[[V], V]`), TOML (`[[overrides]]`) and matrix literals is code, not a
  wiki-link, and was left.
- `10/05/python-book-rotor-naming-after-lean.md` still names `unit-bivector-and-versors.md` in its
  audit row, because that row describes the bad pointer that was fixed; the real path sits beside it.
- `10/20/prove-2d-rotations-commute.md` still cites Lean files by line number.
- Where a doc never recorded an answer, an outcome or a gate run, the record says so ("left
  unanswered", "left to the maintainer", "not run in this task") instead of guessing. A few outcomes
  were inferred from later evidence (the current Makefile, `git tag`, CHANGELOG), and the docs say
  where.
- `tasks/adhoc/archive-hygiene/` is a one-shot worklist, to be `git rm`'d in the archive commit.
