# Audit the Dockerfile package list for CLI tools the gates/CI need

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 3
**Difficulty:** 2
**Created:** 2026-09-30 **Updated:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

A GitHub Actions job died with `cmp: command not found` — the image did not install `cmp` (from
**`diffutils`**), which `make check-generated` uses to compare the twice-generated `g*.py`. That
one-package fix landed in `d478c9d` (2026-09-30). This task was the **broader audit**: enumerate
every CLI tool each gate / CI job / entrypoint script shells out to, cross-check against what the
install scripts put in the image, and add anything missing. **Finding: `diffutils` was the only
gap. No additional packages are needed** — every other container-side gate tool is already in the
right install group, and the one tool CI uses that the image intentionally lacks (`git` for
`check-format`) runs on the host runner, not in the image. CI is green. The durable rule and the
gate → tool → group map are now recorded in `CLAUDE.md` › Continuous integration.

## The audit (what was checked, and the result)

CI is a thin wrapper over `make` (`.github/workflows/checks.yml` + `lean.yml`), so the audit
enumerated the tools each gate shells out to **inside the container** and matched each to an
`entrypoint/0N-install-*.sh` group (the Dockerfile dispatches these by ARG; `git grep` of the
Makefile gate targets, the workflow YAML, `entrypoint/format.sh`, `proofs/check.sh`, and the
`subprocess` calls in `tools/*.py`):

| Gate (CI job)                     | Container-side CLI tools                          | Install group / source           |
|-----------------------------------|---------------------------------------------------|----------------------------------|
| `check-generated` (`generated`)   | `python3`, `cmp` (diffutils), `cp`/`mkdir`/`basename` (coreutils) | base `01` (diffutils added `d478c9d`); coreutils is Fedora-base |
| `check-regions` (`generated`)     | `python3`                                         | base `01`                        |
| `test` (`test`)                   | `pytest` (`python3-pytest`), `python3`            | base `01`                        |
| `check-format` (`format`)         | `ruff`, `ty`, `python3`; `git diff` runs on the **host** runner | base `01`; `git` = host/runner   |
| `lean` (`lean.yml`, `v*` tags)    | `lake` (elan), `git`, `cp`/`grep`                 | `install-lean.sh` (elan + `dnf install git`) |
| `docs` (`make docs`, not per-push)| `convert` (ImageMagick), `gs` (ghostscript), `elaps`/`epix`, `g++`, texlive, `jupytext`, `sphinx-build`, `make` | `06-install-epix.sh` + `04-install-docs.sh` (+ `make`, present in image) |

Findings:

- **`diffutils` (`cmp`) was the only missing package**, and it was already fixed in `d478c9d`
  before this audit ran. No other gate shells out to a tool absent from its image.
- **`git` is deliberately NOT in the base image.** CI's `check-format` runs `make format` in the
  container then `git diff --exit-code` on the **host** runner (ubuntu-latest ships git). The only
  container-side `git` use is `lean`'s `lake` (Mathlib is a git dependency), and `install-lean.sh`
  installs git itself. So no base-image git is needed — matching the project's "git is a host-side
  concern" convention.
- **`tools/gen_specialized.py`'s only `subprocess` call is `ruff check --fix`** (best-effort,
  stdout/stderr discarded); `ruff` is in the base group. `render_epix_figures.py` shells out to
  `elaps`/`convert`/`magick`/`gs` (all in `06`) and uses `shutil.which` to degrade gracefully.
- **coreutils** (`cp`/`mkdir`/`basename`/`grep`) is always present in the Fedora base image; only
  `cmp`'s `diffutils` had to be added explicitly — that is exactly the gap that bit.
- **CI builds the image for the container-side steps.** `checks.yml` passes
  `BUILD_DOCS=0 USE_EMACS=0 USE_SPYDER=0` (a leaner image) but keeps `USE_LEAN`/`USE_EPIX` at their
  defaults; none of its four gates need docs/emacs/spyder tools, so the lean CI image still carries
  everything they shell out to.

## Fix delivered

No source/package change in this task (the audit confirms completeness). The durable deliverable is
a generalized rule added to `CLAUDE.md` › Continuous integration: *every CLI tool a containerized
gate shells out to must be installed by an `entrypoint/0N-install-*.sh` group; a missing one fails
only on the clean runner* — the diffutils lesson, next to the sibling `: image`-prereq gotcha, with
this task's gate → tool → group map cited.

## Open questions

None.
