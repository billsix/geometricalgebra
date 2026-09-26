# Docstrings: name the helper, not the bare `(−1)^(r(r−1)/2)` formula

**Status:** proposed — needs go-ahead (Bill, 2026-09-26)
**Priority:** 6 **Difficulty:** 3 **Created:** 2026-09-26 **Updated:** 2026-09-26
(William Emerison Six <billsix@gmail.com>)

## BLUF

Several `base.py` docstrings state the grade-`r` reversion / blade-square sign as the raw formula
`(−1)^(r(r−1)/2)`. The maintainer wants programmers to learn and use the **function that implements
it** instead — `base.pseudoscalar_squared_sign(r)` (and `pseudoscalar_squared_is_positive(r)`) — so
the docstrings should name that function rather than (or alongside) the bare formula. "Done" = the
prose docstrings that carry the formula cross-reference the helper by name, the formula survives only
where it is genuinely the *definition*, all gates stay green, and the change propagates correctly to
the generated `g*` modules.

## Context (cold-start)

- The implementing function is **`base.pseudoscalar_squared_sign(r) -> int`** (returns the `±1`
  sign), with **`base.pseudoscalar_squared_is_positive(r) -> bool`** built on it. Body is the closed
  form `(-1) ** ((r * (r - 1)) // 2)` (`src/gacalc/base.py`, ~line 181/214).
- **The equivalence the maintainer is remembering** (stated precisely): this sign equals the
  *r-dimensional unit pseudoscalar **squared*** — `pseudoscalar_squared_sign(r) ==
  unit_pseudoscalar_squared(r).scalar_part()` — i.e. `I_r · I_r`, **not** `I_r · Ĩ_r` (that product
  is the unit magnitude `1`). It is *also* literally the **grade-`r` reversion sign** (`Ĩ_r =
  (−1)^(r(r−1)/2) · I_r`), which is why the one helper serves both `reverse()` and `exp()`. The
  hand proof (grades 1–5, induction, the reversal one-liner) is in
  `tasks/reference/pseudoscalar-square-sign.md`; it is gated permanently by
  `tests/test_pseudoscalar_square_sign.py` (asserts `pseudoscalar_squared_sign(r) ==
  int(Gn.unit_pseudoscalar_squared(r).scalar_part())` for r = 0..N).
- History: the helpers were **named** in `tasks/archive/2026/08/15/name-blade-square-sign.md`
  (Phase 1, slow obviously-correct body) and **proven + optimized** to the closed form in
  `tasks/archive/2026/08/16/prove-blade-square-sign-equals-pseudoscalar-squared.md` (Phase 2). The
  rationale digest is `tasks/reference/design-decisions.md` (the "grade-r blade-square sign" bullet).

## Scope — the docstrings carrying the raw formula (verified 2026-09-26)

All in `src/gacalc/base.py`; line numbers are approximate (docstrings shift):

1. **`reverse` (~1160–1167)** — summary "giving the grade-r part the sign `(−1)^(r(r−1)/2)`" and the
   `Returns:` "each grade-r part signed by `(−1)^(r(r−1)/2)`". Best target: say "the grade-`r`
   reversion sign, `pseudoscalar_squared_sign(r)`". (The implementation already *calls*
   `pseudoscalar_squared_sign(r)` — the docstring should name what the code uses.)
2. **`exp` (~1774)** — "For a grade-r blade, `A² = (−1)^(r(r−1)/2) |A|²`". Could read "…
   `A² = pseudoscalar_squared_sign(r) · |A|²`" (and note the sign is decided structurally by grade —
   which is why `exp` calls `pseudoscalar_squared_is_positive(r)`).
3. **`unit_pseudoscalar_squared` (~410/418)** — "the scalar `(−1)^(n(n−1)/2)`". This method *is* the
   quantity; naming `pseudoscalar_squared_sign(n)` as its scalar value ties the two together.

**Keep the formula (do NOT delname):**
- **`pseudoscalar_squared_sign` itself (~181–214)** — this is the *definition site*; the closed
  form belongs here, with the proof pointer already present.
- The **reference docs** (`pseudoscalar-square-sign.md`, `unit-bivector-and-rotors.md`,
  `design-decisions.md`) — they explain the math; they already cite the helper. Leave.

## Propagation to the generated modules (must not break)

- `base.py` docstrings are **copied** into generated `g*` methods that lack a `CUSTOM_METHOD_DOCS`
  entry (via `inspect.getdoc`), so editing base's `reverse`/`exp`/`unit_pseudoscalar_squared`
  docstrings flows to the generic copies (g4/g5, and any role without a custom entry).
- The **grade-specialized `reverse` entries** in `tools/gen_specialized.py` (`scalar|reverse`,
  `vector|reverse`, …) already use the *concrete* per-grade sign ("+1"/"−1"), not the formula, so
  they need no change — but consider whether the `*`/`full`-role generic wording should also name
  the helper for consistency.
- The generator **bakes the sign as a compile-time constant** into each generated `reverse()` via
  `pseudoscalar_squared_sign(len(b))` (it does not call the helper at runtime) — a docs-only change
  here does not touch that.

## Approach / open question

The one real decision: **replace** the formula with the function name, or **name the function AND
keep the formula** (e.g. "the reversion sign `pseudoscalar_squared_sign(r)` = `(−1)^(r(r−1)/2)`")?
Naming-only best serves "programmers use the function"; keeping both preserves the math for a reader
skimming the docstring without chasing the helper. Recommendation: **name the helper first, keep a
terse ` = (−1)^(r(r−1)/2)` gloss** in `reverse`/`exp` (one place each), and let
`pseudoscalar_squared_sign`'s own docstring carry the full definition + proof pointer.

## Verification (docstrings are Google/napoleon; g* are doctest-run)

- Regenerate + `PYTHONPATH=src pytest --doctest-modules src/gacalc/base.py src/gacalc/gn.py
  src/gacalc/g1.py g2.py g3.py`; `make test` (649) + `make check-generated` (determinism).
- `make docs` stays exit 0 / 0 substitution warnings (naming a Python function in prose adds no RST
  substitution; write `:func:`~gacalc.base.pseudoscalar_squared_sign`` if a rendered cross-ref is
  wanted, but confirm it resolves — `base` is autodoc'd in `api.rst`).
- `ruff check .` clean (base.py is E501-gated ≤ 88).

## Open questions

1. Replace the `(−1)^(r(r−1)/2)` formula with the helper name, or keep both (name + terse formula
   gloss)? (Recommendation above: name first, keep a one-place gloss.)

## See also

- `tasks/reference/pseudoscalar-square-sign.md` — the proof that `I_r² = (−1)^(r(r−1)/2)` and that it
  is the reversion sign; the "where this lives in code" section names the helper.
- `tasks/reference/design-decisions.md` — the "grade-r blade-square sign" bullet (naming + the
  make-it-correct-then-fast history).
- `tasks/reference/generated-docstrings.md` — how base docstrings are copied into `g*`; the
  Google-format convention these edits must follow.
- `tasks/archive/2026/08/15/name-blade-square-sign.md`,
  `tasks/archive/2026/08/16/prove-blade-square-sign-equals-pseudoscalar-squared.md` — the naming +
  proof work records.
- `tests/test_pseudoscalar_square_sign.py` — the permanent gate on the equivalence.
