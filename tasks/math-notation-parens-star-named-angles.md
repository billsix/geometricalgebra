# Math notation sweep: parentheses for function application, `*` for scalar multiplication, every angle named

**Status:** proposed — needs go-ahead to run the sweep (all design questions decided 2026-10-09;
the rule text for `CLAUDE.md` is drafted below)
**Priority:** 3
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

Three notation rules the maintainer set on 2026-10-08, to be (a) written into `CLAUDE.md` as
standing conventions and (b) applied by one sweep over every place the project writes math for a
reader — book prose, ePiX figure labels, book + demo notebooks, Python docstrings (hand-written and
generated), Lean doc comments, reference docs, README:

1. **Parentheses mean function application, never multiplication.** `cos θ` → `cos(θ)`;
   `\cos\theta` → `\cos(\theta)`.
2. **Every multiplication carries an explicit `*` — scalar or not.** `r(cos(θ), sin(θ))` →
   `r * (cos(θ), sin(θ))`; `|a||b| sin θ` → `|a| * |b| * sin(θ)`; `\cos\theta\,\vec{a}` →
   `\cos(\theta) * \vec{a}`; and the geometric product of non-scalars too:
   `\vec{a}\,e_{12}` → `\vec{a} * e_{12}`, `e_1 e_2 e_1` → `e_1 * e_2 * e_1`. Juxtaposition never
   means multiplication anywhere the reader sees math. (Decided 2026-10-09: the maintainer
   extended the rule from "scalar multiplication" to all products, so the typeset math reads
   exactly like the code, where `*` *is* the geometric product — `CLAUDE.md` › Operators.)
3. **Every angle is explicitly named.** Never `sin = x/y` or `(cos = c, sin = s)`; always
   `sin(θ) = x/y`, `(cos(θ) = c, sin(θ) = s)`.

"Done" = the three bullets are in `CLAUDE.md` (book/presentation conventions section), the
discovery grep below returns zero hits (or an explained residue), figures re-render, and
`make format` + `make test` + `make docs` are green.

## Context

- **Why:** the book is read by students coming from high-school geometry/precalculus, where `cos θ`
  and `r(cos θ, sin θ)` are read as products by the unwary. In a geometric-algebra book, where a
  bare juxtaposition *is* a product (the geometric product), the ambiguity is worse than usual:
  `\cos\theta\,\vec{a}` must not look like "cos times θ times a". The explicit `*` matches the
  library's own operator (`2 * e_1`, `r * (...)`), so the typeset math and the code read the same.
