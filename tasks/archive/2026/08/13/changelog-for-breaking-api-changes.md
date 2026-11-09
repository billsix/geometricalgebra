# Add a changelog / release notes flagging breaking API changes

**Created:** 2026-08-04 · **Completed:** 2026-08-13

## Why (the motivating incident, 2026-08-04)

gacalc 0.0.15 shipped two changes together: the graded module constants (intended) and, from an
earlier commit (`c86adad`), the `is_close` → `isclose` rename plus the removal of the old hidden
`1e-5` tolerance default (see `tasks/reference/approximate-float-equality.md`). The isclose change
was deliberate and good, but it was a **breaking public-API change** and gacalc had **no
changelog**, so the downstream consumer (github.com/billsix/modelviewprojection) had no signal:
bumping its pin `0.0.14 → 0.0.15` broke its test suite (36 `.is_close()` call sites), found only by
running the tests. The maintainer (2026-08-04): "add a task to gacalc for whatever you suggest for
this." The real gap was breaking-change communication, not the isclose default itself.

## What was done

Created `CHANGELOG.md` (Keep-a-Changelog style, focused on breaking changes; the bar is "would
this break someone who imports gacalc?"), with the two recent breaking releases retro-filled and
versions verified against the git tags:

- `0.0.15`: `is_close` → `isclose`, with tolerances no longer defaulting to `1e-5`; module
  constants `from gacalc.g2 import e_1` became the graded type (`Vector2`), not `G2`.
- `0.0.14`: value types became frozen (immutable); mutate by rebinding.

An `[Unreleased]` section was scaffolded for the coming 0.0.16 rename entry.

## Deferred

Two optional items were left out of scope: (a) a README pointer to the changelog; (b) wiring the
`make release` flow to remind bumping the changelog alongside `pyproject.toml`'s version, since that
changes the release flow and needed its own decision.

## Related

The consumer-side fix was already done: mvp migrated its callers in
github.com/billsix/modelviewprojection `tasks/archive/2026/08/04/gacalc-0015-isclose-tolerance-migration.md`.
