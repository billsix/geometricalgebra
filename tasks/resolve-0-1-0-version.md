# Resolved the unreleased `0.1.0`: its changelog section folded into `[Unreleased]`, version back to `0.0.20`

**Created:** 2026-11-09 · **Completed:** 2026-11-09
**Source:** tasks/review/2026/11/08/repo-review.md §8.3
**Decision** (William Emerison Six <billsix@gmail.com>, 2026-11-09): fold `0.1.0` into `[Unreleased]`
and release the combined changes as `0.1.0`, since 0.1.0 was never published.

## What was found

`pyproject.toml` said `version = "0.1.0"` and `CHANGELOG.md` had `## [0.1.0] — 2026-09-28`, but 0.1.0
was never tagged or released. Sorted as versions (`git tag --sort=v:refname`), the newest tag is
`v0.0.20`. PyPI's JSON API (`https://pypi.org/pypi/gacalc/json`) also reports `0.0.20` as the latest.
The heading had been promoted without a release.

## What changed

- **`CHANGELOG.md`:** the `## [0.1.0]` section's two "Changed" entries (the BREAKING rotor → versor
  rename, and the widened `Sequence` parameters) and its one "Fixed" entry (numeric `==` no longer
  calls `sympy.simplify`) moved to the ends of `[Unreleased]`'s "Changed" and "Fixed". The heading is
  gone.
- **`pyproject.toml`:** `version` went from `0.1.0` back to `0.0.20`, the version actually released.
  - This departs from the plan, which kept `0.1.0`. `tools/check_changelog.py` (run by `make format`)
    requires a `## [<version>]` heading for the declared version, so `0.1.0` with no heading would
    fail the gate.
  - At `0.0.20`, `make release` refuses (the tag `v0.0.20` exists), which forces the bump.
- **The release path:** in one commit, bump `version` to `0.1.0` and promote `[Unreleased]` to
  `## [0.1.0] — <date>`; then run `make release`. That is the order the guard and the release target
  already enforce. `proofs/lakefile.toml`'s `version = "0.1.0"` is the Lean package's own version,
  unrelated, and was left alone.

## Verification

`python3 tools/check_changelog.py` passes. The changelog now runs `## [Unreleased]` → `## [0.0.20]`,
and both moved entries are under `[Unreleased]`.
