# GitHub Actions: PyPI publish on tag (release automation)

## BLUF

Automate a PyPI release when a `v*` tag is pushed, as a thin `checkout → make` workflow, so a
tagged release builds and publishes the sdist+wheel without the current interactive
`make dist`/`upload`/`release` dance. **Done** = a `v*` tag push builds `dist/` in-container and
publishes it to PyPI (recommended: Trusted Publishing / OIDC, no token secret in the repo), with the
artifacts optionally attached to a GitHub Release — OR a deliberate decision to keep releases manual,
recorded here. **Blocked on a maintainer decision + one-time PyPI-side config that only the maintainer
can do; do not implement until that decision is made.**

## Status

**Status:** proposed — needs go-ahead (a maintainer decision, see Open questions)
**Priority:** 6
**Difficulty:** 4
**Started:** 2026-09-26 **Updated:** 2026-10-04 (William Emerison Six <billsix@gmail.com>) — spun
off from `tasks/archive/2026/09/26/github-actions-ci.md` (that task's Phase 2 / open question 3),
whose Phase 1 (check-only CI) is complete and archived.

## Context

- **Phase 1 CI is live** (`.github/workflows/checks.yml`): jobs `format`, `test`, and `generated`
  (the codegen determinism + doc-region gates), all thin `checkout → make <target>` wrappers. See
  `tasks/archive/2026/09/26/github-actions-ci.md` for the phase-1 record and the governing "CI is a thin wrapper over
  the make/Dockerfile system" principle that this task must also follow.
- **gacalc publishes to PyPI** (`github.com/billsix/geometricalgebra`), unlike modelviewprojection
  (a book/app that pushes a container image to ghcr). So gacalc's release story is **PyPI-first**;
  there is **no `image-push`/ghcr step**.
- **A working MANUAL release path already exists**, so automating it is a choice, not a gap:
  - `make dist` — build sdist + wheel in-container (`GACALC_DIMS=1,2,3,4,5`) into `$(DIST_DIR)`.
  - `make upload` / `make upload-test` — interactive `twine` to PyPI / TestPyPI.
  - `make release` — host version-tag guard (refuses if a `v<version>` tag exists) + upload + host
    `git tag`.
  - Auth today is an API token via `~/.pypirc` (mounted read-only) or `TWINE_PASSWORD`.
- **The version-tag guard in `make release`** should be reused so a tag can't publish a version that
  disagrees with `pyproject.toml`.
- **`.github/workflows/lean.yml` (added 2026-09-27, after this task) already triggers on `v*` tags**
  and runs `make lean`. A `release.yml` on the same trigger must decide its ordering relative to that
  Lean gate — publish only after `lean` passes (a `needs:`/workflow dependency), or run independently
  (Open question 2).

## Plan

- [ ] Decide the approach (Open question 1): Trusted Publishing (OIDC) vs. keep manual `make release`.
- [ ] If automating: add a `release.yml` triggered on `v*` tags, thin-wrapper style:
      `checkout` (fetch-depth: 0 if `git describe` is needed) → `make dist BUILD_DOCS=0 …` →
      publish. For **Trusted Publishing**, use `pypa/gh-action-pypi-publish` with
      `permissions: id-token: write` and **no token secret**; the maintainer configures the trusted
      publisher on PyPI once (project → Publishing → add repo + `release.yml` + the environment).
- [ ] Keep all build logic in `make` targets (add one only if a needed step isn't already a target);
      the workflow calls them. Reuse the `make release` version-tag guard so tag ↔ `pyproject.toml`
      version can't drift.
- [ ] Optionally attach `dist/*` (and possibly the `make docs` HTML/PDF) to a GitHub Release via
      `softprops/action-gh-release@v2` (as modelviewprojection's `release.yml` does).
- [ ] Pin `actions/checkout@v5` (Node 24). Agent stages the YAML; the maintainer commits.
- [ ] **Verification caveat:** a real publish can't be dry-run safely (PyPI permanently rejects a
      re-used version). Rehearse against **TestPyPI** first (`upload-test` / a test trusted
      publisher), and treat the first real `v*` tag as the live test — needs maintainer involvement.

## Open questions

1. **Automate the PyPI publish on a `v*` tag, or keep the manual `make release`?** Recommendation:
   automate with **Trusted Publishing (OIDC)** — no token secret in the repo, and it needs a
   one-time PyPI-side config only you can do (add the trusted publisher for this repo +
   `release.yml`). Keeping it manual is also legitimate if you'd rather gate every release by hand.
   (No ghcr/image-push step — gacalc doesn't push a container image.)
2. **Gate the publish on the tag-triggered Lean workflow?** (a) publish only if `lean.yml` passes
   on the same tag (recommended — a release with a broken proof corpus is the thing the tag gate
   exists to catch), or (b) run them independently?

## See also

- `tasks/archive/2026/09/26/github-actions-ci.md` — Phase 1 (this task is its spun-off Phase 2).
- `github.com/billsix/modelviewprojection` › `.github/workflows/release.yml` and
  `tasks/github-actions-release-ci.md` — the sibling release workflow (ghcr + tarball + GitHub
  Release); gacalc's differs by publishing to PyPI instead of pushing an image.
