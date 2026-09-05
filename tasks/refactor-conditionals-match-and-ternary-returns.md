# Refactor conditionals: `match` / ternary-return / dedup / phase-extraction — rules + a project sweep

**Status:** proposed — rules drafted with maintainer 2026-09-05; Cases 1 & 2 decided, Case 3 is
prototype-and-show; needs go-ahead to execute (William Emerison Six <billsix@gmail.com>)
**Priority:** 5
**Difficulty:** 4

## BLUF

Improve control-flow readability in `tools/gen_specialized.py` first (the pilot), **derive a small set
of when-to-apply rules from doing it, codify them in `CLAUDE.md`, then apply project-wide** — all at
discretion, never churning code that's already clear. Four distinct moves came out of the maintainer
discussion (they are NOT all "if→match"): **(A)** collapse simple guard+fallthrough to a **ternary
return**; **(B)** **merge duplicate branches** before restructuring; **(C)** use **`match`** when the
*pattern* does structural work; **(D)** turn a boolean/prefix check into a `match` by first extracting
a **literal-matchable discriminant**; **(E)** extract **long** dispatch branch-bodies into **named
nested functions** so the dispatch reads as one unit. A generator refactor is behavior-preserving by
definition, so the hard gate is: **regenerate before/after and prove the `g*.py` are byte-identical.**

## Context — read first (this is cold-start; assume none of the discussion is in memory)

- **This refines, doesn't replace, existing `CLAUDE.md` conventions.** Under "(b) Judgment calls" the
  repo already says: **"Prefer expressions"**; **"Prefer `match` + `case _` over an open-ended
  `if`/`elif` chain, for exhaustiveness"** with the caveat that "a `match` whose every case is a
  boolean guard is an `if`/`elif` in different syntax — don't convert every two-branch conditional";
  and **"What earns an extraction: duplication, or naming a phase — not reshaping control flow …
  Neither when the helper would be used exactly once and exists *only* to reshape control flow."** The
  rules below sharpen the match line, add the missing ternary-return and dedup rules, and add the
  *length* nuance to the extraction rule. Read that section of `CLAUDE.md` before editing it.
- **Behavior-preservation gate.** The generator's output (`src/gacalc/g1.py`/`g2.py`/`g3.py`, and
  g4/g5 when generating them) must be **byte-identical** before and after every generator edit — it's
  a style change, not behavior. Mechanically: materialize the generated tree (it's gitignored),
  refactor, regenerate, `diff`. `make check-generated` (regenerates twice, asserts byte-stable) plus a
  git-diff of the materialized tree are the tools. This is the "prove a refactor changed nothing"
  discipline; an empty diff IS the proof.
- **The full gate** after any change: `make test` (441 tests) + `make format` (ruff + `ty`). The
  generated-module ty check needs the full-context form (the dev gate skips gitignored g*.py) — see
  `CLAUDE.md` › Dev workflow for the exact `ty check src/gacalc/g1.py … transforms.py` full-context line.

## THE RULES (draft — refine while doing the pilot; this text is what goes into `CLAUDE.md`)

**Before reaching for `match` or a ternary, ask in this order:**

### Rule A — Ternary `return X if cond else Y`
Collapse a guard-`if`-return plus a trailing fall-through return **only when ALL hold:**
- both `X` and `Y` are **single, short expressions** (comfortably ≤88 cols; no multi-statement branch,
  no side effect between guard and return);
- there are **exactly two** outcomes (one guard + the fall-through), not a chain;
- the one-liner **reads at least as clearly** as the two-liner.

**Do NOT** collapse a **top-of-function early-exit guard** (`if bad: raise` / `return None` /
`continue`) — that's the sanctioned cheap guard, and "don't churn existing early-return code" governs.

*Motivating example* (blade naming, `gen_specialized.py`):
```python
if blade == ():
    return "scalar"
return "e_" + "".join(str(i) for i in blade)
```
→ `return "scalar" if blade == () else "e_" + "".join(str(i) for i in blade)`

### Rule B — Dedup before you restructure
**Before converting any conditional, check whether two or more branches produce *identical* code.** If
so, **merge them** — the answer is neither `match` nor ternary. Watch for *vestigial* splits: branches
that used to differ (e.g. one carried a now-removed `cast`) and collapsed to identical bodies, kept
apart only by their comments. Merging deletes the dead discriminating test. (See Case 2.)

### Rule C — `match` earns its keep by *structural work in the pattern*
Convert an `if`/`elif` chain to `match` + `case _` when the **pattern column does real work**, even if
a boolean guard then refines the arm:
- **type dispatch** — `case int() | float():`, `case MultiVectorBase():`;
- **destructuring that binds names** the body/guard uses — `case (a, c, *rest) if a == c:` (this is a
  *good* `match`: the guard on destructured names reads better than manual `blade[0]`/`blade[1]`
  indexing);
- **literal dispatch** — `case "a":`, `case ():`, `case () | (_,):`.

**The anti-pattern (leave as `if`/`elif`, or add a plain final `else`) is narrower than "has a
guard":** it's only when the patterns do **no** structural work — every arm is `case _ if <bool>` (a
bare wildcard + guard), or binds a name it never uses. Then the pattern column is dead and only the
guards discriminate — that's `if`/`elif` in `match` syntax.

