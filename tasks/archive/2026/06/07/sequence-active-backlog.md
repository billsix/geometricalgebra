# Sequence the active tasks/ backlog (dependencies + line-churn coordination)

**Created:** 2026-06-06 · **Completed:** 2026-06-07

## What it was

Nine task docs were in flight on 2026-06-06, several with hard dependencies (an open decision gating
another) and several editing the same lines of `base.py`, the generator and the tests. This task decided
an order so nothing was built that a pending decision might moot, and so no two annotation/refactor
passes churned the same lines. It changed no source itself, and it served as the living execution
tracker while the backlog ran; it was archived once that coordination job was finished. The sequence
was kept here rather than promoted into CLAUDE.md or a `tasks/README.md` (no longer exists): it was
working state, not a stable convention.

## The backlog (snapshot 2026-06-06) and its records

1. `tasks/archive/2026/06/06/add-python-types.md` — annotate local variables in source + generator.
2. `tasks/archive/2026/06/06/basis-vector-construction.md` — rewrite test/bench dict literals as basis
   combinations.
3. `tasks/archive/2026/06/06/clarify-2d-only-transforms.md` — the planar 2D transforms.
4. `tasks/archive/2026/06/06/codegen-checkin-strategy.md` — check in generated code or not.
5. `tasks/archive/2026/06/12/display-simplify.md` — simplify G1/G2/G3 coefficients on display.
6. `tasks/archive/2026/06/06/future-annotations-drop-forward-ref-quotes.md`.
7. `tasks/generalize-reject-reflect-higher-grade.md` — reject/reflect for grade-3+ blades.
8. `tasks/archive/2026/06/06/regen-diff-ci-guard.md` — CI guard that committed `g*.py` matches the
   generator.
9. `tasks/archive/2026/06/06/transform-type-roundtrip-tests.md`.

Plus two doc tasks created alongside: `tasks/archive/2026/06/06/refresh-claudemd-known-issues.md` and
`tasks/archive/2026/06/06/document-rotor-methods.md`, both editing CLAUDE.md, so done together.

## Dependencies found

- **#4 gated #8.** The regen-diff guard assumed generated code was checked in; if #4 chose runtime
  generation, #8 would be meaningless.
- **#6 → #1 → #2 line-churn cluster.** #6 changed annotation semantics module-wide, so it went first
  and #1 annotated the final form; #2 rewrote the same test lines #1 annotated, so it followed #1.
- **Generator-touching work before #8.** #1 (and #5, if done through the generator) changed the
  generated `g*.py`, so they had to settle before the guard was switched on.
- **Independent:** #7 (localized to `reject`/`reflect`, but gated on the author re-reading Hestenes
  p. 18 — a content gate); #9 paired with #3 (shared transform test fixtures); #5.

## Order and what happened (2026-06-06)

1. **The two doc tasks** — done, archived.
2. **#4 → Option 1, keep generated code checked in.** The library is pedagogical, and a `pip install`ed
   student must be able to read the specialized closed forms; runtime generation produces no readable
   source. This unblocked #8. (It was revisited the next day by
   `tasks/archive/2026/06/07/build-time-codegen-dist.md`, which moved to build-time generation.)
3. **#6 — done for `base.py`:** `from __future__ import annotations`, forward-ref quotes dropped (the
   alias stays quoted, being runtime); 141 tests and `ty` clean. The `gn.py` + generator part was folded
   into #1.
4. **#1 — done:** light-touch local annotations across `base.py` / `gn.py` / `transforms.py` /
   `nbplotutils.py` / the generator, plus the folded-in future-annotations in both generated headers;
   141 tests, `ty`, `ruff` clean.
5. **#2 — done:** `test_graded.py`'s `gn({...})` expected values became module-qualified basis
   combinations (`3 * gn.e_1 + 4 * gn.e_2`, wedges for blades); `test_multivector.py` (circular product
   ground truth) and the dense bench/conformance dicts were left as they were. 141 tests.
6. **#8 — done:** `make check-generated` (regenerate, then `git diff --exit-code` the committed files);
   verified exit 0 when clean and 1 on drift; documented in CLAUDE.md and README.
7. **#9 — done:** new `tests/test_transforms.py` (type round-trip over Gn/G1/G2/G3, plus value,
   invertibility and error-path tests).
   **#3 — resolved by removal:** the author chose to delete the planar 2D factories (`rotate`,
   `rotate_90_degrees`, `rotate_around`, `scale_non_uniform_2d`, and the unused
   `is_clockwise`/`is_counter_clockwise`) instead of guarding them — they were modelviewprojection
   artifacts, and GA rotation is the rotor. The two notebooks got a local rotor-based `rotate` helper;
   161 tests.
   **`tasks/archive/2026/06/06/rotor-callers-keyword-args.md` — done:** positional
   `rotor_from_vectors(...)` / `rotate(...)` calls became keyword form across the tests and three
   notebooks. Renaming `create_rotor` was declined; keyword calls gave the readability.
8. **#5 and #7** were left to their own task docs, to be scheduled by appetite (#5 needed a go/no-go;
   #7 waited on the Hestenes re-read). `build-time-codegen-dist` ran as a parallel investigation
   requested by the author on 2026-06-06, and was completed.

Questions raised while sequencing were settled by events: #4 was decided without a runtime-generation
prototype; #6 was done; #2 and #9 turned out to touch different test files.
