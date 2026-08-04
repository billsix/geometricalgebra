# Add a changelog / release notes flagging breaking API changes

**Status:** proposed — needs go-ahead
**Priority:** 4
**Difficulty:** 2

## Why (the motivating incident, 2026-08-04)

gacalc 0.0.15 shipped two changes together: the graded module constants (intended), and — from an
earlier commit (`c86adad`) — the `is_close` → `isclose` rename plus the removal of the old hidden
`1e-5` tolerance default (now `rel_tol=0.0`/`abs_tol=0.0`; see `tasks/reference/approximate-float-equality.md`).
The isclose change is a good, deliberate design. But it is a **breaking public-API change**, and
gacalc has **no changelog / release notes**, so the downstream consumer
(`github.com/billsix/modelviewprojection`) had no signal: bumping its pin `0.0.14 → 0.0.15` broke
its test suite silently (36 `.is_close()` call sites), discovered only by running the tests.

## The suggestion

Keep a lightweight **`CHANGELOG.md`** (or a "Release notes" section in `README.md`), one entry per
released version, that flags **breaking changes** — renamed/removed public methods, changed
defaults, changed return types — so a consumer bumping the pin knows what to migrate. It doesn't
need to be exhaustive; the bar is "would this break someone who imports gacalc?".

Retro-fill at least the recent breaking ones a consumer would hit:
- `0.0.15`: `is_close` → `isclose`, and its tolerances no longer default to `1e-5` (now `0.0` — a
  bare `isclose(a, b)` is exact equality; callers pass `rel_tol`/`abs_tol`). Module constants
  `from gacalc.g2 import e_1` are now the **graded** type (`Vector2`), not `G2`.
- `0.0.14`: value types became **frozen** (immutable) — mutate by rebinding.

Optionally wire a release-time reminder (the `make release` flow) to bump the changelog alongside
`pyproject.toml`'s `version`.

## Notes

- Origin: Bill (2026-08-04) — "add a task to gacalc for whatever you suggest for this." The isclose
  *default itself* is intentional and documented (`tasks/reference/approximate-float-equality.md`);
  the real gap this exposed is the lack of breaking-change communication to consumers.
- Consumer-side fix already done: mvp migrated its callers (mvp
  `tasks/gacalc-0015-isclose-tolerance-migration.md`).
