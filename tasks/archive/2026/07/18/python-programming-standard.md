# Write a Python programming standard (into README.md + CLAUDE.md)

**Status:** complete
**Completed:** 2026-07-18 — standard drafted into CLAUDE.md (+ README pointer); ruff
`N` enabled and all fallout fixed; the full judgment-call standard applied across every
hand-written module (`transforms`/`functions`/`base`/`gn`/`tools`/`tests`/notebooks)
**and the generator's emitted output**; plus the `Blade` alias and a typed `TypeSpec`.
Repo fully ruff + ty clean, 285 tests pass, generator deterministic.
**Created:** 2026-07-18

## Decisions (2026-07-18, from Bill)

- **Canonical home = `CLAUDE.md`.** The full standard lives in CLAUDE.md (already
  the conventions/architecture doc); `README.md` gets a short "Coding standards"
  pointer to it. One source of truth. *(resolves Q1)*
- **Audience = both, agent-terse.** Each rule = a statement + a one-line rationale,
  readable by humans and actionable by agents; a worked before/after example only
  where a rule is unusual (i.e. for the Scheme-style inner-fn shape). *(resolves Q2)*
- **Inline-single-use is context-dependent.** Lean/inline in library code; name +
  type the GA values in teaching notebooks. Rule of thumb: **inline a value used
  exactly once *unless* the name documents an otherwise-opaque expression.**
  *(resolves Q3 — reconciles with the pedagogical locals just added, and with the
  existing "no local aliases" convention)*
- **Scheme-style inner-fn is descriptive/preferred, not enforced.** Document it as
  the preferred shape for *new* code; **don't churn** existing early-return code;
  leave cheap top-of-function `raise`s on nonsensical args as-is. *(resolves Q4)*
- **Enable ruff's `N` (pep8-naming) rules** so naming (N1) is self-enforcing, not
  review-only. Expect a first-pass that flags existing names (generated code, math
  single-chars, `sym_vec*` etc.) → handle with `per-file-ignores`/`# noqa`, not by
  dropping rules. *(resolves Q9, and Q6 for naming)*
- **Organize the standard as enforced-vs-prose, maximally.** Explicitly: "(a) ruff
  enforces these — see `pyproject` `select`, don't repeat" vs "(b) judgment calls —
  prose." Keeps it terse and non-duplicative. *(resolves Q10, and Q6 broadly)*
- **Include the FULL idiom checklist (N3)** as one-liners (+ the enforced-vs-prose
  tags), not a curated subset. *(resolves Q11, and Q8 for idioms)*
- **Annotate types as generously as reasonable** (Bill 2026-07-18): prefer a declared
  type over none — including locals in library code, not just signatures; skip only
  pure noise (`n = 3`); **when in doubt, annotate.** Still bounded by "don't fight the
  checker." (Shifts standard **B** from "locals only when non-obvious" toward generous
  typing; reflected in CLAUDE.md's type-annotation rule.)

## Goal

Articulate Bill's **Python programming standard** as a written document, and put it
in **`README.md`** and **`CLAUDE.md`**. It should capture two kinds of thing:

1. **Normal/standard Python** stated *with its rationale* — e.g. *why* it's
   `sorted(xs)` (returns a new list; an expression) rather than `xs.sort()`
   (mutates in place; returns `None`) — the command/query separation and
   expression-oriented idioms that experienced Python programmers internalize.
2. **Bill's personal conventions** that go beyond stock Python — how he handles
   type annotations (how much gets typed and why), inlining single-use values, and
   a Scheme-influenced function structure (main logic as a nested inner function,
   with the guard/preprocessing/dispatch *below* it, calling in).

This task is **write the doc + investigate the existing style + ask questions** —
**not** to refactor the codebase to match. Any code refactors that the standard
implies are a *separate, later* task.

> **Targets: `README.md` (user-facing) and `CLAUDE.md` (contributor/architecture +
> agent guide).** Both already exist. `CLAUDE.md` is dense with conventions already
> — so the real design question is *where the standard's canonical text lives and
> how it avoids duplicating/contradicting CLAUDE.md's existing convention notes*
> (see Q1/Q7). `git ls-files` confirms `tasks/` is tracked (not gitignored); Bill
> commits from the host.

## The specific standards Bill named (to articulate)

Verbatim intent from Bill, expanded with what I'd write — **each needs his
confirmation/refinement**:

