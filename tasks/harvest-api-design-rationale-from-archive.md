# Harvest archived API/design rationale into the live docs

**Status:** proposed — needs go-ahead
**Priority:** 5
**Difficulty:** 3
**Created:** 2026-08-13
**Origin:** the 2026-08-13 archive gap-analysis sweep (Group B — medium-confidence
design/API rationale, mostly rejected-alternatives). Siblings: the other `harvest-*`
tasks + `blade-dict-interchange-reference.md`.

**Verify each item against current source before writing** — durable, but a couple carry
"confirm it still holds" caveats. Target is mostly `design-decisions.md` (the "why, and
where settled" harvest), with two CLAUDE.md architecture notes.

## Items

- [ ] **`to_matrix` two backends + convention.** `backend="numpy"` (float32, default, for
      GL) vs `"sympy"` (exact/symbolic); column-vector / premultiply convention with the
      translation in the **last column**, matching mvp's `pyMatrixStack` (a cross-repo
      contract); `Gn` needs an explicit `n` (specialized classes read `DIMENSION`).
      *Source:* archive `2026/06/08/invertiblefunction-to-matrix.md`,
      `2026/06/12/to-matrix-build-by-columns.md`. *Home:* design-decisions `to_matrix` entry.
- [ ] **`x`/`y`/`z` coordinate properties are grade-1-only** (Vector1/2/3), deliberately
      not on rotors/bivectors/full types ("a vector's coordinates ARE its coefficients").
      *Source:* `2026/07/09/upgrade-rotation-and-ctc-vector-mapping.md`. *Home:* CLAUDE.md
      Architecture (near the frozen/coordinate-property note).
- [ ] **Declined vector-API additions + rationale:** no `cross` (it's `(a∧b).dual()`,
      zero call sites), no `__getitem__`/`__len__` (`__iter__` already yields blade-order
      coefficients), no zero-safe `normalize` (a zero vector *should* raise, matching
      pygame; the old shim's `(0,0)` was over-defensive). *Source:*
      `2026/07/09/upgrade-rotation-and-ctc-vector-mapping.md`. *Home:* design-decisions
      (API › rejected alternatives).
- [ ] **`InvertibleFunction.__matmul__` overloads preserve invertibility in the type**
      (invertible @ invertible → invertible; @ composable → composable), and the
      generic-TypeVar-bound alternative was **tried and rejected** — ty rejects a generic
      bound (`invalid-type-variable-bound`), and bounding by the bare base is unsound for
      subclasses (`Rotation @ Rotation` would falsely type as `Rotation`, while `compose`
      only ever returns a plain `InvertibleFunction`). *Source:*
      `2026/07/18/release-0-0-10-and-bump-mvp.md`. *Home:* design-decisions
      (composable-function hierarchy).
- [ ] **Rotation "why normalize from/to"** — un-normalized rotate "works" only in 2D; in
      3D it scales the in-plane component by `|from||to|` and leaves the perpendicular
      component unscaled (a non-uniform distortion no single rotor sandwich reproduces).
      Plus the rotor-sandwich scaling three-way distinction: recover the pure rotation by
      dividing by the *scalar* `R R̃` (= `magnitude_squared`); dividing by the *sandwich's
      own* `magnitude_squared` gives the geometric inverse; normalizing `R` needs
      `sqrt(R R̃)`, a nested radical sympy chokes on. *Source:*
      `2026/06/06/graded-blade-subtypes.md`. *Home:* design-decisions (near derived-sandwich).
- [ ] **Animation-layer semantics** — the `at(t)` three-tier resolution (own `interpolate`
      law → recurse through `components` → else step at t≥1), that `compose` must store
      `components` for `at`/`steps` to recurse, the per-factory interpolation laws
      (`translate(b)` → `translate(b·t)`, `uniform_scale(m)` → linear 1→m), and the
      invariant **`inverse(f).at(t) == inverse(f.at(t))` at every t** (what lets an
      against-the-arrow edge animate smoothly rather than snap). **Verify against the
      2026-07-17 composable-function reassessment first.** *Source:*
      `2026/06/08/port-animation-layer-from-mvp.md`. *Home:* design-decisions
      (API › composable-function), or promote `composable-function-followups` to reference.