**The test:** *strip the guards and keep only the patterns — do they still meaningfully dispatch (by
type / shape / literal / binding)?* Yes → `match`. All `_` → `if`/`elif`.

### Rule D — make a boolean/prefix/attribute check matchable
A check like `if name.startswith("a_"): … elif name.startswith("b_"):` is **not** structural as
written (a `case s if s.startswith("a_")` would be the Rule-C anti-pattern). But it often *becomes* a
clean `match` after you **extract a literal-matchable discriminant first** (and usually hoist any
duplicated setup):
```python
kind, _, label = name.partition("_")
blade = blade_of_label(label)           # was duplicated in both arms
match kind:
    case "a": ...
    case "b": ...
    case _:   raise ValueError(f"unexpected operand symbol {name!r}")
```
The `case _: raise` documents the invariant ("only a_/b_ exist") even though it can't fire — the
"always write the default branch" rule paying off. (See Case 1.)

### Rule E — extract *long* dispatch branch-bodies into named nested functions
The "don't extract a single-use block **only** to reshape control flow" rule targets **short**
gratuitous extractions. It does **not** forbid — and the "name a distinct phase" / "nest when it
closes over the enclosing parameters" clauses **positively favor** — extracting a **long** branch body
in a multi-way dispatch into a **named nested function.** At length the extraction changes kind: a long
`if`/`elif` ladder **interleaves the table of contents (the conditions) with the chapters (the
bodies)**, so you can't see the decision as a unit; extracting the bodies to named functions separates
them — the dispatch becomes a clean table of contents you can hold in your head, each chapter read by
name only when needed.
- **Heuristic:** when a multi-way dispatch has **≥3 arms AND** the bodies are long enough that the
  conditions don't fit on one screen (or any single body runs past ~15–20 lines) → extract.
- **Nest, don't hoist** to module scope — the bodies close over enclosing locals; nested functions
  capture them, module-level would need a pile of params (the coupling the rule rightly warns about).
- **Guardrail:** two short branches stay inline; that's what Rules A/plain-`if` are for. The name each
  extracted function gets is itself documentation of what that branch does.

## The specific cases in `gen_specialized.py` (decided + one to prototype)

### Case 1 — the `a_`/`b_` operand-symbol dispatch — DECIDED: do it (Rules D + B)
`gen_specialized.py:275-282` (the `for sym in term.free_symbols` loop that builds the product-key):
```python
        if sym.name.startswith("a_"):
            blade = blade_of_label(sym.name[2:])
            left = (len(blade), blade)
        elif sym.name.startswith("b_"):
            blade = blade_of_label(sym.name[2:])
            right = (len(blade), blade)
```
**Both arms recompute `blade`.** Hoist it and dispatch on the literal prefix with an exhaustive raise:
```python
        kind, _, label = sym.name.partition("_")
        blade = blade_of_label(label)
        match kind:
            case "a":
                left = (len(blade), blade)
            case "b":
                right = (len(blade), blade)
            case _:
                raise ValueError(f"unexpected operand symbol {sym.name!r}")
```
Keep the `if not isinstance(sym, sympy.Symbol): continue` filter above as-is (a clean guard-continue).

### Case 2 — the `via_var` / `owner` / `else` chain — DECIDED: merge (Rule B), NOT a match
`gen_specialized.py:1328-1340`:
```python
    if via_var is not None:
        stmts.append(return_stmt(cast(construct_type_of(via_var, pairs))))
    elif owner is not None and owner == result_spec.name and cast is cast_self:
        # Same-type result. Every value type is now @typing.final ...
        stmts.append(return_stmt(construct(result_spec.name, pairs)))
    else:
        # grade-changing arm ... the old cast(Self, Rotor(...)) was unsound.
        stmts.append(return_stmt(construct(result_spec.name, pairs)))
    return stmts
```
The `elif` and `else` bodies are **byte-identical** (`construct(result_spec.name, pairs)`) — a
vestigial split (they used to carry a now-removed cast), kept apart only by comments. **Merge them,
deleting the whole `owner is not None and owner == result_spec.name and cast is cast_self` test:**
```python
    if via_var is not None:
        stmts.append(return_stmt(cast(construct_type_of(via_var, pairs))))
    else:
        # same-type OR grade-changing: both construct the concrete @typing.final result
        # type directly -- no subclass to preserve, and grade-changing returns
        # MultiVectorBase so no cast (the old cast(Self, ...) was unsound).
        stmts.append(return_stmt(construct(result_spec.name, pairs)))
    return stmts
```
`match` is *worse* here (a `None`-check reads fine as `if`). **Also check** the similar
`if owner is not None and owner == result_spec.name:` at `gen_specialized.py:1361` (a *different*
function) — determine whether it's the same vestigial split or a live distinction; apply Rule B only
if its branches are genuinely identical.

