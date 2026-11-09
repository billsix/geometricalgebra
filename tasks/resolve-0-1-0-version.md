# Resolve the unreleased `0.1.0`: the changelog heading has no tag or PyPI release

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 2
**Created:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §8.3

## BLUF

`pyproject.toml` says `version = "0.1.0"` and `CHANGELOG.md` has `## [0.1.0] — 2026-09-28`, but 0.1.0
was never tagged or released. The newest tag and the newest PyPI release are both `0.0.20`. Done means
the version, the changelog and the next release agree: `## [0.1.0]` is folded back into
`[Unreleased]`, or released, and the next version number is decided.

## Context

Read first: `CLAUDE.md` › "Dev workflow" (`make dist` / `upload` / `release`) and the cross-project
`versioning-and-changelogs.md` (github.com/billsix/runClaudeInContainer `tasks/reference/`). Re-checked
2026-11-09:

- `git tag --sort=v:refname | tail -1` → `v0.0.20`. A text sort puts `v0.0.9` last, so always sort as
  versions.
- PyPI JSON API (`https://pypi.org/pypi/gacalc/json`): `info.version` is `0.0.20`; there is no 0.1.0.
- `CHANGELOG.md`: `[Unreleased]` starts at line 12, `## [0.1.0] — 2026-09-28` at 195,
  `## [0.0.20] — 2026-09-06` at 224. The heading was promoted without a release.
- `[Unreleased]` holds ~180 lines, including a changed default (`Frame.to_invertible_function` now
  defaults to `"reciprocal"`). That is breaking, so pre-1.0 the next version is a minor bump.
- Split of work: the agent stages the version bump and the changelog edit; the maintainer tags and
  publishes.

## Plan

- [ ] Merge `## [0.1.0]`'s entries into `[Unreleased]`, keeping their categories and breaking-change
  callouts.
- [ ] Keep `pyproject.toml` at `version = "0.1.0"`. Leave `[Unreleased]` unpromoted until release
  time, when it becomes `## [0.1.0] — <release date>`.
- [ ] Run `make check-changelog` (the version↔changelog guard), and update it if it expects a promoted
  heading for the current version.
- [ ] Hand off: the maintainer runs `make release` when ready.

## Decisions

1. Fold `0.1.0` into `[Unreleased]` and release the combined changes as `0.1.0`, since 0.1.0 was
   never published (William Emerison Six <billsix@gmail.com>, 2026-11-09).

## Open questions

None.
