# Rename "rotor" → "versor" across gacalc (breaking API change)

**Status:** DONE 2026-09-28 (full gate green) — **archive DEFERRED at the maintainer's request**: hold
this until `lean-proof-rotation-from-scratch.md` is also done, then archive both together so the final
squash deletes the `tasks/adhoc/rename-rotor-to-versor/` codemods in ONE step (the two are semi-related
— the "a rotor is really a unit versor" insight drove both). Do NOT `git mv`/`git rm` yet.
**Priority:** 4
**Difficulty:** 7

## Execution record (2026-09-28)

Done (verified by an intermediate `make generate`/`check-generated`/`test`/`check-regions` pass = green
after the structural rename; a full gate re-run was in flight at hand-off):

- **Code identifiers** (idempotent codemods under `tasks/adhoc/rename-rotor-to-versor/`): graded type
  `Rotor` → `Versor`; `rotor_from_vectors` → `versor_from_vectors`; `rotor_rotation` →
  `versor_rotation`; `rotor_inv`/`rotor_extras`. **Kept** `_unit_bivector_rotor_factory` / `rotor_for`
  (they build a genuinely *unit* rotor).
- **Code prose** (`base.py`, `transforms.py`): general spots → versor; the `exp` block (exp of a
  bivector = unit rotor) and the `plane_rotation`/`bivector_rotation` unit-factory prose kept "rotor".
- **Generator** (`tools/gen_specialized.py`): the internal doc-role key `"rotor|…"` + `"Versor":"rotor"`
  map + emitted `Versor`-type docstrings → versor; then restored "rotor" in the statements only true for
  a unit rotor (exp result, reverse = inverse, `R R̃ = 1`, `cos(t/2)` definition, magnitude = 1). `g*.py`
  regenerated; docstrings attach; no `Rotor`/`rotor|` artifacts.
- **CHANGELOG + version**: `0.0.20 → 0.1.0` (pre-1.0 breaking); `[Unreleased]` promoted to
  `## [0.1.0] — 2026-09-28` with a BREAKING entry (so `check-changelog` matches pyproject).
- **Docs/book/tasks** (subagents + hand): book needed **no** change (all its "rotor" = the unit
  `R = cos θ + sin θ e₁₂`); task docs updated (6 files, unit cases kept); reference docs + README +
  CLAUDE.md pass finishing at hand-off.

Completed after hand-off:
- **Full gate GREEN**: `make test` (649 passed), `check-generated`, `check-regions`, `format`
  (ruff + ruff-format + ty), `check-changelog` (v0.1.0 matches) — all exit 0.
- **Tests + notebooks + `tools/bench.py`** swept (test fn names `test_rotor_*` → `test_versor_*`,
  the `symbolic-equality.md` citation updated to match; notebook prose; unit `exp`/`plane_rotation`
  spots kept). Reference docs + README + CLAUDE.md swept (subagents); `unit-bivector-and-rotors.md`
  §2 graded-type refs fixed by hand.
- **Final `git grep` sweep** done: every remaining `[Rr]otor` is an intentional *unit* mention
  (exp/`plane_rotation`/`bivector_rotation` half-angle rotor, `R R̃ = 1`, the `Rotor = exp` §3 heading,
  Dorst/Hestenes citation titles) or a historical record (CHANGELOG past-version entries, archived
  adhoc scripts) — correctly left as "rotor".
- Everything was committed by the maintainer directly (working tree clean; no agent staging needed).

**Related:** `lean-proof-rotation-from-scratch.md` (the Lean `versor` sandwich/composition proof) —
coupled for archiving (see Status).

## BLUF

gacalc's "rotor" objects are, in the strict GA sense, **un-normalized even versors** — a *rotor* is
the special case of a *unit* even versor (`R R̃ = 1`), which gacalc does not require. The maintainer
decided (2026-09-28) to rename the general object **rotor → versor** library-wide, accepting the
breaking API change + `CHANGELOG` entry + version bump ("nobody but me uses my library"). "Done" =
every occurrence swept (Python via the generator, all docs, tests, notebooks, book), `make test` /
`make check-generated` / `make lean` green, version bumped, changelog written, everything staged.

## Context — read first

- **Why:** the analysis is in `tasks/reference/unit-bivector-and-rotors.md` §6 — versor = product of
  non-null vectors; rotor = *unit* even versor; gacalc's `versor_from_vectors` builds the un-normalized
  even versor `R = |a||b| + b a` and rotates via the *inverse* sandwich `R v R⁻¹` (scale-invariant), so
  "rotor" is a misnomer for the un-normalized object. `MultiVectorBase.sandwich` is already documented
  as "versor conjugation."
