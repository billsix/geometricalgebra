# Adopt Hestenes notation for variable names (Greek scalars, lowercase vectors, capital multivectors)

**Status:** ready — decisions made 2026-09-30; awaiting go-ahead to start the sweep
**Priority:** 6
**Difficulty:** 6
**Created:** 2026-09-30 **Updated:** 2026-09-30 (William Emerison Six <billsix@gmail.com>)

## BLUF

Sweep the whole codebase (`src/`, `tools/`, `tests/`, `notebooks/`, docstrings) so variable
names follow **Hestenes / standard-GA notation**: a **Greek** letter for a scalar (`α`, `β`,
`λ`), a **lowercase Latin** letter for a vector (`a`, `b`, `v`, `x`), and a **CAPITAL Latin**
letter for a bivector/trivector/pseudoscalar or any general multivector/versor (`A`, `B`, `R`,
`I`). A reader can then tell an element's grade-class from its name, matching Hestenes &
Sobczyk / MacDonald — the books the library is written against. This is the convention that
motivated disabling ruff **N806** project-wide on 2026-09-30 (uppercase locals are now
intentional, not accidental constants; see `pyproject.toml [tool.ruff.lint]`). "Done" =
the one-branch rename pass (locals/internals only — **not** public parameters), green
`make format` + `make test`, and a reference doc + `CLAUDE.md` pointer. **All four design
questions are decided (below); this is now a go-ahead-to-execute gate, not a design gate.**

## Decisions (2026-09-30, William Emerison Six <billsix@gmail.com>)

1. **Scope = locals + internal (private) helpers only, NOT public parameters.** Public
   parameter names stay as-is and **N803 stays ON** — renaming a public parameter is a breaking
   keyword-arg change on the PyPI API, deferred to a separate versioned decision.
2. **Grade-pure ≥2 (bivector/trivector/pseudoscalar) = CAPITAL.** Lowercase is reserved for
   grade 1 (vectors); Greek for grade 0 (scalars); capital for everything else.
3. **Scalars = Greek letters** (`α`, `β`, `λ`, …), per what Hestenes actually uses (confirmed
   by lookup — the standard GA convention: Greek scalars, lowercase-Latin vectors,
   uppercase-Latin multivectors; en.wikipedia.org/wiki/Geometric_algebra). **Caveat, apply at
   rename time:** Python 3 *does* allow Greek identifiers, so this is feasible — but `λ`
   collides visually with the `lambda` keyword, Greek is hard to type and to `grep`, and some
   editors/tools mangle it. Where a Greek identifier would hurt more than help (a throwaway
   loop scalar, a name other code must type), fall back to a spelled-out Latin name
   (`alpha`, `lambda_`) and note it — the intent (grade-0 → "scalar-ish name") is what matters.
4. **One big review-and-fix pass on a branch** (not split by directory), for a single review.

## Context (read first)

- The trigger: while fixing `tools/derive_lean_algebra.py` (which used `A`/`B` for two 𝒢ₙ
  multivectors and tripped N806), we chose to keep the uppercase and **disable N806
  project-wide** rather than lowercase the math. This task is the natural follow-on: apply the
  same convention *consistently* everywhere, so the notation is a real, enforced-by-habit rule
  rather than one file's exception.
- **The user's stated rule (verbatim, 2026-09-30):** "go through all variables and use hestenes
  notation. I think it would be lowercase variable for scalars and vectors, capital for
  multivectors." Refined by the Q3 lookup below: Hestenes actually uses **Greek** for scalars,
  and the user chose "use whatever he used" — so scalars are Greek, not lowercase Latin.
- **Related tasks:** `tasks/archive/2026/10/05/consider-renaming-scalar-to-real.md` (done 2026-10-05; a separate axis — the *word*
  "scalar" vs "real", not the letter-case of variables); the two are orthogonal but both touch
  naming and both would land in a naming reference doc.

## The convention (decided)

