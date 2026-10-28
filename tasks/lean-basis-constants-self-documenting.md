# Make the Lean basis-constant definitions self-documenting (named fields, not positional tuples)

**Status:** proposed — needs go-ahead (the maintainer will revisit another day)
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

The basis-constant `def`s in `G1.lean`/`G2.lean`/`G3.lean` are written as **positional**
anonymous-constructor literals (`def one : G2 := ⟨1, 0, 0, 0⟩`), so a reader must track the field
order from `structure G2` (`s, c1, c2, c12`) to see which coefficient is the `1`. Rewrite them in a
**self-documenting** form that mirrors the docstring — the preferred shape is `{ zero with … }`
(`def e_1 : G2 := { zero with c1 := 1 }`), which is **already the house pattern in G3** for
`bivector`/`trivector`/`scalar`. "Done" = every basis constant and `vec`/`bivector`-style
constructor across G1/G2/G3 reads in named-field form, `make lean` green, and `git diff` shows only
those def bodies changed (a semantic-preserving edit, not a behavior change).

## Context (cold start)

- Raised 2026-10-28 by the maintainer while reviewing the G2 basis block during the file-structure
  sweep (`tasks/study-and-reorder-lean-file-structure.md`). This is a sibling of the object-out
  parity task [[lean-g2-object-out-parity]] — both are "make the contents live up to the comment,"
  and both are **content** changes deliberately out of scope for the content-preserving reorder sweep.
- The current form (example, `proofs/GacalcProofs/G2.lean`):
  ```lean
  def one : G2 := ⟨1, 0, 0, 0⟩
  def e_1 : G2 := ⟨0, 1, 0, 0⟩
  def e_2 : G2 := ⟨0, 0, 1, 0⟩
  def e_12 : G2 := ⟨0, 0, 0, 1⟩
  def vec (x y : ℝ) : G2 := ⟨0, x, y, 0⟩
  ```
- The target form (option b below), matching G3's existing `bivector`/`trivector`/`scalar`:
  ```lean
  def zero : G2 := ⟨0, 0, 0, 0⟩          -- NEW: G2 has no `zero` today (G1/G3 do)
  def one  : G2 := { zero with s := 1 }
  def e_1  : G2 := { zero with c1 := 1 }
  def e_2  : G2 := { zero with c2 := 1 }
  def e_12 : G2 := { zero with c12 := 1 }
  def vec (x y : ℝ) : G2 := { zero with c1 := x, c2 := y }
  ```

## Options

- **(a) named-all-fields** — `def e_1 : G2 := { s := 0, c1 := 1, c2 := 0, c12 := 0 }`. Explicit but
  verbose (you still write every field).
- **(b) `{ zero with … }`** (recommended) — shows "zero except c1 = 1"; matches G3's existing
  grade constructors. Requires a `zero` constant to exist first.

## Scope / sub-tasks

1. **G2 has no `zero` constant** — it spells it inline as `(⟨0,0,0,0⟩ : G2)` in several wedge
   lemmas (e.g. `wedge_self_vec`, `wedge_isVector_isBivector_eq_zero`, `vec_wedge_I_eq_zero` in
   `Projection2D.lean`). Adding `def zero : G2 := ⟨0,0,0,0⟩` enables option (b) **and** lets those
   inline literals become the named `zero` (a second readability win + G1/G3 parity). Decide whether
   to also fold those inline literals (recommended: yes).
2. Convert the basis constants + `vec` in **G2** to option (b).
3. Do the same in **G1** (`one`/`e_1`/`vec`/`I`/`I_inv`/`zero` — `zero` already exists) and **G3**
   (`one`/`e_1`…`e_123`/`vec`/`I` — `zero` already exists; `bivector`/`trivector`/`scalar` are
   already in `{ zero with … }` form).

## Risk / verification

- `{ s := 1, … }`, `{ zero with s := 1 }`, and `⟨1, 0, 0, 0⟩` all elaborate to `G2.mk 1 0 0 0`
  (definitionally equal), so proofs that `simp only [one]; ext <;> ring` should be unaffected —
  **but confirm with `make lean`, do not assume** (USE_LEAN image; runs `proofs/check.sh`).
- Lean only. The generated Python `g*.py` are untouched.
- Content change, so it is **not** part of the content-preserving reorder sweep; its own commit.

## Deliverables

- Basis constants + constructors in G1/G2/G3 in named-field form; `make lean` green; `git diff`
  limited to those def bodies (plus the new G2 `zero` and any folded inline literals).

See also: [[lean-g2-object-out-parity]], `tasks/study-and-reorder-lean-file-structure.md`,
`tasks/reference/lean-ga-proof-architecture.md`.
