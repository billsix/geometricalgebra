# Redo the "explain Gn multiplication" explanation as markdown, in the swap/annihilate style

**Status:** complete
**Completed:** 2026-10-09
**Priority:** 4
**Difficulty:** 3
**Created:** 2026-08-16 **Updated:** 2026-10-09 (William Emerison Six <billsix@gmail.com>)

## BLUF

Wrote `tasks/reference/gn-multiplication-by-hand.md` — the general, hand-countable
slide/flip/annihilate account of the geometric product, move-by-move in ASCII with a running sign, in
the voice of `tasks/reference/pseudoscalar-square-sign.md`. It ties each move to the four `match` arms
of `gn.py`'s `decrease_grade` and leads into the pseudoscalar-sign and associativity write-ups.
Per the maintainer's decisions (2026-10-09): the write-up lives in a **reference doc** (option a), and
the existing `notebooks/displaymv.py` multiplication-rules prose is **left as-is** (the runnable intro
serves a different reader than the read-the-moves proof).

## What was done

- Created `tasks/reference/gn-multiplication-by-hand.md`: the three rules (R1 `eᵢeᵢ=+1`, R2
  `eᵢeⱼ=−eⱼeᵢ`, concatenation + distributivity), then six worked products shown move-by-move with a
  running sign — `e_2 e_1` (one swap), `e_1 e_2 e_1 = −e_2` (swap then annihilate), `(e_1 e_3)(e_3 e_1)
  = +1` (annihilate from the middle, with the three-parenthesization associativity aside),
  `(2 e_1)(3 e_3)(4 e_3)(5 e_1) = 120` (coefficients ride along), `(3 e_1 + 4 e_2)² = 25` (cross terms
  cancel by R2), `e_3 e_1 e_2 = +e_123` (put it in order) — then a table mapping each move to
  `decrease_grade`'s base / annihilate / swap+negate / in-order-insert arms, and pointers onward.
- **Every product was checked against a `Gn` REPL** before writing (the known-good set from the
  archived first-pass task): results `{(1,2):-1}`, `{(2,):-1}`, `{():+1}`, `{():120}`, `{():25}`,
  `{(1,2,3):+1}` all confirmed.
- Added a sibling backlink in `tasks/reference/pseudoscalar-square-sign.md` (the special case `I_r²`)
  pointing to the new general doc, so the "by counting" set is navigable.
- Left `notebooks/displaymv.py` unchanged (decision Q2).

## Decisions (maintainer, 2026-10-09)

- **Q1 — where:** reference doc (option a), the natural sibling of the pseudoscalar write-up.
- **Q2 — existing notebook prose:** keep it, add the markdown alongside.

## Verification

Documentation only — no source changed, so no code gate applies. The products in the doc were
verified against a live `Gn` REPL; all cited artifacts (`pseudoscalar-square-sign.md`,
`geometric-product-associativity.md`, `blade-square-sign.rst`, `displaymv.py`, `test_conformance.py`,
`test_multivector.py`, `proofs/GacalcProofs/`, `gn.py`'s `_geometric_product`/`decrease_grade`) were
confirmed to exist.

## Open questions

None.
