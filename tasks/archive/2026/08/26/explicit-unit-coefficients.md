# Make implicit unit coefficients explicit in basis-blade sums (`e_1` → `1 * e_1`)

**Status:** DONE 2026-08-26 (William Emerison Six <billsix@gmail.com>) — see Outcome.
**Priority:** 5
**Difficulty:** 4

## Outcome (2026-08-26)

Done, Bill liked it, CLAUDE.md updated. The final rule (broader than the original decision 3, after
Bill flagged the list-element inconsistency): **make the implicit `1` explicit wherever a bare blade
is a coordinate vector** — (a) sum terms, (b) list/tuple elements, and (c) the vector args of the
measure calls `area`/`volume`/`signed_area`/`signed_volume`; a blade used as a **direction** stays
bare (`cls.i(e_1, e_2)`, `plane_rotation(…)`, `rotor_from_vectors(…)`, `project(onto=e_1)`,
`coefficient(e_1)`). Applied by the AST codemod
`tasks/adhoc/explicit-unit-coefficients/add_explicit_unit_coefficients.py` (span-based text
insertion; also rewrites single-line `>>>` doctests). Totals across three passes: ~235 unit
coefficients made explicit across `tests/`, `notebooks/`, and `src/gacalc/` docstrings. **410 tests
green (behaviour unchanged — `1 * e_1 == e_1`), ruff + ty clean, codemod idempotent** (second run a
no-op). `book/` (textbook LaTeX math, not gacalc code — out of scope) and `README.md` (already
explicit) needed nothing. CLAUDE.md's "Build vectors from the basis constants" convention now states
all three rules and the direction-stays-bare carve-out.

**Codemod disposition (for /archive-task):** it is a **one-shot** conversion — the codebase is
converted and new code follows the convention by hand — so at archive it can be `git rm`'d (history
keeps it). It could instead be **promoted** to `tools/` as a re-runnable normalizer/checker if Bill
wants an ongoing gate; left under `tasks/adhoc/` for now, Bill to decide.

## Progress (Phase 1, 2026-08-26)

**Phase 1 done — `tests/` + `notebooks/`:** 127 unit coefficients made explicit across 12 files, via
the AST codemod `tasks/adhoc/explicit-unit-coefficients/add_explicit_unit_coefficients.py` (span-based
text insertion, so all formatting/comments are preserved). Verified: **410 tests pass (behaviour
unchanged — `1 * e_1 == e_1`)**, ruff + ty clean, and a **second codemod run is a no-op** (idempotent,
as required). Standalone blades (list elements like `[e_1, e_2]`, `project(onto=e_1)`) correctly left
bare; negatives handled (`a - e_2` → `a - 1 * e_2`, `-e_1 + …` → `-1 * e_1 + …`).

**Deferred, pending Bill liking the look** (the hard/risky surface — kept out of Phase 1 on purpose):
- **`src/gacalc/*.py` docstrings / doctests** — the codemod parses code, not the `>>>` lines inside
  string literals; rewriting those safely needs a doctest-aware pass (and `base.py` docstrings flow to
  the generated modules via `inspect.getdoc`, so fix them at the `base.py` source).
- **`book/` and `README.md`** — RST/prose code blocks, not AST-parseable; a targeted pass.

**Next steps:** (1) Bill reviews the Phase 1 diff. (2) If liked → do Phase 2 and update CLAUDE.md's
"Build vectors from the basis constants" convention (change its `2*e_1 + e_2` model to `2 * e_1 +
1 * e_2`). If not → revert Phase 1 (`git checkout tests notebooks`) and drop the task.

## Goal

For **educational clarity**, sweep the codebase and make the implicit coefficient `1` explicit
wherever a bare basis blade appears as a term in a multivector sum alongside explicitly-scaled
terms:

- `e_1 + 3 * e_2` → **`1 * e_1 + 3 * e_2`**
- `2 * e_1 + e_2` → **`2 * e_1 + 1 * e_2`**

So every term reads as `coefficient * basis`, and a student sees each coordinate the same way
instead of guessing that a bare `e_1` means `1 * e_1`. There is already inconsistency to normalize —
e.g. `tests/test_multivector.py:43` writes `1 * e_1 + 3 * e_3` while line 38 writes `5 * e_1 + 6 *
e_2` next to bare-blade sums elsewhere.