| Grade-class of the value the name holds | Style | Examples |
|---|---|---|
| scalar (grade-0 / a plain real coefficient) | **Greek** (Latin fallback where Greek hurts) | `α`, `β`, `λ` / `alpha`, `lambda_` |
| vector (grade-1) | **lowercase Latin** | `a`, `b`, `v`, `x`, `axis` |
| bivector / trivector / pseudoscalar (grade-pure ≥2) | **CAPITAL Latin** | `B`, `T`, `I` |
| general / mixed-grade multivector, versor, rotor | **CAPITAL Latin** | `A`, `B`, `R`, `M`, `V` |

- **Already-protected / externally-fixed names are exempt** (unchanged): `cls`, `n` (the
  dimension, never `grade`), the `m`/`b` of `f(x)=m·x+b` in `translate`/`uniform_scale`, the
  interchange primitives, dunder/`_repr_latex_` names — per CLAUDE.md "an externally-defined
  name overrides the naming rules."
- **N806 is already off** (locals may be uppercase). **N803 (argument names) stays ON** — so
  this convention applies to **locals + internal helpers only**; public parameter names are out
  of scope (Decision 1).

## Scope / how to do it (on go-ahead)

- **Generator-first** for anything under `src/gacalc/g*.py`: those are generated + gitignored, so
  variable names there come from `tools/gen_specialized.py` — never hand-edit the output (see
  `tasks/reference/code-generator-architecture.md`).
- Discover candidates with a shell sweep, not a tree-walk (per CLAUDE.md ad-hoc/bulk rules): e.g.
  `git grep -nE '\b(mv|multivector|rotor|versor)\b'` for likely multivectors currently lowercase,
  and inspect each — **grade-class is a judgment call the linter cannot make**, so this is a
  read-every-hit pass, not a blind codemod. Log hits to `tasks/adhoc/hestenes-notation/data/`.
- Keep `make format` + `make test` green after each coherent batch; the rename must be
  behaviour-preserving (pure identifier renames).
- **Public parameters are OUT of scope** (Decision 1) — do not rename them in this pass. If a
  future versioned decision brings them in, note that any renamed *public* parameter is a
  keyword-arg breaking change → SemVer bump + `CHANGELOG.md` entry + grep consumers (mvp calls
  `from_scalar`, `versor_from_vectors`, etc.) before breaking, and N803 would then be relaxed too.
- **Write a reference doc** `tasks/reference/hestenes-variable-notation.md` (the rule table + the
  Greek-scalar sources below + the Latin-fallback caveat + the exempt-names list) and add a
  one-line pointer in `CLAUDE.md`'s coding-standard section, so the convention is durable. Carry
  the Sources section forward into that doc.

## Open questions

All resolved — see **Decisions** above (2026-09-30). Remaining gate is go-ahead to start the
one-branch sweep.

## Sources (for the Greek-scalar convention — Decision 3)

The rule "scalars = Greek, vectors = lowercase Latin, general multivectors = uppercase Latin" is
the standard Geometric-Algebra typographic convention. Confirmed by lookup 2026-09-30:

- **Wikipedia, "Geometric algebra" — Notation:** "A useful convention … scalars are denoted by
  Greek letters (α, β, …), vectors by lowercase Latin letters (a, b, …), and other multivectors
  by capital [Latin] letters (A, B, …)." <https://en.wikipedia.org/wiki/Geometric_algebra>
- **Primary sources the library is already written against** (the convention originates here;
  cite these in the reference doc when the pass runs — add the exact page once checked against
  the physical copies): D. Hestenes & G. Sobczyk, *Clifford Algebra to Geometric Calculus*; and
  A. MacDonald, *Linear and Geometric Algebra* (the slower, teaching-oriented companion this
  project leans on).
- **Python-feasibility note (not a math source):** PEP 3131 makes Greek identifiers valid Python
  3 — the basis for the Latin-fallback caveat in Decision 3, not for the notation itself.