### A. Expression-oriented / command-query idioms ("`sorted` not `sort`")
- `sorted(xs)` / `reversed(xs)` / a comprehension **return a new value** and are
  *expressions*; `xs.sort()` / `xs.append()` mutate and return `None`. Prefer the
  value-returning form; don't write `x = xs.sort()` (a classic bug).
- Generalize: **command–query separation** — a function either *does* something
  (side effect, returns `None`) or *computes* a value (no side effect), not both.
- Prefer expressions over statements where it reads clearly (comprehensions,
  ternaries, `match` returning a value). *Codebase already does this* — `sorted(`
  in `base.py`, comprehension-built results everywhere, no in-place `.sort()` in
  `src/`.

### B. Type annotations — how much, and why
This is exactly what the just-finished `annotate-local-variable-types` task
established empirically. Proposed articulation:
- **Signatures (params + returns) are annotated** — they're the contract.
- **Local variables are annotated when the type is non-obvious or pedagogically
  useful**, *not* blanket. `n = 3` needs none; `r: Rotor2 = a * b` earns one.
- **Don't fight the type checker.** A locally-correct annotation that forces edits
  to unrelated logic (or breaks flow-narrowing) is not worth it in a readability
  pass — leave it inferred and say why (the `__iter__` / reused-name cases).
- **Read-only mapping/collection params take the covariant supertype** (`Mapping`,
  `Sequence`, `Iterable`), not the invariant concrete (`dict`, `list`) — so callers
  passing a subtype-valued container aren't rejected.
- **Polymorphic values take the abstract base** (`MultiVectorBase`), never a
  concrete class picked from a runtime value.
- Modern syntax only: `A | B` unions (ruff `UP007`/`UP035`), `X | None` not
  `Optional[X]` where the rule applies.
- *(Open: how does this interact with C and D below? See questions.)*

### C. Inline a value that's used exactly once
- If a local is bound and then referenced a **single** time, inline it — the name
  earns its keep only by being reused or by *explaining* an opaque expression.
- **Tension to resolve (Q3):** this pulls against B's "annotate a pedagogical
  local" and against naming-for-clarity. The codebase's own
  **"no local aliases for values that have a direct name"** convention (CLAUDE.md)
  is the same spirit. Likely the real rule is *"inline single-use values that add
  no name-level meaning; keep a single-use local only when the name documents an
  otherwise-opaque expression"* — needs Bill's line.

### D. Scheme-style structure: inner function first, dispatch/guards below
Bill's model (from Scheme): the **main body is a nested inner function** defined
first; the **guard/precondition/preprocessing checks come at the bottom**, and
call the inner function. This *inverts* the common Python "guard clauses with
early `return` at the top" shape.
- **Precedent already in the codebase** (so this is partly documenting, partly
  formalizing): `Gn._geometric_product` defines `decrease_grade` (the core
  recursion) then drives it below; `compose` defines `composed_fn` / `inv_composed_fn`
  then wires them; `base.project/reject/reflect` define `r` + `rejection`/`reflection`
  then `match` on the operand at the bottom; `to_matrix` defines `coords` then
  builds columns.
