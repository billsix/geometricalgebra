# Rename "rotor" → "versor" across gacalc (breaking API change)

**Status:** DONE 2026-09-28 (full gate green; released as `0.1.0`), archived 2026-10-04 together with
`lean-proof-rotation-from-scratch.md` at the maintainer's request (the two share the "a rotor is really a
unit versor" thread). **Priority:** 4. **Difficulty:** 7.
**Durable record:** `tasks/reference/unit-bivector-and-rotors.md` §6 (the analysis), `CHANGELOG.md`
`[0.1.0]` (the BREAKING entry listing every renamed public name).

## BLUF

gacalc's "rotor" objects are un-normalized even versors; a rotor is the unit special case (`R R̃ = 1`),
which gacalc does not require. The maintainer renamed the general object rotor → versor library-wide,
accepting the breaking change ("nobody but me uses my library"), with the rule: **rename except where the
object is known unit-magnitude** — there "rotor" stays (the `exp`/`plane_rotation` half-angle rotor
`cos(θ/2) − sin(θ/2) i`, the unit-bivector rotor factory, `R R̃ = 1`).

## What was done (2026-09-28)

- Code identifiers via idempotent codemods (one-shot, deleted at archive): graded type `Rotor` → `Versor`;
  `rotor_from_vectors` → `versor_from_vectors`; `rotor_rotation` → `versor_rotation`; `rotor_inv`/
  `rotor_extras` → `versor_*`. Kept `_unit_bivector_rotor_factory`/`rotor_for` (genuinely unit).
- The generator's doc-role keys and emitted docstrings renamed, with "rotor" restored only in the
  statements true for a unit rotor; `g*.py` regenerated.
- `pyproject.toml` `0.0.20 → 0.1.0`; `[Unreleased]` promoted to `[0.1.0] — 2026-09-28` with the BREAKING
  entry.
- The book needed no change (all its "rotor" are the unit `R = cos θ + sin θ e₁₂`); task docs, reference
  docs, README, CLAUDE.md, tests (`test_rotor_*` → `test_versor_*`), notebooks and `tools/bench.py` swept.
- Verification: `make test` (649 passed), `check-generated`, `check-regions`, `format`, `check-changelog`
  all green; a final `git grep -niE rotor` showed only intentional unit mentions and historical records.
  The maintainer committed directly.

## Decisions

- `*_rotation` names keep "rotation" (they name the operation); only names containing "rotor" changed.
- The Lean `Rotation2D.rotor θ` (the one-sided full-angle operator) was left as is — a unit object, so the
  word is correct there.
