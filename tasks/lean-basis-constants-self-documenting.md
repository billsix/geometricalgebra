# Make the Lean basis-constant definitions self-documenting (named fields, not positional tuples)

**Status:** proposed — needs go-ahead (the maintainer will revisit another day). Form **decided**:
named-all-fields (see Decision).
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

The basis-constant `def`s in `G1.lean`/`G2.lean`/`G3.lean` are written as **positional**
anonymous-constructor literals (`def one : G2 := ⟨1, 0, 0, 0⟩`), so a reader must track the field
order from `structure G2` (`s, c1, c2, c12`) to see which coefficient is the `1`. Rewrite them in a
**self-documenting named-field** form. **Decision (maintainer, 2026-10-28): option (a),
named-all-fields** — `def e_1 : G2 := { s := 0, c1 := 1, c2 := 0, c12 := 0 }`, spelling out every
field, **not** the `{ zero with … }` shorthand. "Done" = every concrete positional basis constant and
the `vec`/`I_inv` constructors across G1/G2/G3 read in named-all-fields form, `make lean` green, and
`git diff` shows only those def bodies changed (a semantic-preserving edit, not a behavior change).

## Decision (2026-10-28)

**Option (a), named-all-fields, was chosen over (b) `{ zero with … }`.** The maintainer preferred the
fully-explicit form. Consequences: **no `zero` is added to G2** (option (b) would have needed one), and
G2's inline `(⟨0,0,0,0⟩ : G2)` literals are **left as-is**.

- **(a) named-all-fields** — `{ s := 0, c1 := 1, c2 := 0, c12 := 0 }`; every field spelled out.
  **← chosen.**
- **(b) `{ zero with … }`** — "zero except c1 = 1"; matches G3's existing `bivector`/`trivector`/
  `scalar` constructors but needs a `zero` constant first. **Not chosen.**

## Context (cold start)

- Raised 2026-10-28 by the maintainer while reviewing the G2 basis block during the file-structure
  sweep (`tasks/archive/2026/10/28/study-and-reorder-lean-file-structure.md`). This is a sibling of the
  object-out parity task [[lean-g2-object-out-parity]] — both are "make the contents live up to the
  comment," and both are **content** changes deliberately out of scope for the content-preserving
  reorder sweep.
- The current form (example, `proofs/GacalcProofs/G2.lean`):
  ```lean
  def one : G2 := ⟨1, 0, 0, 0⟩
  def e_1 : G2 := ⟨0, 1, 0, 0⟩
  def e_2 : G2 := ⟨0, 0, 1, 0⟩
  def e_12 : G2 := ⟨0, 0, 0, 1⟩
  def vec (x y : ℝ) : G2 := ⟨0, x, y, 0⟩
  ```
- The target form (the decided option (a), named-all-fields):
  ```lean
  def one  : G2 := { s := 1, c1 := 0, c2 := 0, c12 := 0 }
  def e_1  : G2 := { s := 0, c1 := 1, c2 := 0, c12 := 0 }
  def e_2  : G2 := { s := 0, c1 := 0, c2 := 1, c12 := 0 }
  def e_12 : G2 := { s := 0, c1 := 0, c2 := 0, c12 := 1 }
  def vec (x y : ℝ) : G2 := { s := 0, c1 := x, c2 := y, c12 := 0 }
  ```

## Scope

1. Convert the **concrete positional `def`s** to named-all-fields across **G1/G2/G3**: the basis
   constants (`one`/`e_1`/…/`e_123`), `vec`, and the positional `I_inv` (`G2.I_inv := ⟨0,0,0,-1⟩` and
   `G3.I_inv := ⟨0,…,-1⟩` → `{ s := 0, …, c12 := -1 }` / `{ s := 0, …, c123 := -1 }`).
2. **Leave alias defs** — `G2.I := e_12`, `G3.I := e_123`, `G1.I := e_1`, `G1.I_inv := e_1`. They are
   already self-documenting (a name, not a positional literal).
3. **Leave the already-non-positional parameterized constructors** — G3's `bivector`/`trivector`/
   `scalar` are `{ zero with c12 := p }`-style and read fine; do **not** expand them to all-fields
   (strictly more verbose, no readability gain).
4. **No `zero` is added to G2, and its inline `(⟨0,0,0,0⟩ : G2)` literals** (in `wedge_self_vec`,
   `wedge_isVector_isBivector_eq_zero`, and `vec_wedge_I_eq_zero` in `Projection2D.lean`) **are left
   as-is** — a bare `⟨0,0,0,0⟩` already reads as zero; this is the consequence of choosing (a) over (b).

## Risk / verification

- `{ s := 1, c1 := 0, … }` and `⟨1, 0, 0, 0⟩` both elaborate to `G2.mk 1 0 0 0` (definitionally equal),
  so proofs that `simp only [one]; ext <;> ring` should be unaffected — **but confirm with `make lean`,
  do not assume** (USE_LEAN image; runs `proofs/check.sh`).
- Lean only. The generated Python `g*.py` are untouched.
- Content change, so it is **not** part of the content-preserving reorder sweep; its own commit.

## Deliverables

- The concrete positional basis constants + `vec`/`I_inv` in G1/G2/G3 in named-all-fields form;
  `make lean` green; `git diff` limited to those def bodies (no new `zero`, inline literals untouched).

See also: [[lean-g2-object-out-parity]], `tasks/archive/2026/10/28/study-and-reorder-lean-file-structure.md`,
`tasks/reference/lean-ga-proof-architecture.md`.
