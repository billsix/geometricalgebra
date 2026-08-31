# Release gacalc 0.0.18 (cross product + blade display symbols)

**Status:** ready — agent prep done 2026-08-31; awaiting the maintainer's commit + `make release`
**Priority:** 2
**Difficulty:** 2
**Created:** 2026-08-31 (William Emerison Six <billsix@gmail.com> approved the plan)

## BLUF

Ship 0.0.18 to PyPI carrying the two features implemented 2026-08-31: the cross
product (`vectorcalc.cross`, `MultiVectorBase.cross`, generated `g3.Vector.cross` —
see `[[custom-symbols-and-vector-calc]]` and `[[generated-vector-cross]]`) and the
custom blade display symbols (`set_blade_symbols`). Done means the wheel is on PyPI
and `pip install gacalc==0.0.18` imports `gacalc.vectorcalc`. The downstream
consumer task — modelviewprojection's
`tasks/use-gacalc-cross.md` (in that repo) — is **blocked on this release**.

## Already done (staged by the agent, 2026-08-31)

- `pyproject.toml` `version` bumped `0.0.17` → `0.0.18` (v0.0.17 tag exists; PyPI
  permanently rejects a re-used version).
- `CHANGELOG.md`: `[Unreleased]` entries written for both features, and a
  retro-filled `[0.0.17] — 2026-08-23` section (that tag had shipped with no entry;
  reconstructed from `git log v0.0.16..v0.0.17` — breaking: exp-of-vector raises,
  generated `dual` dimension-locked).
- All gates green: containerized `make test` (439), `ruff`, `ty` (hand-written and
  generated modules), `make check-regions`, `make check-generated`.

## Maintainer steps (in order)

1. **[HOST]** Review + commit the staged work (`git status` staged = the handoff).
2. **[HOST]** Edit `CHANGELOG.md`: rename `## [Unreleased]` to
   `## [0.0.18] — <release date>` and open a fresh empty `[Unreleased]` above it;
   include that in the release commit.
3. **[HOST]** `make release` — builds sdist+wheel in the container with
   `GACALC_DIMS=1,2,3,4,5` (**budget ~90+ min**: g4 ~5 min, g5 ~87 min), runs the
   containerized `twine upload` (paste your PyPI token; `~/.pypirc` or
   `TWINE_PASSWORD` also work), then host-side `git tag v0.0.18`. The target
   refuses if the tag already exists.
4. After PyPI shows 0.0.18: the mvp task's gate clears — see its `Recheck:`.
