# Split the tests into a fast everyday suite (`make test`) and a full suite (`make test-full`) for CI

**Status:** in progress — the maintainer approved it and answered the open questions (William Emerison
Six <billsix@gmail.com>, 2026-11-07)
**Priority:** 3
**Difficulty:** 3
**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "make a task to investigate breaking
the unit tests up into two suites, with two make targets, like the existing test target would do the
non-slow tests, and a make test-full, where the make unit-test-full would be part of the github cicd
suite, but not part of every day development"

## BLUF

The full `pytest` run takes 26:38 (2026-11-07), almost all of it in a handful of 3D symbolic frame tests.
Mark the slow tests, make `make test` skip them for everyday development, add `make test-full` that runs
everything, and make CI run `make test-full`. Done = both targets, the slow set chosen by measured time
(not by guess), `make test` timed, the CI job switched, and CLAUDE.md's dev-workflow and CI sections
updated.

## Context

- Why it got slow: the frame inverses and `Frame.coefficients()` now use the named projection operations,
  which `Gn` simplifies after every product and inverse. Timings, before and after:
  `tasks/archive/2026/11/07/line-to-line-projection-invertible-function.md` and
  `tasks/reference/frames-qr-and-reciprocal-frames.md`, "The code form: one line-to-line projection". The
  slowest on 2026-11-07: `test_inverse_methods_are_equivalent_symbolic[3d]` 475 s,
  `test_composed_round_trip_is_identity_symbolic[3d-peel]` 415 s, `[3d-reciprocal]` 282 s,
  `test_coefficients_are_triangular_with_unit_diagonal[frame_3d]` 212 s, all in `tests/test_frame_class.py`;
  the next ones are 20–40 s.
- Today: `Makefile` target `test` (`: image`, regenerates, runs `python -m pytest`); `pytest.ini`
  (`testpaths = src tests tools`, `addopts = --doctest-modules`); no pytest markers are registered.
  `test-all-dims` (g1–g5, ~1.5 h) is the existing precedent for a slow, separate target.
- CI: `.github/workflows/checks.yml` job `test` runs `make test BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0` on
  every push and PR. CLAUDE.md "Continuous integration": every CI step is a make target, and every
  containerized target CI runs needs `: image`.

## Plan

1. Measure: `python -m pytest --durations=0` in the container; write the per-test times to
   `tasks/adhoc/split-tests-fast-and-full/data/durations.txt` (with the discovery command saved beside it).
2. Register a `slow` marker in `pytest.ini` (`markers = slow: …`, so `--strict-markers` stays possible) and
   mark the tests over the threshold (Open question 1) with `@pytest.mark.slow`, on the specific
   parametrized cases where only some cases are slow (`pytest.param(..., marks=pytest.mark.slow)`), so the
   2D cases keep running everyday.
3. `make test` runs `python -m pytest -m "not slow"`; `make test-full` runs everything, `: image`, with
   a `## ` description. Time `make test`.
4. Switch `checks.yml`'s `test` job to `make test-full` (Open question 2 for when).
5. CLAUDE.md: the dev-workflow bullet for `make test` / `make test-full` and the CI section;
   `tasks/reference/` if a testing reference doc covers the targets.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-07: "1) sure 2) sure 3) sure")

1. **Threshold:** a test is slow if it takes over 10 s in the container.
2. **CI runs the full suite on every push and PR**, replacing today's `make test` in `checks.yml`.
3. **Target name:** `test-full`.

The maintainer asked for a commit after each step.

## Open questions

None.
