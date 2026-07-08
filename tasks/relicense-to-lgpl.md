# Relicense gacalc from GPL v2+ to LGPL

**Status:** proposed — needs go-ahead
**Created:** 2026-07-09

## Goal (Bill, 2026-07-09)

Change gacalc's license from GPL v2+ to the LGPL.

## Context

Raised during modelviewprojection's `ctc-vector2-deferral` work: the plan is
to back the Code-the-Classics shim's `Vector2` with `gacalc.g2.Vector2`, and
the shim (`pgzero_gl`) is LGPL-2.1 — an LGPL gacalc makes the coupling
license-clean (and friendlier for any downstream user embedding gacalc in
non-GPL code). Bill holds the copyright on all gacalc code, so relicensing
is his prerogative; no external contributors to clear (verify via
`git shortlog -sne` before executing).

## Steps

- [ ] Verify sole authorship: `git shortlog -sne` — if anyone else has
      commits, their sign-off is needed for their contributions.
- [ ] Pick the exact license: LGPL-2.1-only, LGPL-2.1-or-later, or
      LGPL-3.0 — **pgzero_gl is `LGPL-2.1-only`**, so LGPL-2.1 keeps the two
      consistent (Bill's call).
- [ ] Replace `LICENSE` (currently GPL v2) with the LGPL text.
- [ ] Update the license header in every `src/gacalc/*.py`, `tools/*.py`,
      `tests/*.py`, and the generator's emitted file header in
      `tools/gen_specialized.py` (the generated `g1/g2/g3/scalar.py` carry
      the header too — regenerate after).
- [ ] `pyproject.toml`: the `license` field / classifier ("License :: OSI
      Approved :: ...") — note CLAUDE.md also states "License: GPL v2+"
      (update it), and README if it mentions the license.
- [ ] **PyPI**: the next `make release` publishes the new metadata; already-
      published versions keep their GPL grant (fine — relicensing applies
      going forward).
- [ ] Leave the vendored Emacs elpa tree alone (third-party packages with
      their own licenses; not gacalc code).

## Gate

`grep -ri "GPL" --include="*.py" --include="*.toml" --include="*.md" .`
(excluding elpa/) shows only LGPL; `make test` green; `make dist` builds
with correct metadata.
