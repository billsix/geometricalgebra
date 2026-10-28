# Make the Lean basis-constant definitions self-documenting (named fields, not positional tuples)

**Status:** done — 2026-10-28. `make lean` green (8958 jobs; completeness gate OK). 21 positional
basis-constant defs across G1/G2/G3 converted to named-all-fields; aliases and parameterized
constructors left as-is.
**Priority:** 7
**Difficulty:** 3
**Created:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)
**Updated:** 2026-10-28 (William Emerison Six <billsix@gmail.com>)

## BLUF

The basis-constant `def`s in `G1.lean`/`G2.lean`/`G3.lean` were **positional** anonymous-constructor
literals (`def one : G2 := ⟨1, 0, 0, 0⟩`), forcing a reader to track the field order from the
`structure` to see which coefficient is the `1`. Rewrote them in self-documenting **named-all-fields**
form (`def e_1 : G2 := { s := 0, c1 := 1, c2 := 0, c12 := 0 }`). Definitionally equal to the old
literals, so every proof passed unchanged — verified by `make lean`; `git diff` was the converted
`def` lines only (no proof body touched).

## Decision (2026-10-28)

**Option (a), named-all-fields, over (b) `{ zero with … }`** — the maintainer preferred the
fully-explicit form. Consequences: **no `zero` was added to G2** (option (b) would have needed one),
and G2's inline `(⟨0,0,0,0⟩ : G2)` literals were **left as-is**.

## What was done

**21 concrete positional `def`s converted** to named-all-fields (`{ s := …, c1 := …, … }` in each
file's field order — G1 `s,c1`; G2 `s,c1,c2,c12`; G3 `s,c1,c2,c3,c12,c13,c23,c123`):

- **G1 (4):** `zero`, `one`, `e_1`, `vec`.
- **G2 (6):** `one`, `e_1`, `e_2`, `e_12`, `vec`, `I_inv`.
- **G3 (11):** `zero`, `one`, `e_1`, `e_2`, `e_3`, `e_12`, `e_13`, `e_23`, `e_123`, `vec`, `I_inv`.

**Left unchanged, by design:**

- **Alias defs** — `G2.I := e_12`, `G3.I := e_123`, `G1.I := e_1`, `G1.I_inv := e_1` — already a name,
  not a positional literal.
- **Parameterized `{ zero with … }` constructors** — G3's `bivector`/`trivector`/`scalar` — already
  self-documenting; expanding them to all-fields would be strictly more verbose.
- **G2's inline `(⟨0,0,0,0⟩ : G2)` zero literals** in its wedge lemmas — a bare `⟨0,0,0,0⟩` already
  reads as zero, and (a) adds no `zero` to fold them into.

The conversion was a one-off positional→named transform targeting exactly the named defs (it skipped
aliases, operations, and `{ zero with … }` naturally, since those are not `:= ⟨…⟩` basis constants);
not kept as a script (it only reproduces a mechanical file edit).

## Files touched

- `proofs/GacalcProofs/G1.lean`, `proofs/GacalcProofs/G2.lean`, `proofs/GacalcProofs/G3.lean` — the
  converted basis-constant / `vec` / `I_inv` defs. Diff = those def lines only.

See also: [[lean-g2-object-out-parity]], `tasks/archive/2026/10/28/study-and-reorder-lean-file-structure.md`,
`tasks/reference/lean-ga-proof-architecture.md`.
