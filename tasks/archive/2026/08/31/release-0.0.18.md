# Release gacalc 0.0.18 (cross product + blade display symbols)

**Created:** 2026-08-31 · **Completed:** 2026-08-31 (plan approved by William Emerison Six
<billsix@gmail.com>)

## What shipped

0.0.18 went to PyPI carrying the two features built 2026-08-31: the cross product
(`vectorcalc.cross`, `MultiVectorBase.cross`, generated `g3.Vector.cross` — see
`tasks/archive/2026/08/31/custom-symbols-and-vector-calc.md` and
`tasks/archive/2026/08/31/generated-vector-cross.md`) and the custom blade display symbols
(`set_blade_symbols`). It unblocked the downstream consumer task, github.com/billsix/modelviewprojection
`tasks/archive/2026/08/31/use-gacalc-cross.md`.

## Steps

- **Agent (staged):** `pyproject.toml` `version` bumped `0.0.17` → `0.0.18` (the v0.0.17 tag existed,
  and PyPI permanently rejects a re-used version). `CHANGELOG.md` got `[Unreleased]` entries for both
  features and a retro-filled `[0.0.17] — 2026-08-23` section, since that tag had shipped with no
  entry; it was reconstructed from `git log v0.0.16..v0.0.17` (breaking: exp-of-vector raises, the
  generated `dual` is dimension-locked).
- **Maintainer (host):** committed the staged work, promoted `[Unreleased]` to
  `## [0.0.18] — 2026-08-31`, and ran `make release` — sdist+wheel built in the container with
  `GACALC_DIMS=1,2,3,4,5` (about 90 minutes: g4 ~5 min, g5 ~87 min), containerized `twine upload`,
  then the host `git tag v0.0.18`, which was pushed.

## Verification

Before release: containerized `make test` (439 tests), ruff, ty (hand-written and generated modules),
`make check-regions`, `make check-generated` all green. After: the 0.0.18 wheel and sdist were
verified on PyPI.
