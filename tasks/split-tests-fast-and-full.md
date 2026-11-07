# Split the tests into a fast everyday suite (`make test`) and a full suite (`make test-full`) for CI

**Created:** 2026-11-07 (William Emerison Six <billsix@gmail.com>): "make a task to investigate breaking
the unit tests up into two suites, with two make targets, like the existing test target would do the
non-slow tests, and a make test-full, where the make unit-test-full would be part of the github cicd
suite, but not part of every day development" · **Done:** 2026-11-07

## BLUF

`make test` now skips the tests marked `slow` and runs in **1:11** (792 tests); `make test-full` runs all
803 in about 26:30 and is what CI's `test` job runs. Eleven 3D symbolic frame cases carry the mark, chosen
from measured times. CLAUDE.md's dev-workflow and CI sections describe both targets and when to mark a
test slow.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-07: "1) sure 2) sure 3) sure")

1. Threshold: a test is slow if it takes over 10 s in the container.
2. CI runs the full suite on every push and PR, replacing `make test` in `checks.yml`.
3. Target name: `test-full`.

The maintainer asked for a commit after each step.

## What changed

- `pytest.ini` registers the `slow` marker. `Makefile`: `test` runs `pytest -m "not slow"`; the new
  `test-full` (`: image`, `## `-documented) runs everything. `.github/workflows/checks.yml`: the `test`
  job runs `make test-full`.
- `tests/test_frame.py`: `FRAMES_WITH_SLOW_3D_SYMBOLIC` is `FRAMES` with the `gn-3d-symbolic` case marked,
  used by the four tests whose 3D symbolic case is slow (`test_orthogonal_frame_keeps_the_first_…`,
  `test_hestenes_parallel_to_rejection`, `test_hestenes_inverse_equals_rejection_exactly`,
  `test_last_reciprocal_vector_is_the_last_rejection`); the other `FRAMES` tests keep their 3D case
  (under 9 s). It imports `ParameterSet` from `_pytest.mark.structures`, because pytest 9.1 does not
  export it.
- `tests/test_frame_class.py`: the `frame_3d` / `3d` cases of `test_inverse_methods_are_equivalent_symbolic`,
  `test_composed_round_trip_is_identity_symbolic` (both methods), `test_coefficients_are_triangular_…`,
  `test_coefficients_rebuild_the_vectors`, `test_squared_lengths_are_ratios_of_span_volumes` and
  `test_orthogonal_vectors_are_mutually_orthogonal` are `pytest.param(..., marks=pytest.mark.slow)`. Test
  IDs are unchanged.

## Measured

- Full run with per-test durations: 803 passed in 26:26; ten tests over 10 s, 1521 s of the total (the
  slowest `test_inverse_methods_are_equivalent_symbolic[3d]`, 470 s).
- First `make test` run after marking those ten: 4:40, because
  `test_coefficients_rebuild_the_vectors[frame_3d]` took 223 s. In the full run it had taken 4 s only
  because the triangular test before it had already simplified the same 3D coefficients, and sympy
  caches. Marked it too; `make test` then took 1:11, slowest remaining test 9.5 s. CLAUDE.md now says to
  time a candidate in `make test`'s own run.
- The per-test data and the discovery script were in `tasks/adhoc/split-tests-fast-and-full/`, removed at
  archive (in git history).

## Gates

`entrypoint/format.sh` green after each step. The marks change no test body; the full suite passed (803)
on the unmarked code at the start of the task, and `-m slow` collects exactly the marked eleven.
