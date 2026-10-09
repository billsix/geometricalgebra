# Math notation sweep: parentheses for function application, `*` for scalar multiplication, every angle named

**Status:** DONE 2026-10-09 (work committed by the maintainer as pre-squash quick-saves — the "added parenthesis and use * for
multiplication" and "tigthen mult without spaces" commits, which collapse into one at squash); the
archive move plus `git rm -r tasks/adhoc/math-notation-parens-star-named-angles/` are owed as their
own commit after the squash.
**Priority:** 3
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

Three notation rules the maintainer set on 2026-10-08 and sharpened on 2026-10-09 — parentheses
show function application (`cos(θ)`, never `cos θ`); every multiplication, scalar or geometric,
carries a literal `*` (`r * (cos(θ), sin(θ))`, `\vec{a} * e_{12}`, `e_1 * e_2`; in Lean comments
without surrounding spaces, `|a|*|b|`); every angle is named (`sin(θ) = y/r`, never `sin = y/r`) —
were written into `CLAUDE.md` and the book outline as standing conventions and applied by one sweep
over every place the project writes math for a reader: book prose and figure labels, book and demo
notebooks, Python docstrings (hand-written and the generator's table), tests, Lean doc comments,
reference docs, README. The maintainer's review of the first result caught two inner products
turned into `*`; the codemod was fixed at the root and the whole span re-audited. `make format`'s
steps, `make test`, `make lean` and `make docs` passed on the result.

## Context (still true of the repo)

- **The rules, their rationale and their exemptions** are `CLAUDE.md` › "Math notation for
  readers" (the book-facing bullet is `tasks/reference/book-outline.md` › "Notation & prose
  conventions for proof pages"). Why: a reader from precalculus reads `cos θ` and `r(cos θ, sin θ)`
  as products, and in a geometric-algebra book a bare juxtaposition *is* a product, so the typeset
  math must read exactly like the code, where `*` is the geometric product. Exempt: Lean *code*
  (`Real.cos θ` is the language's application syntax), Python code, doctest lines.
- **Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-09):** the symbol is a literal `*`
  in LaTeX math (not `\ast`, not `\cdot`, which is the dot product, not `\times`, the cross
  product); `*` marks the geometric product of non-scalars too (`\vec{a} * e_{12}`), not only
  scalar multiplication; and in Lean doc comments the star carries no surrounding spaces
  (`a₁*b₂ − a₂*b₁`), because the spaced form `a₁ * b₂-a₂ * b₁` reads as if the minus bound tighter.
- **The dot is never a multiplication to mark.** `a·b`, `u·v`, `(v·d / d·d)`, and the Hestenes
  plane projection `(c·B)B⁻¹` are inner products and keep the middle dot; `R * a = |a| * h`,
  `R = b * a + |a| * |b|`, `to * from` are `mul` in the Lean statements they describe (the versor is
  the geometric product `b a` plus `|a||b|`), so they take the star. The `∗` scalar-product symbol
  in `base.py` (`Ã ∗ B`) is a third thing and is untouched.
- **A doc that quotes a rejected spelling on purpose** (the rule paragraphs themselves) fences the
  span with `<!-- notation-rule: begin -->` / `<!-- notation-rule: end -->`, which a re-sweep
  skips; `CLAUDE.md` states this beside the rules.
- **Where juxtaposition deliberately survives:** Lean code quoted in doc comments (`rot θ v`,
  `smul k v`); the relative-graph-paper page's quotation of the reader's prior `a i + b j` and the
  demo notebook's "you already know how to multiply `(x + 2)(x + 3)`" (quotations, kept verbatim);
  `blade-square-sign.rst`'s sliding diagrams, whose columns a `*` would misalign — the page says so
  in one sentence before the first of them; and a few proof-technique chains in
  `lean-ga-proof-architecture.md`'s tactic notes (`R u (R̃ R) v R̃`), written as the reader of that
  doc writes Lean.

## Chronology (2026-10-08 → 10-09)

1. **Filed** 2026-10-08 with the three rules, a per-file-group hit table (23 book, 20 figure,
   35 Lean-doc, 16 `src/`, 13 demo-notebook, 12 reference-doc, 6 test, 4 generator, 1 README hits
   for rule 1; a handful for rule 3; ~25 `|a||b|`-style juxtapositions), and the plan: rules into
   `CLAUDE.md`, a discovery script, a read-every-hit fix in generator → `src/` → book → figures →
   notebooks → Lean docs → reference docs order, then the gates.
2. **Decisions** 2026-10-09: literal `*`; `*` for all products. (The filed text of those two had
   lost its backslashes to control characters — `\ast` had become a BEL byte plus "st" — repaired.)
3. **Go-ahead** 2026-10-09; the sweep.
4. **The maintainer's review** of the first result: "it looks to me like you replaced some inner
   product stuff with `*`, especially when it comes to the lean, and descriptions." Confirmed on two
   lines; corrected, re-audited (below). Both the sweep and its corrections are the
   "added parenthesis and use * for multiplication" quick-save.
5. **"No space in the multiplication in the lean comments"** — the maintainer's spacing decision,
   applied as the "tigthen mult without spaces" quick-save.

## What was done

**The rules.** `CLAUDE.md` gained the section "Math notation for readers: parentheses apply, `*`
multiplies, every angle is named"; the outline gained its bullet. Both quote the rejected
spellings, hence the markers.

**Discovery.** `tasks/adhoc/math-notation-parens-star-named-angles/discover.sh`, one grep per
rule over every reader-facing group; `data/hits-before.txt` held 1079 lines (rule 1: 183,
rule 3: 40, rule 2 candidates: 856 — a list to read, not a to-do list, because the middle dot is
usually the dot product). The counts exceeded the filed table because the two tasks archived
earlier that day (typed notebooks; indexed subscripts) had added pages and notebooks in the old
spelling. `proofs/README.md` was missing from the file list and was swept by hand later.

**The codemod** `fix.py` did the mechanical part, on prose regions only: Python comment and
string tokens (doctest lines skipped), Lean comment spans, whole `.rst`/`.md` files minus the
fenced spans and `blade-square-sign.rst`. It took three versions before the first result, each
after a full read of the diff and a revert-by-path of the processed files before the final run
(second run = 0 changes): v1 rewrote the rule text itself ("not `cos(θ)`") and swallowed the brace
after a subscript inside `\frac`; v2 turned the prose cross-reference `sin (§3)` into `sin(§3)` and
half-converted `|a|^2|b|^2` and `2|a||b|(…)`; v3 restricted the trig-parenthesis lookahead to
angles and magnitudes, required a complete magnitude after a digit, stopped treating `e_3 (use the
…` and `grade-3 (e_123)` as products, and handled the combining-mark hats (`B̂`) that `\b` cannot
see. Its middle-dot rule converts a dot only when the LEFT operand is a scalar (a magnitude, a
trig value, a digit, `θ`, a coefficient `c1`/`c12`, a parenthesised ratio); a dot between two
vectors is left alone.

**The hand edits** (plain edits of named lines; the script that made them was session scratch,
not kept): the site-specific angle names — `proof-projection.rst` (`\cos(-\theta) = b_1/|b|` for
the 2D alignment; the two 3D plane swings now say "by an angle `\theta_1`/`\theta_2`"),
`proof-rotate-from-a-to-b.rst` (`\cos(-\beta)` for step 1, `\cos(\theta)` for step 2), two notebook
comments, `Trig.lean`/`TrigEquiv.lean`; `blade-square-sign.rst` in full (`e_1 * e_2 * e_3`,
`I_r = e_1 * e_2 * \cdots * e_r`, `(a * e_1) * (b * e_2) * (c * e_1)`, `r * (r-1)/2`, plus the
diagram sentence); the product's own docstrings (`__mul__` no longer says "A B (juxtaposition)";
`⟨A * B⟩`, `Ã * A`, `A * I⁻¹`, the bisector derivation `h * a = (|b| * a + |a| * b) * a`); the
demo notebooks' `R * v * R^{-1}` and `(2 * e_1) * (3 * e_3) * …`; one false positive reverted (a
test comment's parenthetical "(1 + e_1 is in fact a zero divisor)"). Then 35 comment and docstring
lines the stars pushed past 88 columns were reflowed paragraph-wise.

**The review and its corrections.** A script paired every removed middle dot in the first
result with its replacement (719 lines read), then a second pass over the whole
`origin/master..tree` span classified every removed dot by its left operand (258 scalar-left
removals counted; the 81 other hunks read in full). Found and fixed:

- **Two genuine inner products wrongly converted**, both in `Projection3D.lean`: the Hestenes
  projection onto a plane, `(c·B)B⁻¹` and `(c·(a∧b))(a∧b)⁻¹`, had become `(c * B)` and
  `(c * (a∧b))` — the codemod's scalar list had treated any lone `c` or `s` as a coefficient, and
  `c` is a vector there. Both reverted, and the lone `c`/`s` rule removed from the codemod (which
  had re-converted the reverted lines on its next run until it was). Every other removed dot was
  a scalar times something or a juxtaposed geometric product; the genuine dot products were kept,
  and the `∗` scalar-product symbol was untouched.
- **The versor identities had been left mixed:** `R = b·a + |a| * |b|`, `R·a = |a| * h`,
  `b · R = |b| * h`, `h·a = |a| * R`, `to·from`, `t·f + …`, `uvec β · uvec α`, `(a·b)·1`. In those
  the dot is the *geometric* product — checked against the Lean statements (`versorFromVectors =
  mul to from + smul (|from| * |to|) one`, `mul R a = smul |a| h`, `mul_eq_proj_dot_add_reject_wedge:
  mul a b = smul (dot b a) one + wedge a b`) and the Python bodies (`versor_from_vectors` returns the
  geometric product plus the scalar; `dual` returns `self * I.inverse()`) — and beside a `*` it read
  as a dot product. All converted (36 sites across the `Rotation3D`, `Versor2D`, `Rotor`, `Sandwich`,
  `G3`, `StandardPosition`, `ProjectionRotation2D/3D` doc comments, three reference docs, the graded
  demo notebook and `proofs/README.md`).
- **Half-converted stragglers finished:** a matrix product `g⁻¹ * Mᵀ * g` (galgebra comparison),
  `a * e`, `b * e`, `c * e` (a test docstring), `(2c² − 1) * e₁ + 2sc * e₂`, `|R|⁴ * (u · v)`, the
  subscripted coefficients `c₁₂ * e₁₂` (not in the codemod's list), `e_r * e_r` in the
  pseudoscalar-sign doc, `(−1)^(…) * |A|²` in `base.py`; and one that mattered beyond notation —
  `nR/|f||t|` had become `nR/|f| * |t|`, a different expression, now `nR/(|f| * |t|)`.

**The spacing pass** (the "tigthen mult without spaces" quick-save). A tightening step in the codemod's Lean-comment handler removes
the spaces around the star inside comment spans (a star at the start of a comment line is a
markdown bullet and is left alone): 28 files; proven comment-only by stripping comment spans from
HEAD's and the tree's version of every changed file and asserting the code identical. The maintainer
then asked whether the no-space rule should extend to LaTeX prose or Python comments — **no, for
both** (recorded in the `CLAUDE.md` rule): LaTeX math is *rendered*, so source spacing is ignored
and `*`/`−` get equal operator spacing no matter how typed (the misleading artifact cannot appear
in what the reader sees); and Python docstring math doubles as copyable code, where `2 * e_1` is
correct PEP 8 and `2*e_1` would read as bad Python. A targeted grep confirmed no asymmetric
`a * b-c * d` instance remains in either — the one real Python case (`a_1 * b_2-a_2 * b_1`) was
already equalized to spaced-both during the reflow.

**Gates.** Locally `ruff check .` and `ruff format --check .` clean, `ty check` over `src`, `tests`,
`tools`, `book/docs/notebooks` clean, `tools/check_epix_keywords.py` clean, `pytest` 696 passed
with doctests (after removing two stale gitignored `src/gacalc/g4.py`/`g5.py` from an older
generator, which the current `base.py` cannot import and the container never has). `make lean`
(`make -o image lean`) ran after each pass — sweep, corrections, spacing: `[lean] OK` each time, the
10 warnings the pre-existing ones in `ProjectionRotation3D.lean`. `make docs` (`make -o image docs`):
exit 0, every notebook executed; the proof-rotate derivation page and its figures read with the new
notation in the PDF. The discovery grep afterwards flags, for rules 1 and 3, only the fenced rule
text, Lean code and the prose "cos/sin (§3)"; rule 2's residue is the deliberate list in Context
(`data/hits-after.txt`).

**Not changed.** The public API and the generated modules (the generator's docstring table was
edited; the emitted `g*.py` regenerate). No `CHANGELOG` entry: docstring wording, nothing a
consumer pins. The subscript sweep (archived 2026-10-09) had already run; this one ran on top of it.

## Open questions

None.
