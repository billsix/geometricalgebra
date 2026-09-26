# Docstrings: name the helper, not the bare `(−1)^(r(r−1)/2)` formula

**Status:** DONE 2026-09-26 (branch `unitPseudoscalarReferences`; maintainer merges). See Outcome.
**Priority:** 6 **Difficulty:** 3 **Created:** 2026-09-26 **Updated:** 2026-09-26
(William Emerison Six <billsix@gmail.com>)

## BLUF

Several `base.py` docstrings state the grade-`r` reversion / blade-square sign as the raw formula
`(−1)^(r(r−1)/2)`. The maintainer wants programmers to learn and use the **function that implements
it** instead — `base.pseudoscalar_squared_sign(r)` (and `pseudoscalar_squared_is_positive(r)`) — so
the docstrings should name that function instead of the bare formula. **Decided (2026-09-26): the
reference is a Sphinx `:func:` cross-reference so it renders as a clickable hyperlink in the HTML
book.** "Done" = the prose docstrings that carry the formula reference the helper via
`` :func:`~gacalc.base.pseudoscalar_squared_sign` `` (hyperlinked, resolves with 0 warnings), the
formula survives only where it is genuinely the *definition* (the helper's own docstring), all gates
stay green, and the change propagates correctly to the generated `g*` modules.

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

## Approach (DECIDED 2026-09-26)

Reference **`pseudoscalar_squared_sign(r)`** as the primary way the docstrings talk about this sign,
and render it as a **Sphinx cross-reference (a clickable hyperlink in the HTML book)**, not bare
text. The full definition + closed form + proof pointer stay in `pseudoscalar_squared_sign`'s own
docstring (the link target); a terse ` = (−1)^(r(r−1)/2)` gloss beside the reference is at the
author's discretion (keep it where the math reads better; don't duplicate the whole derivation).

**How to make it a hyperlink (Sphinx `:func:` role):**
- Write **`` :func:`~gacalc.base.pseudoscalar_squared_sign` ``** in the docstring prose. Sphinx's
  Python domain renders it as a link to that function's autodoc entry; the leading **`~`** shows
  just `pseudoscalar_squared_sign()` as the link text (drop it to show the full dotted path).
- It **resolves** because `book/docs/api.rst` already `automodule`s `gacalc.base`, so the
  module-level function `pseudoscalar_squared_sign` gets an autodoc target. (Same pattern the
  existing base docstrings use for `:class:`~gacalc.functions.ComposableFunction``.)
- Works in napoleon field prose too (inside `Returns:`/`Args:` text), so the `reverse` `Returns:`
  line can carry the link.
- **Caveat — the generated `g*` copies:** these base docstrings are copied into `g1/g2/g3/g4/g5`
  (methods without a `CUSTOM_METHOD_DOCS` entry) and those modules are **not** autodoc-rendered, so
  there the `:func:` markup shows as literal-ish text to a source reader and runs fine under
  `--doctest-modules` (no `>>>`). That is acceptable — the rendered book (base) hyperlinks; the g*
  copy is source-only. (If a plain-text look in g* is later preferred, that's a separate call.)
- **`unit_pseudoscalar_squared`'s** own docstring may also `:func:`-link `pseudoscalar_squared_sign`
  as the scalar value it equals; `pseudoscalar_squared_sign`'s docstring does not self-link.

## Verification (docstrings are Google/napoleon; g* are doctest-run)

- Regenerate + `PYTHONPATH=src pytest --doctest-modules src/gacalc/base.py src/gacalc/gn.py
  src/gacalc/g1.py g2.py g3.py`; `make test` (649) + `make check-generated` (determinism).
- `make docs` stays exit 0, **0** substitution warnings, and — the point of this task — **0**
  undefined-hyperref / ambiguous-cross-ref warnings for the new `:func:` links, AND the link
  actually renders clickable in `_build/html` (spot-check the rendered `reverse`/`exp` pages).
- `ruff check .` clean (base.py is E501-gated ≤ 88).

## Outcome (2026-09-26)

Implemented in `src/gacalc/base.py` (committed `ccd68d8`): `reverse`, `exp`, and
`unit_pseudoscalar_squared` now reference **`` :func:`~gacalc.base.pseudoscalar_squared_sign` ``**
instead of stating the bare `(−1)^(r(r−1)/2)` formula; `exp` also links
`` :func:`~gacalc.base.pseudoscalar_squared_is_positive` `` in its positive-square rejection branch.
The formula survives only in `pseudoscalar_squared_sign`'s own docstring (the link target). The
stale verbatim quote in `generated-docstrings.md` was updated to match.

**Verified:** `make docs` exit 0 — 0 substitution / undefined-hyperref / ambiguous-xref warnings,
and the roles render as **clickable hyperlinks** (7 in-page `href="#gacalc.base.pseudoscalar_squared_sign"`
in `api.html`, incl. inside the `reverse` entry; 3 for `pseudoscalar_squared_is_positive`).
`make test` / host `pytest` **649 passed**, 170 doctests pass, generator deterministic (g3
byte-identical), `ruff check .` clean. The `:func:`-hyperlink technique is harvested into
`tasks/reference/book-and-docs-pipeline.md`.

## Resolved decisions

- **Reference the helper as a hyperlinked `:func:` cross-reference** (Bill, 2026-09-26) — see
  Approach + Outcome. No open questions remained.

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
