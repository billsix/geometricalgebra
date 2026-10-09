# Math notation sweep: parentheses for function application, `*` for scalar multiplication, every angle named

**Status:** DONE 2026-10-09 (work committed by the maintainer as `9a699d6`); the archive move plus
`git rm -r tasks/adhoc/math-notation-parens-star-named-angles/` are owed as their own commit after
the squash.
**Priority:** 3
**Difficulty:** 4
**Created:** 2026-10-08 (William Emerison Six <billsix@gmail.com>)

## BLUF

Three notation rules the maintainer set on 2026-10-08 and sharpened on 2026-10-09 — parentheses
show function application (`cos(θ)`, never `cos θ`); every multiplication, scalar or geometric,
carries a literal `*` (`r * (cos(θ), sin(θ))`, `\vec{a} * e_{12}`, `e_1 * e_2`); every angle is
named (`sin(θ) = y/r`, never `sin = y/r`) — were written into `CLAUDE.md` and the book outline as
standing conventions, and applied by one sweep over every place the project writes math for a
reader: book prose and figure labels, book and demo notebooks, Python docstrings (hand-written and
the generator's table), tests, Lean doc comments, reference docs, README. `make format`'s steps,
`make test`, `make lean` and `make docs` passed on the result.

## Context (still true of the repo)

- **The rules, their rationale and their exemptions** are `CLAUDE.md` › "Math notation for
  readers" (the book-facing bullet is `tasks/reference/book-outline.md` › "Notation & prose
  conventions for proof pages"). Why: a reader from precalculus reads `cos θ` and `r(cos θ, sin θ)`
  as products, and in a geometric-algebra book a bare juxtaposition *is* a product, so the typeset
  math must read exactly like the code, where `*` is the geometric product. Exempt: Lean *code*
  (`Real.cos θ` is the language's application syntax), Python code, doctest lines.
- **Decisions (William Emerison Six <billsix@gmail.com>, 2026-10-09):** the symbol is a literal `*`
  in LaTeX math (not `\ast`, not `\cdot`, which is the dot product, not `\times`, the cross
  product); and `*` marks the geometric product of non-scalars too (`\vec{a} * e_{12}`), not only
  scalar multiplication — no juxtaposed product remains anywhere a reader sees math.
- **A doc that quotes a rejected spelling on purpose** (the rule paragraphs themselves) fences the
  span with `<!-- notation-rule: begin -->` / `<!-- notation-rule: end -->`, which a re-sweep
  skips; `CLAUDE.md` states this beside the rules.
- **Where juxtaposition deliberately survives:** the middle dot as the **dot product** (`a·b`);
  Lean code quoted in doc comments (`rot θ v`, `smul k v`); the relative-graph-paper page's
  quotation of the reader's prior `a i + b j` and the demo notebook's "you already know how to
  multiply `(x + 2)(x + 3)`" (quotations, kept verbatim); `blade-square-sign.rst`'s sliding
  diagrams, whose columns a `*` would misalign — the page says so in one sentence before the first
  of them; and a few proof-technique chains in `lean-ga-proof-architecture.md`'s tactic notes
  (`R u (R̃ R) v R̃`), written as the reader of that doc writes Lean.

## Chronology (2026-10-08 → 10-09)

1. **Filed** 2026-10-08 with the three rules, a per-file-group hit table (23 book, 20 figure,
   35 Lean-doc, 16 `src/`, 13 demo-notebook, 12 reference-doc, 6 test, 4 generator, 1 README hits
   for rule 1; a handful for rule 3; ~25 `|a||b|`-style juxtapositions), and the plan: rules into
   `CLAUDE.md`, a discovery script, a read-every-hit fix in generator → `src/` → book → figures →
   notebooks → Lean docs → reference docs order, then the gates.
2. **Decisions** 2026-10-09 (above): literal `*`; `*` for all products. (The filed text of those
   two decisions had lost its backslashes to control characters — `\ast` had become a BEL byte plus
   "st" — repaired in the rewrite.)
3. **Go-ahead** 2026-10-09; the work (`9a699d6`, "added parenthesis and use * for multiplication").

## What was done (all in `9a699d6`)

**The rules.** `CLAUDE.md` gained the section "Math notation for readers: parentheses apply, `*`
multiplies, every angle is named"; the outline gained its bullet. Both quote the rejected
spellings, hence the markers.

**Discovery.** `tasks/adhoc/math-notation-parens-star-named-angles/discover.sh`, one grep per
rule over every reader-facing group; `data/hits-before.txt` held 1079 lines (rule 1: 183,
rule 3: 40, rule 2 candidates: 856 — a list to read, not a to-do list, because the middle dot is
usually the dot product). The counts exceeded the filed table because the two tasks archived
earlier that day (typed notebooks; indexed subscripts) had added pages and notebooks in the old
spelling.

**The codemod** `fix.py` did the mechanical part, on prose regions only: Python comment and
string tokens (doctest lines skipped), Lean comment spans, whole `.rst`/`.md` files minus the
fenced spans and `blade-square-sign.rst`. It took three versions, each after a full read of the
diff and a revert-by-path of the processed files before the final run (second run = 0 changes):
v1 rewrote the rule text itself ("not `cos(θ)`") and swallowed the brace after a subscript inside
`\frac`; v2 turned the prose cross-reference `sin (§3)` into `sin(§3)` and half-converted
`|a|^2|b|^2` and `2|a||b|(…)`; v3 (final, 96 files) restricted the trig-parenthesis lookahead to
angles and magnitudes, required a complete magnitude after a digit, stopped treating
`e_3 (use the …` and `grade-3 (e_123)` as products, and handled the combining-mark hats (`B̂`)
that `\b` cannot see.

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

**Gates.** Locally `ruff check .` and `ruff format --check .` clean, `ty check` over `src`, `tests`,
`tools`, `book/docs/notebooks` clean, `tools/check_epix_keywords.py` clean, `pytest` 696 passed
with doctests (after removing two stale gitignored `src/gacalc/g4.py`/`g5.py` from an older
generator, which the current `base.py` cannot import and the container never has). `make lean`
(`make -o image lean`): `[lean] OK`, the 10 warnings the pre-existing ones in
`ProjectionRotation3D.lean`. `make docs` (`make -o image docs`): exit 0, every notebook executed;
the proof-rotate derivation page and its figures read with the new notation in the PDF. The
discovery grep afterwards flags, for rules 1 and 3, only the fenced rule text, Lean code and the
prose "cos/sin (§3)"; rule 2's residue is the deliberate list in Context (`data/hits-after.txt`).

**Not changed.** The public API and the generated modules (the generator's docstring table was
edited; the emitted `g*.py` regenerate). No `CHANGELOG` entry: docstring wording, nothing a
consumer pins. The subscript sweep (archived 2026-10-09) had already run; this one ran on top of it.

## The maintainer's review of `9a699d6`, and the corrections (2026-10-09)

The maintainer read the diffs and flagged that some inner products had become `*`, in the Lean
doc comments especially. A full audit of every hunk in `9a699d6` where a middle dot was removed
(a script pairing each removed line with its replacement; 719 lines read) found:

- **Two genuine inner products wrongly converted**, both in `Projection3D.lean`: the Hestenes
  projection onto a plane, `(c·B)B⁻¹` and `(c·(a∧b))(a∧b)⁻¹`, had become `(c * B)` and
  `(c * (a∧b))`. Cause: the codemod's scalar-left-operand list treated any lone `c` or `s` as a
  coefficient, and `c` is a *vector* there. Both reverted; the lone `c`/`s` rule was removed from
  the codemod (which re-converted the reverted lines on its next run until it was), and two
  consecutive runs now change nothing. Every other removed dot was a scalar times something
  (`|a| * e₁`, `cos(θ) * v`, `(|a|/|b|) * b`, `|R|² * 1`, `c1 * e₁`) or a juxtaposed geometric
  product (`R v R̃`); the genuine dot products (`u·v`, `a·b`, `f·t`, `(v·d / d·d)`) were kept.
- **Three half-converted lines** finished in the rule's direction: `g⁻¹ * Mᵀ * g` (a matrix
  product, `galgebra-comparison.md`), `a * e`, `b * e`, `c * e` (`tests/test_frame.py`),
  `(2c² − 1) * e₁ + 2sc * e₂` (`unit-bivector-and-rotors.md`).
- **The versor identities had been left mixed:** `R = b·a + |a| * |b|`, `R·a = |a| * h`,
  `b · R = |b| * h`, `h·a = |a| * R`, `to·from`, `t·f + …`, `uvec β · uvec α`, `(a·b)·1`. In
  those the dot is the *geometric* product (the versor is `b a + |a||b|`), and beside a `*` it
  read as a dot product. All converted to `*` (36 sites across `Rotation3D`, `Versor2D`, `Rotor`,
  `Sandwich`, `G3`, `StandardPosition`, `ProjectionRotation2D/3D`, three reference docs, the
  graded demo notebook, and `proofs/README.md`, which the sweep's file list had never included).

A second verification over the whole `origin/master..tree` span (every removed middle dot,
classified by its left operand; the 81 hunks with a non-scalar left operand read in full) found
no further inner product converted and the `∗` scalar-product symbol untouched, and fixed five
stragglers: a division that had lost its grouping (`nR/|f| * |t|` became `nR/(|f| * |t|)`),
`|R|⁴·(u · v)`, the subscripted coefficients `c₁₂·e₁₂` (not in the codemod's list), `e_r · e_r`
in the pseudoscalar-sign doc, and `(−1)^(…) · |A|²` in `base.py`.

Gates after the corrections: `ruff check .` clean, `tests/test_frame.py` 16 passed (the one
docstring touched), `make lean` re-run: `[lean] OK`, the same 10 pre-existing warnings.

## Open questions

None.
