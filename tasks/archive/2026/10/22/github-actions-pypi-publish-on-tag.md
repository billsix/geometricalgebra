# GitHub Actions: PyPI publish on tag (release automation)

**Created:** 2026-09-26 · **Completed:** 2026-10-22 (declined)

The proposal was to automate a PyPI release when a `v*` tag is pushed, as a thin `checkout → make`
workflow, replacing the interactive `make dist`/`upload`/`release` steps. It was spun off from
`tasks/archive/2026/09/26/github-actions-ci.md` (that task's Phase 2 / open question 3), whose Phase 1
check-only CI was complete. **Nothing was implemented: the maintainer declined it.**

## Decision (William Emerison Six <billsix@gmail.com>, 2026-10-22)

**Declined. Releases stay manual** — `make dist` / `make upload` / `make release` plus a host `git
tag`; gacalc does not add a tag-triggered PyPI publish to CI. The doc was archived on the maintainer's
instruction; restore it from the archive if the decision is ever reconsidered. Both questions the
proposal raised became moot with the decline:

1. Automate the publish with **Trusted Publishing (OIDC)** — the agent's recommendation, no token secret
   in the repo, but a one-time PyPI-side config only the maintainer could do — or keep the manual
   `make release`? Answered: keep it manual.
2. Gate the publish on the tag-triggered `lean.yml` (recommended, since a release with a broken proof
   corpus is what the tag gate exists to catch) or run them independently? Moot.

## Background (as of the decision)

- **Phase 1 CI** (`.github/workflows/checks.yml`) runs `format`, `test` and `generated` as thin
  `checkout → make <target>` wrappers, under the "CI is a thin wrapper over the make/Dockerfile system"
  principle any release workflow would also have had to follow.
- **gacalc publishes to PyPI** (`github.com/billsix/geometricalgebra`), unlike modelviewprojection, a
  book/app that pushes a container image to ghcr — so there was no `image-push`/ghcr step to consider.
- **The manual release path already worked**, so automation was a choice, not a gap: `make dist`
  (sdist + wheel in-container, `GACALC_DIMS=1,2,3,4,5`), `make upload` / `make upload-test`
  (interactive `twine`), and `make release` (host version-tag guard that refuses if a `v<version>` tag
  exists, + upload + host `git tag`). Auth is an API token via `~/.pypirc` (mounted read-only) or
  `TWINE_PASSWORD`.
- `.github/workflows/lean.yml` (added 2026-09-27) already triggers on `v*` tags and runs `make lean`.

## The design that was not built

For reference if the decision is revisited: a `release.yml` on `v*` tags — `checkout` (fetch-depth 0 if
`git describe` is needed) → `make dist BUILD_DOCS=0 …` → publish with `pypa/gh-action-pypi-publish`
under `permissions: id-token: write` and no token secret (the maintainer adds the trusted publisher on
PyPI once: project → Publishing → repo + `release.yml` + environment). All build logic stays in `make`
targets, reusing `make release`'s version-tag guard so tag and `pyproject.toml` version can't drift;
optionally attach `dist/*` to a GitHub Release via `softprops/action-gh-release@v2`; pin
`actions/checkout@v5` (Node 24). A real publish can't be dry-run safely (PyPI permanently rejects a
re-used version), so it would be rehearsed against TestPyPI first, with the first real `v*` tag as the
live test.

## See also

- `tasks/archive/2026/09/26/github-actions-ci.md` — Phase 1 (this was its spun-off Phase 2).
- mvp's sibling release workflow (ghcr + tarball + GitHub Release): `.github/workflows/release.yml`
  and github.com/billsix/modelviewprojection `tasks/github-actions-release-ci.md`, both in that repo.