- **Related conventions already in force** (read first): `CLAUDE.md` › "Presenting to students:
  prefer sine/cosine over dot/wedge" and "Coordinates only when needed";
  `tasks/reference/book-outline.md` › "Notation & prose conventions for proof pages" (θ is the
  standing angle symbol; β a vector's own standing angle). The new rules extend that section.
- **Companion sweep:** `tasks/archive/2026/10/09/coordinate-subscripts-indices-not-xyz.md` (`a_1` instead of `a_x`)
  touches the same lines; run it **after** this one, or in the same pass with its own commit.

## Current state (discovery, 2026-10-08)

Hits for "trig function applied without parentheses" (`cos θ`, `\cos\theta`, …):

| File group | Hits | Notes |
|---|---|---|
| `book/docs/*.rst` | 23 | `geometric-product.rst`, `proof-rotate.rst`, `proof-rotate-from-a-to-b.rst`, `blade-square-sign.rst` |
| `book/figures/epix/*.py` | 20 | label strings, e.g. `rotate1.py`: `r"$r\,(\cos\beta,\ \sin\beta)$"` → `r"$r * (\cos(\beta), \sin(\beta))$"` |
| `proofs/GacalcProofs/*.lean` | 35 | **doc comments only** (`/-- … cos θ … -/`). Lean *code* `Real.cos θ` is the language's application syntax — an externally-defined form, exempt |
| `src/gacalc/*.py` | 16 | docstrings in `base.py` (`cosine`, `angle`, `conjugate`, …), `measure.py`, `vectorcalc.py` |
| `notebooks/*.py` | 13 | demo notebooks |
| `tasks/reference/*.md` | 12 | |
| `tests/*.py` | 6 | comments/docstrings |
| `tools/*.py` | 4 | `gen_specialized.py` `CUSTOM_METHOD_DOCS` strings — **generator-first**: fix the table, regenerate, never the emitted `g*.py` |
| `README.md` | 1 | |

Hits for "implicit angle" (`\cos = …`, `(cos = c, sin = s)`): `book/docs/proof-projection.rst`
(4: lines near "cos = b_x/|b|" and the 3D plane rotations), `proof-rotate-from-a-to-b.rst` (2),
`book/docs/notebooks/proof-projection.py` (1 markdown line; the code `cos, sin = …` locals are
Python names, fine), Lean doc comments in `StandardPosition.lean`, `CrossStandardPosition.lean`,
`StudentTrigForms.lean` (`cos = 0 ⟺ dot = 0` — name the angle: `cos(θ) = 0`).

Juxtaposed products in docstrings/prose: ~25 `|a||b|`-style hits in `src/`/`tools/`/`book/docs`,
the `r\,\big(…\big)` lines of `proof-rotate.rst`'s derivation (lines ~123–130), **and — since
2026-10-09 — every juxtaposed geometric product**: `\vec{a}\,e_{12}` (`geometric-product.rst`),
`I_r = e_1 e_2 \cdots e_r` / `e_1 e_2 e_1` chains (`blade-square-sign.rst`; a chain becomes
`e_1 * e_2 * \cdots * e_r`), docstring forms like `A B` / `Ã B`, and the Lean doc comments'
`cos θ·1 + sin θ·e₁₂` (the `·` there is scalar multiplication → `*`). Extend `discover.sh` with a
juxtaposition grep and then **read every hit** — this part cannot be matched mechanically; it is a
read-the-page pass.

## Plan

1. **`CLAUDE.md`:** add the three rules under "Presenting to students" (or a new
   "Math notation for readers" subsection), each one line, pointing here for the sweep record. Draft:

   > - **Parentheses show function application, never multiplication** — `cos(θ)`, not `cos θ`.
   > - **Every multiplication has an explicit `*`, scalar or geometric** — `r * (cos(θ), sin(θ))`,
   >   `|a| * |b| * sin(θ)`, `a * e_12`, `e_1 * e_2`; juxtaposition never means a product.
   > - **Every angle is named** — `sin(θ) = y/r`, never `sin = y/r`.

   Also add the same three bullets to `tasks/reference/book-outline.md` › "Notation & prose
   conventions for proof pages" (the book-facing home).
2. **Discovery script** `tasks/adhoc/math-notation-parens-star-named-angles/discover.sh` (the
   greps above, one per rule), logging to `data/`. This is a read-every-hit pass, not a blind
   codemod: each hit needs a judgment (is this juxtaposition a scalar product or a geometric
   product?), so fix by hand file-by-file, bottom-up.
3. **Order:** `tools/gen_specialized.py` docstring table → `make generate` → `src/` docstrings →
   book `.rst` → figure labels (`make docs` re-renders; eyeball `_static/epix/*.png`) → notebooks →
   Lean doc comments (`make lean` still passes — comments only) → reference docs/README.
   In typeset math the symbol is a **literal `*`** in math mode (decided 2026-10-09; not `\ast`,
   not `\cdot` — the dot product — and not `\times` — the cross product).
4. **Verify:** re-run `discover.sh` = zero; `make format`, `make test`, `make docs`; spot-read the
   rendered `proof-rotate` page (the derivation with the `r * (…)` factor is the densest case).

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-09)

1. **The symbol is a literal `*`** in LaTeX math, matching the Python operator — not `st`.
2. **`*` applies to the geometric product of non-scalars too**, not only scalar multiplication:
   `ec{a} * e_{12}`, `e_1 * e_2`. No juxtaposed products remain anywhere a reader sees math.

## Open questions

None — both resolved above. Remaining gate: go-ahead to run the sweep.
