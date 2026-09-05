# Type-annotation audit: sweep all Python, list where types should be added

**Status:** READY — scoped 2026-09-05, NOT started; awaiting an explicit go-ahead to run the sweep.
Parameters settled by the maintainer: **apply, don't just list**; **scope = all four dirs** —
`src/` + `tools/` + `tests/` + `notebooks/` (NOT `tasks/`); **both add missing AND tighten** loose
annotations ("everything you can find"). Execute directly, gated per batch, once told to go.
(William Emerison Six <billsix@gmail.com>)
**Priority:** 4
**Difficulty:** 5

## BLUF

Read **every** hand-written Python file in `src/` and `tools/` (and, if wanted, `tests/` +
`notebooks/`) and produce a **catalog of every place a type annotation should be added or
tightened** — one row per site: file:line, the unannotated/loosely-typed name, and the concrete
type it should carry. The maintainer wants **more types listed than currently exist** — bias the
sweep toward *more* annotations, not fewer. Deliverable is the **list**; applying it is a separate,
gated step. The bar is set by `CLAUDE.md` › "(b) Judgment calls" › **"Type annotations — annotate
generously"**, which this task executes against the whole tree.

## Context — read first (cold-start; assume none of the discussion is in memory)

- **The governing convention is already written** — `CLAUDE.md` › "Coding standard (Python)" ›
  "(b) Judgment calls" › **"Type annotations — annotate generously."** Read it before cataloging.
  Its rules, condensed:
  - **Signatures (params + returns) always** — the contract.
  - **Locals: as much as reasonable — prefer a declared type over none, including in library code**
    (`r: Rotor = a * b`); skip only where it would be pure noise (`n = 3`); **when in doubt,
    annotate.**
  - **Loop/unpack targets** can't be annotated inline → declare the type on the line *above*
    (`blade: tuple[int, ...]` above `for blade, coef in mv.to_blade_dict().items():`; a bare
    `x: sympy.Symbol` per name above a `symbols(...)` unpack). Two limits: it does **not** reach a
    *comprehension*/genexpr loop var (separate scope — stays inferred); and if a name is reused
    across loops of different (sub)types, give each loop its **own** distinctly-named, typed variable.
  - **Don't fight the checker** — a locally-correct annotation that forces edits to unrelated logic
    or breaks flow-narrowing isn't worth it; leave it inferred and say why (e.g.
    `MultiVectorBase.__iter__`).
  - **Parameterize generics — never a bare generic** (`ComposableFunction[MultiVectorBase]`, not
    bare `ComposableFunction`; bare degrades the parameter to implicit `Any`). Invariance rules:
    `[Any]` for a polymorphic param that accepts any transform and applies it internally;
    `isinstance` checks and `MultiVectorFn` stay bare (documented exceptions).
  - **Read-only container params** take the covariant supertype (`Mapping`/`Sequence`), not
    invariant `dict`/`list`. **Polymorphic values** take the abstract base (`MultiVectorBase`).
  - **Inline a value used exactly once** takes precedence over "annotate generously" — don't keep a
    single-use local *only* to give it a type; inline it. Generous typing applies to the locals that
    *survive*.
- **Sibling (now complete) of the conditional-refactor sweep**
  (`tasks/archive/2026/09/05/refactor-conditionals-match-and-ternary-returns.md`; rules in
  `tasks/reference/conditional-refactoring-rules.md`) — the same discretionary code-quality-sweep
  discipline applies here: never churn what's already clear, protect what matters, per-batch
  `make test` + `make format` gate. That sweep already landed, so there's no edit-collision to
  coordinate; this one runs on top of it.
- **Scope excludes, hard:** the generated `src/gacalc/g1.py`/`g2.py`/`g3.py` (build artifacts — the
  generator owns their annotations; fix them in `tools/gen_specialized.py`/`astbuild.py`, never by
  hand) and the vendored `entrypoint/` Emacs tree (off-limits).
- **Verification reality:** `ty check src`, `ty check tests`, `ty check tools` are all currently
  **clean**, and `make format` is green. Any annotation added must keep all three clean. **Notebooks
  aren't in the `ty` gate** — verify their generics with `pyright` in the container (`make image`
  ships it), where host `ty` can't reach.

## Method (the audit)

1. **Enumerate the target files.** `src/gacalc/*.py` hand-written (`base.py`, `functions.py`,
   `transforms.py`, `frame.py`, `measure.py`, `vectorcalc.py`, `gn.py`, `nbplotutils.py`); `tools/*.py`
   (`gen_specialized.py`, `astbuild.py`, `bench.py`, `check_doc_regions.py`); and — if the maintainer
   wants them in scope (open question 1) — `tests/*.py` and `notebooks/*.py`.
2. **Per file, walk for these site classes** (each a catalog row: `file:line — name — proposed type —
   why`):
   - **Missing return annotation** on any `def` (incl. `-> None`).
   - **Missing param annotation** on any `def`.
   - **Unannotated local assignment** where a concrete type is knowable and not pure noise.
   - **Unannotated loop/unpack target** whose type is knowable → the "declare on the line above" form.
   - **Loosely-typed existing annotation** worth tightening: a bare generic
     (`ComposableFunction` → `[…]`), an `Any` that could be concrete, an invariant `dict`/`list`
     param that should be `Mapping`/`Sequence`, a concrete type where the abstract base belongs.
3. **Classify each row** `add | tighten | leave (with reason)`. The **leave-with-reason** rows matter
   most for review — the "don't fight the checker" / "inline single-use" / documented-bare-generic
   exceptions are the judgment calls.
4. **Produce the list** — grouped by file, most-impactful first (signatures before locals). This IS
   the deliverable. Keep it as a section in this task doc (or a `tasks/reference/` note if it grows
   large — decide once its length is known).
5. **Only after maintainer review**, apply in batches (per open question 2), each batch gated by
   `ty check src/tests/tools` + `make format` green, and the generated-module full-context ty run if
   anything under `tools/` changed how the generator annotates its output.

## Verification / done-state

- **Audit phase (this task's core):** a complete, file-grouped catalog of add/tighten/leave sites
  across the in-scope files, each row with file:line + proposed type + one-line reason.
- **Apply phase (gated, after review):** annotations added; `ty check src`, `ty check tests`,
  `ty check tools` all still clean; `make format` + `make test` green; notebook generics verified
  with `pyright` if notebooks were in scope. Generated `g*.py` untouched (annotations there come from
  the generator).

## Open questions — all RESOLVED 2026-09-05

1. ~~**Scope**~~ — **RESOLVED: all four** — `src/` + `tools/` + `tests/` + `notebooks/`, NOT `tasks/`
   ("all four, just not tasks").
2. ~~**List-only vs list-then-apply**~~ — **RESOLVED: apply them all** ("just do them all") — execute
   directly, gated per batch; not a list-only deliverable.
3. ~~**Additive only, or also tighten**~~ — **RESOLVED: everything** ("everything you can find") —
   add missing AND tighten loose generics / `Any` / invariant containers.