**This is a trial.** Apply it, Bill reviews how it reads, and **if he likes it, update `CLAUDE.md`**
— specifically the *"Build vectors from the basis constants, not the raw constructor"* convention,
which today shows `2*e_1 + e_2` (the bare form) as the model. Do **not** edit `CLAUDE.md` up front;
that's the second step, gated on Bill liking the diff.

**Purely cosmetic — zero behaviour change:** `1 * e_1 == e_1`, so every test/doctest result is
unchanged. The value of the task is entirely how the source *reads*.

## Scope

Teaching-facing GA code first, where clarity pays off most:

- `tests/` (the largest surface), `notebooks/`, and **docstrings / doctests** in `src/gacalc/*.py`
  (hand-written modules).
- The book (`book/`) `literalinclude`/prose examples and `README.md`.
- Applies to every spelling of a basis blade: module constants (`e_1`, `e_12`), qualified
  (`g2.e_1`, `gn.e_1`), and class constants (`Vector.e_1`, `Bivector.e_12`, `G.e_123`).

**Out of scope / do NOT touch:**

- **Generated modules** `g1.py`/`g2.py`/`g3.py` (build artifacts — if any generated *docstring* shows
  the bare form, that comes from `base.py` via `inspect.getdoc`, so fix it at the `base.py` source,
  not the generated file).
- Non-GA arithmetic (plain `int`/`float`/`sympy` sums) — the change is only for **basis-blade
  terms**.
- `coeff_e_1=...` keyword constructor calls (already explicit; and the house rule says teaching code
  shouldn't use that form anyway).

## Decisions (Bill, 2026-08-26)

1. **All multi-term sums** — not only the mixed case. `e_1 + e_2` → `1 * e_1 + 1 * e_2` too. The
   rule is simply "every basis-blade term inside a `+`/`-` sum is `coef * basis`."
2. **Negatives too.** `2 * e_1 - e_2` → `2 * e_1 - 1 * e_2` (keep the `-` operator, reads as "minus
   one e_2"); a lone `-e_2` term → `-1 * e_2`.
3. **Standalone single terms stay bare** (my recommendation — Bill's "whatever makes a cleaner API";
   not explicitly ruled on, proceeding with this). A lone `e_1` that is *not* part of a `+`/`-` sum
   (e.g. `content([e_1])`, `Vector.project(onto=e_1)`) keeps the bare form — a `1 *` there is noise,
   not symmetry. **Only rewrite terms inside a multi-term sum.** (Flag at review; easy to extend if
   Bill wants standalone too.)

## How (mechanism — this is the hard part, hence D4)

- **Not a blind regex.** Detecting "a bare basis blade that is a term in a GA sum" without also
  hitting non-GA `+`/`-`, string contents, comments, or a bare blade used as a whole value needs
  care. Prefer an **AST-based codemod** (walk `ast.BinOp(Add/Sub)` chains; rewrite a term that is a
  basis-blade `Name`/`Attribute` — matched against a known basis-name pattern `e_<digits>` and the
  `*.e_*` class/qualified forms — into `BinOp(Mult, Constant(1), <blade>)`), or a **carefully
  scoped, reviewed pass** with printed before/after per file. Save the codemod under
  `tasks/adhoc/explicit-unit-coefficients/` per the ad-hoc-scripts convention.
- **Make it idempotent and prove it:** a second run must be a no-op (don't turn `1 * e_1` into
  `1 * 1 * e_1`). Run it twice; the second run reports zero changes.
- **Doctests are code too:** rewriting a doctest *input* line is fine (output is unchanged), but the
  rewrite must stay inside the `>>> ` and not disturb the expected-output lines.
- **Report the diff by group** (tests / notebooks / docstrings / book) so Bill can judge the look
  before the CLAUDE.md decision.

## Verify

- `make test` green **and unchanged** (cosmetic only — same values, same doctests).
- `make format` clean (`ruff` + `ty check`); confirm `ruff format` is idempotent afterward.
- Codemod run twice → second run is a no-op (idempotence proof).

## Second step (only if Bill likes it)

Update `CLAUDE.md` › *"Build vectors from the basis constants, not the raw constructor"* to state the
explicit-unit-coefficient preference and change its example from `2*e_1 + e_2` to `2 * e_1 + 1 *
e_2`. Leave this until after review.

## Cross-links

- `CLAUDE.md` › "Build vectors from the basis constants, not the raw constructor" (the convention to
  update in step 2).
- Representative surface: `tests/test_multivector.py` (already mixes `1 * e_1` and bare forms),
  `notebooks/`, `src/gacalc/*.py` docstrings.