- **The generated modules `src/gacalc/g1.py`/`g2.py`/`g3.py` are gitignored build artifacts** — do NOT
  hand-edit them. Rename in the **generator** `tools/gen_specialized.py` (+ `tools/astbuild.py` if it
  names anything), then `make generate` and diff. The ~821 `src/` hits are mostly generated output.

## Design decisions to confirm during execution

1. **Unit rotors genuinely exist** (the `exp` / `plane_rotation` path builds `cos(θ/2) − sin(θ/2) i`,
   which *is* unit). Proposal: rename the general type/builders to **versor** (they don't enforce
   unit-ness, so "versor" is accurate); keep the word **rotor** only in *prose* where a genuinely unit
   versor is meant, defining "rotor = unit versor" once. Confirm this split rather than a blind
   global replace.
2. **`*_rotation` names keep "rotation"** (they name the *operation*/result): `plane_rotation`,
   `projection_rotation` stay; only names containing **"rotor"** change (e.g. `versor_rotation` →
   `versor_rotation`).
3. **Lean proofs** (`proofs/GacalcProofs/Rotation.lean`) already use `versor` for the new sandwich
   material; the older `rotor θ` (one-sided full-angle operator) can be renamed for consistency or
   left — decide (low stakes, separate from the Python API).

### Identifiers to rename (from a 2026-09-28 grep of the generator + hand-src)

`Rotor` (graded type) → `Versor`; `versor_from_vectors` → `versor_from_vectors`; `versor_rotation` →
`versor_rotation`; `rotor_for` → `versor_for`; `versor_inv` → `versor_inv`; `versor_extras` →
`versor_extras`; `_unit_bivector_rotor_factory` → `_unit_bivector_versor_factory`; `rotors` →
`versors`; and prose/var `rotor` → `versor`. (Re-grep at execution time; identifiers may have shifted.)

## The sweep (the maintainer's explicit instruction: cover ALL of these)

Discover with `git grep -niE 'rotor'` per area; log matches to `tasks/adhoc/rename-rotor-to-versor/`.

- [ ] **Every Python file** — the generator `tools/gen_specialized.py` (+ `tools/astbuild.py`), the
      hand-written `src/gacalc/*.py` (`base.py`, `transforms.py`, `gn.py`, `frame.py`, `measure.py`,
      `vectorcalc.py`, …), other `tools/*.py`, `tests/*.py`, `notebooks/*.py`. Regenerate `g*.py`; do
      not hand-edit generated output.
- [ ] **Every open task** under `tasks/` (non-archive, ~219 hits) — update identifier references and
      any prose naming; leave `tasks/archive/` historically accurate (do not rewrite history).
- [ ] **Every reference doc** `tasks/reference/*.md` — especially `unit-bivector-and-rotors.md`,
      `transform-and-composable-function-layer.md`, `generated-product-typing.md`, `design-decisions.md`.
      Update the "rotor = unit versor" framing consistently.
- [ ] **`CLAUDE.md`** (~18 hits) — the Operators section, the rotor conventions, `versor_from_vectors`
      references.
- [ ] **`README.md`** (~22 hits) — quick-start / graded-subtypes sections.
- [ ] **`book/`** (~236 hits) — the Sphinx book prose + code cells (heaviest area; may warrant its own
      pass). Confirm with the maintainer whether the book renames in this same change or a follow-up.
- [ ] **`CHANGELOG.md`** — a `[Unreleased]` **Changed (BREAKING)** entry listing every renamed public
      name.
- [ ] **`pyproject.toml`** — version bump **0.0.20 → 0.1.0** (pre-1.0 breaking → bump MINOR per
      SemVer/CLAUDE.md; agent stages the bump, maintainer tags/publishes).

## Verify

- `make generate` then `make check-generated` (byte-identical determinism); `make test` (~650 tests);
  `make format` (ruff + ty + changelog guard); `make check-regions`; `make lean` (if Lean names touched).
- `git grep -niE '\brotor' src tools tests notebooks` returns only intentional "rotor = unit versor"
  prose mentions (re-grep = the completion signal).

## Resolved (maintainer, 2026-09-28)

1. **The book renames in this same pass** (`book/`, ~236 hits) — not a follow-up.
2. **Rename "rotor" → "versor" EXCEPT where the object is known unit-magnitude** — there, keep
   "rotor" (a rotor *is* a unit versor). So the classification below (unit vs general) is load-bearing:
   general/un-normalized objects and the even-grade *type* → versor; genuinely-unit constructions (the
   `exp`/`plane_rotation` `cos(θ/2) − sin(θ/2) i` rotor, the unit-bivector rotor factory) keep "rotor".
