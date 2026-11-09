# Docstrings: name the helper, not the bare `(−1)^(r(r−1)/2)` formula

**Created:** 2026-09-26 · **Completed:** 2026-09-26 (branch `unitPseudoscalarReferences`, work commit
`3a98012`, merged in `1fc63a3`; William Emerison Six <billsix@gmail.com>)

## Goal

Several `base.py` docstrings stated the grade-`r` reversion / blade-square sign as the raw formula
`(−1)^(r(r−1)/2)`. The maintainer wanted programmers to learn and use the function that implements it,
`base.pseudoscalar_squared_sign(r) -> int` (and `pseudoscalar_squared_is_positive(r) -> bool`, built
on it; body `(-1) ** ((r * (r - 1)) // 2)`).

The equivalence, stated precisely: this sign equals the r-dimensional unit pseudoscalar **squared**,
`pseudoscalar_squared_sign(r) == unit_pseudoscalar_squared(r).scalar_part()` — `I_r * I_r`, not
`I_r * Ĩ_r` (that is the magnitude `1`). It is also literally the grade-`r` reversion sign
(`Ĩ_r = (−1)^(r(r−1)/2) * I_r`), which is why one helper serves both `reverse()` and `exp()`. The hand
proof is in `tasks/reference/pseudoscalar-square-sign.md` and the equivalence is gated permanently by
`tests/test_pseudoscalar_square_sign.py`. The helpers were named in
`tasks/archive/2026/08/15/name-blade-square-sign.md` and proven + optimized to the closed form in
`tasks/archive/2026/08/16/prove-blade-square-sign-equals-pseudoscalar-squared.md`.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-09-26)

- **The reference is a Sphinx `:func:` cross-reference**, `` :func:`~gacalc.base.pseudoscalar_squared_sign` ``,
  so it renders as a clickable link in the HTML book (the `~` shows just the function name). It
  resolves because `book/docs/api.rst` already `automodule`s `gacalc.base`, and it works inside
  napoleon field prose.
- **The formula stays only at its definition site**, `pseudoscalar_squared_sign`'s own docstring (the
  link target, which does not self-link), and in the reference docs that explain the math
  (`pseudoscalar-square-sign.md`, `unit-bivector-and-rotors.md`, `design-decisions.md`).
- **Generated `g*` copies accepted as-is:** base docstrings are copied into generated methods lacking
  a `CUSTOM_METHOD_DOCS` entry, and those modules are not autodoc-rendered, so there the `:func:`
  markup is source-only text (harmless under `--doctest-modules`). The grade-specialized `reverse`
  entries already use the concrete per-grade sign, and the generator bakes the sign as a constant via
  `pseudoscalar_squared_sign(len(b))`, so a docs-only change touched neither.

## What changed

In `src/gacalc/base.py`, `reverse`, `exp` and `unit_pseudoscalar_squared` reference
`` :func:`~gacalc.base.pseudoscalar_squared_sign` `` instead of the bare formula; `exp` also links
`` :func:`~gacalc.base.pseudoscalar_squared_is_positive` `` in its positive-square rejection branch.
The stale verbatim quote in `tasks/reference/generated-docstrings.md` was updated, and the `:func:`
technique was harvested into `tasks/reference/book-and-docs-pipeline.md`.

## Verification

`make docs` exit 0 with 0 substitution / undefined-hyperref / ambiguous-xref warnings, and the roles
render as clickable links (7 in-page `href="#gacalc.base.pseudoscalar_squared_sign"` in `api.html`,
including inside the `reverse` entry; 3 for `pseudoscalar_squared_is_positive`). `make test` / host
`pytest` 649 passed, 170 doctests pass, the generator deterministic (g3 byte-identical), `ruff check .`
clean.