- **But the repo also uses top-of-function guard clauses / early returns**
  (`__truediv__`, `__add__`, `magnitude`, `inverse`, `to_matrix`'s `NONLINEAR`
  raise). So this is a **style shift**, not a pure description — **Q4**: is the
  standard *prescriptive* (new code should invert guards into the inner-fn shape;
  refactor opportunistically) or *descriptive* (document the pattern as
  *preferred/allowed*, don't churn existing early-returns)? And how does it square
  with the widely-held view that early-return guard clauses are very readable?

## Investigation — existing conventions already consistent in the code

Things the standard could **codify from what's already here** (so it reads as "our
house style," grounded in the repo, per Bill's "investigate what's consistent"):

- **One concept per file / thin public surface** (CLAUDE.md "Module layout";
  acyclic layering with `functions.py` the only base-importable leaf).
- **`match`/structural dispatch** is the idiom for case analysis (17 in `g2.py`,
  22 in `g3.py`, plus `base`/`gn`) — pairs naturally with D's inner-fn+dispatch.
- **Keyword arguments for meaning-bearing call sites** — `rotor_from_vectors(
  from_vector=…, to_vector=…)`, `project(onto=…)` (36 keyword-arg uses in
  tests/notebooks); keyword-only `*,` markers in `transforms.py`.
- **Full-word, intention-revealing names**; the dimension is `n` (the rename from
  the misleading `grade` is called out in CLAUDE.md). Constants/aliases avoided
  when a value already has a canonical name.
- **Docstrings cite the source** (Hestenes page/equation — 25 refs in `base.py`);
  the generator copies base docstrings so they never drift.
- **Dataclasses, `slots=True`** for value types; `@dataclass` with an interchange
  protocol rather than ad-hoc `__init__`.
- **Immutability / value semantics** — multivectors are values; ops return new
  values; no in-place mutation of coefficients after construction (`Gn` even
  eager-simplifies in `__post_init__`).
- **Comprehensions and `sum(..., start=…)`/`math.prod(..., start=…)`** over manual
  accumulation loops.
- **Explanatory comments explain *why*, inline at the point they apply** (mirrors
  Bill's own CLAUDE.md rule about caveats attached to the step).
- **Numeric-preservation discipline** — don't promote a `float` pipeline to sympy
  (the `magnitude`/`inverse` rule). A domain-specific but real house rule.

## Candidate standard content (web-researched 2026-07-18 — Bill to react/select)

Sourced from PEP 8, PEP 20, the Google Python Style Guide, and ruff's rule docs.
This is a **menu to talk through**, not adopted yet. **Key organizing insight:**
much of PEP 8 *layout* + several idioms are **already mechanically enforced by this
repo's ruff `select`** — the standard should NOT re-prose those; it should say "ruff
enforces X" once and spend its words on the **judgment calls ruff can't check**
(naming grammar, the mutate/return idioms, EAFP, the type-annotation philosophy, the
Scheme-style structure). See the enforced-vs-prose split in Q6/Q9.

### N1. Naming conventions (PEP 8) — the part Bill most wants
- `snake_case`: functions, methods, variables, parameters, modules, packages
  (packages ideally no underscores). *bad* `def CalcTotal(itemList)` → *good*
  `def calc_total(items)`.
- `CapWords`/PascalCase: classes, type vars, exceptions. Acronyms all-caps
  (`HTTPServerError`). Exceptions end in **`Error`** (`ValidationError`).
- `UPPER_SNAKE_CASE`: module-level constants (`MAX_RETRIES = 5`).
- `_single_leading`: non-public/internal (prefer non-public if unsure — easier to
  promote later). `__double_leading`: name-mangling (Google discourages; prefer one
  underscore). `trailing_` to dodge a keyword (`class_`, `type_`). `__dunder__`:
  leave to the language, never invent.
- Never `l`/`O`/`I` as single-char names. Avoid redundant type/container suffixes
  (`names` not `name_list`; `name_by_id` not `id_to_name_dict`). No letter-deleting
  abbreviations (`convert_to_string` not `cvt_str`).
- `self`/`cls` for the first method/classmethod arg. Short names OK in narrow scopes
  only: loop indices `i`/`j`, `except … as e`, `with open() as f`, math, comps.
- **Naming grammar** (standard practice, not codified): verbs for functions, nouns
  for values/classes; boolean predicates `is_`/`has_`/`should_`/`can_`
  (`user.is_admin`, `is_active = …`). *(This repo already follows most of this —
  see the "n not grade", full-word-names note in Investigation.)*
- **Ruff can enforce most of N1 mechanically via the `N` (pep8-naming) family** —
  currently **NONE are enabled**. Candidates: N801 (class CapWords), N802
  (func lowercase), N803 (arg lowercase), N806 (local lowercase), N804/N805
  (`cls`/`self`), N818 (`Error` suffix), N815/N816 (no mixedCase). → **Q9.**

### N2. Mutate-vs-return idioms (Bill's "sort vs sorted", generalized)
Principle: **Command–Query Separation** — a method either *does* (mutates, returns
`None`) or *answers* (returns a value, no side effect), not both.
- In-place methods return `None` **on purpose**: `list.sort/reverse/append/extend/
  insert/remove`, `set.add/update`, `dict.update`. So *bad* `top = names.sort()`
  (→ `None`, and mutated `names`) → *good* `top = sorted(names)` (new list) OR
  `names.sort()` as its own statement then use `names`.
- **Never chain a mutator**: *bad* `data.sort().reverse()` → `AttributeError` →
  *good* `data.sort(reverse=True)` / `sorted(data, reverse=True)`.
- Prefer the returns-new (query) form when you want a value to name/pass; reserve
  in-place for when mutation IS the intent and the object is reused by name.

### N3. Idiomatic Python (PEP 20 + community) — each = one-line rule + rationale
Marked **[ruff]** where this repo's config already enforces it (→ don't re-prose):
- **EAFP over LBYL** — `try/except` over pre-checks.
- **Truthiness for emptiness** — `if not seq:` not `if len(seq)==0:` (but compare
  ints explicitly: `if count == 0:`).
- **`is`/`is not` for `None`/singletons; `==` for values** **[ruff E711/E712]**;
  don't `== True`. `isinstance()` over `type(x) == T` **[ruff E721]**.
- **`enumerate()`** over `range(len())`; **`zip()`** for parallel iteration.
- **Comprehensions / genexprs** over trivial map/filter+loop (keep them simple —
  one `for`, at most one `if`).
- **f-strings** over `%`/`.format()`.
- **`with`** for resources (don't rely on `__del__`).
- **`dict.get()`/`defaultdict`/`setdefault`** over key-check branches.
- **Iterable unpacking** (`first, *rest = xs`).
- **No mutable/callable default args** **[ruff B006/B008]** — use `None` sentinel.
- **`pathlib`** over `os.path`.
- **Keyword args** at call sites for meaning (already a house convention).
- **Flat over nested** — guard clauses / early return (note: interacts with Bill's
  Scheme-style **D** — reconcile which shape wins where).
- **No bare `except:`** **[ruff E722]**; **no stray `print`** **[ruff T201]**.
- **Consistent returns** — if any branch returns a value, all do (explicit
  `return None`).

### N4. What this repo's ruff ALREADY enforces (so the standard just references it)
Current `select` = `F401 F811 E402 I001 TID252 F841 E302 E231 B006 B007 B008 UP007
UP035 S311 S602 T201` **plus the whole `E`, `F`, `I` categories**. That already gives:
PEP 8 layout/whitespace/blank-lines (`E`), the Pyflakes correctness tier (`F` —
unused/undefined/logic bugs, incl. E711/E712/E714/E722 idioms), import sorting (`I`),
modern unions (`UP007`/`UP035`), mutable-default & bugbear checks (`B006-008`),
no-`print` (`T201`), abs-imports (`TID252`), crypto-random / shell=True (`S311`/`S602`).
**Gap: zero naming enforcement** (no `N`). So the standard's naming section (N1) is
exactly the part that's review-only today unless `N` is added.



**Q1–Q4 are RESOLVED — see "Decisions" near the top.** Still open: **Q5, Q6, Q7,
Q8** below.

1. ✅ *(resolved — CLAUDE.md canonical, README pointer)* **Canonical home + README↔CLAUDE.md split.** The standard should be *one* source
   of truth to avoid drift. Which is canonical: (a) `CLAUDE.md` holds the full
   standard (it's already the conventions/architecture doc) and `README.md` gets a
   short "Coding standards" pointer to it; (b) `README.md` holds it (user-facing)
   and `CLAUDE.md` links to it; or (c) full text duplicated in both? My lean: (a) —
   the standard is contributor/agent guidance, which is CLAUDE.md's job, and README
   just points to it.
2. ✅ *(resolved — both, agent-terse)* **Audience & altitude.**
3. ✅ *(resolved — context-dependent; inline single-use unless the name documents
   an opaque expression; lean library / named+typed notebooks)* **Inline-single-use
   vs. named/annotated locals.**
4. ✅ *(resolved — descriptive/preferred; no churn of existing early-returns; cheap
   top-of-fn raises stay)* **Scheme-style inner-fn.**
5. **How many rules, how long?** A tight one-screen "house style" list, or a fuller
   document with a worked before/after example per rule (esp. for D, which is
   unusual enough to need a concrete example)?
6. **Enforcement.** Should any of these be *mechanically enforced* (ruff rule,
   a note in `format.sh`) vs. prose-only guidance? (e.g. an "inline single-use"
   or "sorted-not-sort" lint isn't standard, but some are expressible.)
7. **Dedup with CLAUDE.md's existing notes.** CLAUDE.md already states several of
   these idioms in passing (the no-local-aliases convention, keyword-arg rotations,
   `n`-not-`grade`, numeric-preservation, one-concept-per-file, caveats-inline).
   Should the new standard section *absorb and centralize* those (removing the
   scattered mentions), or sit alongside them and cross-reference? And: promote the
   type-annotation philosophy discovered in the annotate task into this permanent
   standard — yes?
8. **Any more of your idioms to include?** You mentioned these are "the kind of
   stuff" — are there others (error-handling style, when to use a class vs a
   function, import ordering, test structure, naming of predicates `is_*`, use of
   `assert` for invariants, f-strings, etc.) you want captured while we're here?

9. ✅ *(resolved — enable the `N` family; per-file-ignores for the fallout)*
10. ✅ *(resolved — organize enforced-vs-prose, maximally)*
11. ✅ *(resolved — full idiom checklist)*

## Rollout (incremental — each step: I finish + verify, Bill reviews, Bill commits, then next)

- [x] **1. Draft the standard into `CLAUDE.md`** (done 2026-07-18) — new
      "## Coding standard (Python)" section, organized enforced-vs-prose, full idiom
      checklist, one worked example (the inner-fn shape), project conventions absorbed
      by reference. **Awaiting Bill's review + commit.**
- [x] **2. README "Coding standards" pointer** (done 2026-07-18) — new
      "## Contributing" section pointing at CLAUDE.md's standard. Awaiting review.
- [x] **3. Enable ruff `N` in `pyproject.toml`** (done 2026-07-18) — **fixed all
      fallout, ZERO suppressions** (generated `g*.py` were already N-clean).
      `setup.py` `build_py_with_codegen`→`BuildPyWithCodegen` (N801); `nbplotutils`
      `graphBounds`→`graph_bounds` (N803), `extraLinesMultiplier`→
      `extra_lines_multiplier: int` (N816); generator `SELF`/`COEF`→`self_ann`/
      `coef_ann` (N806); ~21 uppercase math locals in `test_transforms`/`test_graded`
      lowercased **+ typed** (2 `t`-collisions → `translate_fn`). Gate: ty clean,
      determinism OK, 285 tests pass. Awaiting review.
- [x] **4. Apply the judgment-call standard to existing hand-written code, module by
      module** — the "new code only" default in the standard is lifted **for this
      task**: refactor existing code to the standard (inner-fn shape where it reads
      better, idioms, inline single-use, naming grammar). Skip generated `g*.py` (fix
      via the generator if needed). Each module (or function group) is a
      finish→review→commit increment. Gate each: `make test` + `make format` green.
      Suggested order (self-contained first): `transforms.py` → `functions.py` →
      `base.py` → `gn.py` → `tools/` (generator) → `tests/` → notebooks.
  - [x] `transforms.py` (done 2026-07-18) — generous typing of the untyped locals
        (`rotor`/`plane`/`i`/`origin`/`directions`/`columns`/`cos_half`/… + `coords`
        return); modernized `typing.Optional[X]`→`X | None`; inner-fn shapes already
        idiomatic, left intact. Gate green (ty, 285 tests). Awaiting review.
  - [x] `functions.py` (done 2026-07-18) — modernized 2 `typing.Optional[X]`→`X | None`
        dataclass fields; typed `compose`/`inverse` locals (`fns`/`linearity`/
        `inv_fns`/`step`/`f_inverse`); left `law` untyped (verbose type, already
        commented — the "as much as *reasonable*" line). Gate green (ty, 285 tests).
  - [x] `base.py` (done 2026-07-18) — **typing-only, zero GA-logic/structure changes**
        (the reference stays pristine): typed the ~10 remaining untyped locals
        (`mag_sq`/`grades`/`r`/`components_in_plane`/`label`/`scale`/`blades`/
        `magnitude_squared`/`projected`). Already used `X | Y` unions; `project`/
        `reject`/`reflect` already exemplify the inner-fn shape. Gate green (285 tests).
  - [x] `gn.py` (done 2026-07-18) — one typing addition
        (`sorted_blade_dictionary_entry: BladeDictionaryEntry`) in the blade-canonical
        recursion; no logic touched. Already fully annotated otherwise. Gate green.
  - [~] loop/unpack typing amendment (2026-07-18, Bill) — CLAUDE.md now documents:
        statement `for`/unpack targets take a bare `name: Type` line above; NOT
        comprehension loop vars (separate scope); and a name reused across loops of
        different (sub)types must be **split into distinctly-named typed vars** (not
        left to inference). Applied to `functions.py` (`composed_fn`/`inv_composed_fn`
        loop `f`s; compose-body `f`→`f`+`invertible_fn`) and `gn.py` (`symbols(...)`
        unpack → six `sympy.Symbol` decls). Re-gated green.
  - [x] `tools/` (done 2026-07-18) — **both parts.** (A) generator *source*
        (`gen_specialized.py` + `astbuild.py`): ~89 locals typed (ast-node types), plus
        loop/unpack decls; sensible skips (`term_grade_key` chained assign, `cse`
        unpacks, param-reassigns). (B) generated *output* made standard-compliant by
        fixing the generator to emit typed locals (`d: BladeCoef`, `left`/`right:
        BladeCoef`, cse temps `: Coef`), a typed `_coerce`, and ≤88-col coordinate
        docstrings. Gate: generator runs, **deterministic**, ruff+ty clean on source
        AND generated, 285 tests. Awaiting review.
  - [~] type double-check (Bill 2026-07-18) — verified the Part-A annotations are
        domain-correct. Found the real gap: `TypeSpec` was an untyped
        `collections.namedtuple`, so `spec.blades` was `Any` and the
        `list[tuple[int, ...]]` blade annotations were accepted *gradually* (trusted,
        not ty-verified). **Hardened:** `TypeSpec` → `typing.NamedTuple`
        (`blades: tuple[tuple[int, ...], ...]`, etc.) + tightened `blades_of_grade`'s
        bare `-> tuple`. Now ty genuinely verifies every blade annotation — all pass
        clean, confirming correctness.
  - [~] `Blade` type alias (Bill 2026-07-18) — the raw `tuple[int, ...]` (a basis
        blade) was used ~40× with no named alias, though `Coef`/`BladeCoef` exist.
        Introduced **`Blade = tuple[int, ...]`** in `base.py` (beside `Coef`),
        `BladeCoef = dict[Blade, Coef]`, and threaded `Blade` through `base.py`,
        `gn.py`, the generator (`gen_specialized.py`, incl. `TypeSpec.blades:
        tuple[Blade, ...]`), and `test_conformance.py`. Generated output unaffected
        (uses `BladeCoef`). Gate: ruff+ty clean, deterministic, 285 tests.
  - [x] `tests/` (done 2026-07-18) — ~200 remaining "obvious" locals typed across all
        9 files (`MultiVectorBase` for parametrized-`cls` values, concrete types for
        fixed, `Coef`/`Blade`/`float` for scalars, `InvertibleFunction`/`np.ndarray |
        sympy.Matrix` for transforms, loop/unpack decls). 5 ty errors from over-broad
        `MultiVectorBase` (where `.dual()`/`.DIMENSION`/`.coeff_e_1` need concrete) +
        one `Coef`-should-be-`Expr` — fixed (don't-fight-the-checker: narrowed or let
        inference give the concrete union). Gate: ruff + ty clean, 285 tests.
        *(Process note: the delegated pass first stalled silently, then a synchronous
        re-run blocked ~27 min with no visibility — do this incrementally next time.)*
  - [x] notebooks (done 2026-07-18) — renamed junk names (`asdf*`→`vec_a`/`vec_b`/
        `biv`, `aoeu*`→`p`/`q`) + typed them `MultiVector`; **fixed all 6 long-standing
        `displaymv.py` E501 prose lines → the whole repo is now ruff-clean**. Left the
        pure-scalar/scratch locals per the standard's "type the GA *values* in
        notebooks" guidance. Gate: ruff clean, all notebooks parse.
  - **✅ Module sweep complete** — the whole standard is applied.

## Plan (superseded by the Rollout above; kept for reference)

- [ ] Resolve Q1–Q8; settle the canonical home and the CLAUDE.md shape.
- [ ] Draft the standard: intro + rule sections (A–D + the codified house style),
      each rule = *statement + one-line rationale* (+ a before/after for D).
- [ ] Add to `README.md` (and create/populate `CLAUDE.md` per Q1), keeping a single
      source of truth to avoid drift.
- [ ] (Separate future task, if Bill wants) refactor passes to bring code toward
      the prescriptive rules (D especially).