### Case 3 — the `if spec.name.startswith("Bivector"): …` special-case chain — PROTOTYPE-AND-SHOW
In `generate_graded_type` the per-type injections are a run of long, independent blocks:
`gen_specialized.py:3043` `startswith("Bivector")` (exp + `.i()`), `:3073` `startswith("Rotor")`
(plane_of_rotation + sandwich + `.i()`), `:3115` `== "Odd_3"` (to_vector/to_trivector),
`:3177` `startswith("Vector")` (project/reject/reflect overrides + coordinate props). The bodies are
long (the chain runs well past a screen), so the **dispatch structure is invisible** — the exact
Rule-E situation.

**Do NOT just apply it — prototype it and show the maintainer both versions.** Steps:
1. Extract each block's body into a **named nested function** inside `generate_graded_type`
   (`bivector_extras()`, `rotor_extras()`, `odd3_extras()`, `vector_extras()`), each closing over the
   enclosing locals (`spec`, `n`, `full_name`, `mvb_ann`, …) and **returning the list of nodes to
   append** (don't mutate `body` inside — return, so each reads as a pure phase).
2. Replace the chain with a dispatch — a `match spec.name:` (names are exact, so `case "Bivector":`
   etc.; `startswith` is vestigial) with a `case _: pass` documenting "grade-pure types with no extras
   (Trivector, Scalar, higher `KVector`s)". (Or a dict-dispatch if that reads cleaner — note the
   option; `match` is preferred for explicit visibility.)
3. **Show the maintainer the before/after diff** — the current chain vs. the extracted-and-dispatched
   version — so the "the table of contents now fits on one screen" claim can be *seen*, not taken on
   faith. **Get the go/no-go before baking Rule E's Case-3 verdict into `CLAUDE.md`.**
4. If accepted: verify byte-identical generated output (the injections must emit the same nodes).

## Work plan

1. **Read** `CLAUDE.md` "(b) Judgment calls" and this file's rules. Materialize the generated tree
   (`make generate`) and snapshot it (copy `src/gacalc/g1.py g2.py g3.py` aside) as the byte-identical
   baseline.
2. **Case 1 & Case 2** — apply the decided fixes (above). Also handle the `:1361` sibling of Case 2 per
   Rule B if identical.
3. **Case 3** — prototype per the four steps; **stop and show the maintainer** the before/after.
4. **Catalog** the remaining `if`s in `gen_specialized.py` + `astbuild.py` into
   {ternary / merge / match / extract / leave-alone} with a one-line reason each — that catalog is the
   evidence the rules are right; apply the clear ones at discretion.
5. **Prove nothing changed:** regenerate, `diff` against the snapshot → **byte-identical**;
   `make check-generated`; `make test`; `make format` — all green.
6. **Codify the rules in `CLAUDE.md`** — fold Rules A–E into "(b) Judgment calls," lean, beside the
   existing "Prefer expressions" / "Prefer `match`" / "What earns an extraction" bullets. Keep the
   table-of-contents-vs-chapters framing for E (it's the memorable part). If the worked examples run
   long, put them in a `tasks/reference/` note and point to it. Only bake Case-3's Rule E after the
   maintainer OK'd the prototype.
7. **Apply project-wide**, file by file, same discretion: `src/gacalc/*.py` hand-written
   (`base.py`, `functions.py`, `transforms.py`, `frame.py`, `measure.py`, `vectorcalc.py`, `gn.py`,
   `nbplotutils.py`), `tests/*.py`, `notebooks/*.py`, `tools/*.py`. **NEVER** the generated `g*.py`
   (build artifacts — the generator owns them) or the vendored `entrypoint/` Emacs tree. Verify per
   batch (`make test` + `make format` green).
8. **Report the exceptions** briefly: bulk changes made, and the notable **leave-alones** (where the
   "obvious" change would have hurt readability) — the judgment calls are the review-worthy part.

## Verification / done-state

- Cases 1 & 2 applied; Case 3 prototyped and maintainer-decided; the remaining `gen_specialized`/
  `astbuild` `if`s catalogued and the clear ones applied.
- **Generated `g*.py` byte-identical** before/after (proven, not assumed); `make check-generated`,
  `make test`, `make format` all green.
- `CLAUDE.md` carries Rules A–E (lean).
- Project-wide sweep applied with discretion; per-batch gate green; a short report of bulk changes +
  notable leave-alones.

## Open questions

1. **Case 3 go/no-go** — pending the prototype (step 3). If the extracted-and-dispatched version reads
   better, Rule E's long-body verdict is confirmed and Case 3 lands; if not, Case 3 stays inline and
   Rule E is scoped to "consider, don't mandate."
2. **Worked examples: inline in `CLAUDE.md` vs a `tasks/reference/` note** — keep `CLAUDE.md` lean;
   decide once the rule text's length is known.
