# Reconsider checking in generated code: build-time generation + `make dist`

**Created:** 2026-06-06 · **Completed:** 2026-06-07

## What it was

The generated `scalar.py` / `g1.py` / `g2.py` / `g3.py` were moved **out of git** and produced at
build/dev time instead, automake-style: `make shell` generates them before the prompt, and
`make dist` builds a PyPI sdist + wheel with them baked in. This revisited the #4 decision in
`tasks/archive/2026/06/06/codegen-checkin-strategy.md` ("keep checked-in"), which had rested on
there being no build step. Since then the generator had become a `make` target (#8, `make
check-generated`), development had moved into `make shell`, and the author wanted a `make dist`.

The hard constraint from #4 was kept: a `pip install`ed student must be able to **read** the
specialized closed-form source. Build-time generation (#4's Option 3) bakes readable `.py` into the
wheel and sdist; runtime / on-import generation (Option 2) produces no readable source and stayed
rejected.

## Facts the design rested on

- **No chicken-and-egg.** `tools/gen_specialized.py` imports only the hand-written
  `geometricalgebra.base` + `geometricalgebra.gn`; there is no `__init__.py` and nothing imports the
  generated modules at package-import time, so a tree with the generated files deleted can still run
  the generator. (Tests, `tools/bench.py` and the `displayg2`/`g3`/`graded` notebooks do import them.)
- **Deterministic and idempotent** (proven by `make check-generated`); full regen took ~30 s, 𝒢₃
  dominating. `ruff` is best-effort in the generator, not a hard dependency.
- The repo is bind-mounted into the `make shell` container, so files generated there land in the
  host tree (gitignored).

## Decisions

- **Generation in `entrypoint/shell.sh`, unconditional,** before the editable install — not a
  setuptools hook firing during `-e .` (which runs `--no-build-isolation --no-deps --no-index`, so a
  hook would be fragile). Generate-if-missing in `shell.sh` was rejected because it would not pick up
  generator edits.
- **`setup.py` `build_py` hook generates only if the modules are missing** (chosen over "always
  generate"): build-from-repo regenerates, while building from a shipped sdist is a no-op. The
  release path (`make generate` / `make dist`) always regenerates explicitly, so releases are fresh
  and installs are cheap.
- **Bake the generated files into the sdist too**, so an sdist install needs no multi-minute
  generation.
- **`make check-generated` (#8) was repurposed** as a determinism check (regenerate twice, `cmp`),
  since there was no longer a committed copy to diff against.
- **`upload` / `release` stay separate from `dist`** — publishing is irreversible. PyPI permanently
  rejects a re-used version, so the version is bumped by hand in `pyproject.toml` and `make release`
  refuses if tag `v$(VERSION)` already exists, then `twine check` + `twine upload` + `git tag`.
  Pushing the tag stays the author's call. An automated bump target and a TestPyPI `make
  upload-test` were judged overkill for a solo pre-1.0 project and not added.
- The minimal alternative (keep the files in git and only add `make dist`) was weighed and not
  taken: build-time generation removes thousands of generated lines from history, cleans up diffs,
  and removes the regen-drift bug class. Its cost is a "generate before tests/IDE/bench" step for
  non-container dev, a hook to maintain, and build-requires.

## What changed

- `.gitignore` gained `/src/geometricalgebra/{scalar,g1,g2,g3}.py`; the four were `git rm --cached`.
- `entrypoint/shell.sh` runs `python tools/gen_specialized.py` before the editable install.
- `setup.py` — the generate-if-missing `build_py` subclass.
- `pyproject.toml` — `[build-system].requires = ["setuptools","wheel","numpy","sympy"]`,
  `readme = "README.md"`, and a `dev = ["build","twine"]` optional-dependencies group.
- `Makefile` — `generate`, `dist` (`generate` → `python -m build`), `upload`, `release`, and the
  repurposed `check-generated`.
- CLAUDE.md (Module layout / Code generation / Dev workflow) and README (Generating, plus a new
  "Building & publishing" section) were updated to the not-in-git model.

Corrections to the proposal found while implementing:

1. Build-requires needed **`numpy` as well as `sympy`**: the generator imports `geometricalgebra.base`,
   which imports `numpy`.
2. "sympy-free end users" was imprecise: `numpy`/`sympy` are runtime dependencies anyway. The accurate
   claim is that installing the **wheel** runs no build step and no generator; the pure-Python
   `py3-none-any` wheel matches every platform, so the sdist path is rarely hit.
3. `tools/gen_specialized.py` is not shipped in the sdist. That is harmless because the sdist always
   ships the generated files; a from-sdist regen would need `tools/` added via `MANIFEST.in`.

## Verification

`make generate` and `make check-generated` passed; `make dist` produced an sdist and a wheel that both
contain `scalar/g1/g2/g3.py`; `twine check` passed (after adding `readme`); the wheel installed in a
clean venv imported `geometricalgebra.g2` and built a `G2`; the `build_py` hook regenerated into the
wheel from a tree with no generated files; the full suite passed (161 tests).

Left undone on purpose: adding `--cgroups=disabled` to the `make shell` `podman run` (needed only for
nested runs in the sandbox, orthogonal to this task).

Related: `tasks/archive/2026/06/06/regen-diff-ci-guard.md` (#8, which this repurposed).
