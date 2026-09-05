# Conditional refactoring — when to reach for `match`, a ternary, a merge, or a phase-extraction

**Reference doc** — the worked-example backing for the five conditional-refactoring rules (A–E)
that live, lean, in `CLAUDE.md` › "Coding standard (Python)" › "(b) Judgment calls". Read the
`CLAUDE.md` bullets for the rules themselves; read this for the *why*, the real before/after code
from the `tools/gen_specialized.py` pilot, and the judgment calls (especially the leave-alones).
Written 2026-09-05 (William Emerison Six <billsix@gmail.com>). Origin task (archived):
`tasks/archive/2026/09/05/refactor-conditionals-match-and-ternary-returns.md`.

## The point

Not every conditional wants the same fix. Four distinct moves came out of the maintainer
discussion — plus one about *length*. In order of what to ask before touching a conditional:

1. **Rule A — ternary** a simple guard-value + fall-through-value into `X if cond else Y`.
2. **Rule B — dedup** identical branches *before* restructuring.
3. **Rule C — `match`** when the *pattern* does structural work (type / shape / literal / binding).
4. **Rule D — make it matchable** by extracting a literal discriminant first.
5. **Rule E — extract long dispatch bodies** into named nested functions so the dispatch reads as
   one unit.

The pilot was `tools/gen_specialized.py`. A generator refactor is behavior-preserving **by
definition**, so the hard gate throughout was: regenerate `src/gacalc/g1.py`/`g2.py`/`g3.py` and
prove them **byte-identical** before/after. Every change below passed that gate.

## Rule A — ternary `return X if cond else Y`

Collapse a guard-`if`-return plus a trailing fall-through return **only when ALL hold**: both `X`
and `Y` are single expressions (not multi-statement, no side effect between guard and return);
there are exactly two outcomes (not a chain); and the ternary reads at least as clearly as the
two-liner. **Do NOT** collapse a top-of-function early-exit *guard* (`if bad: raise` /
`return None` / `continue`) — that's the sanctioned cheap guard, and "don't churn existing
early-return code" governs. The distinction that matters: Rule A is for a guard that returns a
**real value** (one of two genuine outcomes); the early-exit exception is for a guard that bails
with an error/None/continue.

**Length is not a criterion.** `make format` wraps a long ternary into the parenthesized
multi-line form, so a would-be one-liner exceeding 88 cols is never a reason to leave a conditional
un-refactored — only *readability* and *outcome shape* decide (see `CLAUDE.md` › "(a)" › "Line
length is the formatter's job").

**Applied (blade naming + its inverse):**
```python
# before
def blade_label(blade):
    if blade == ():
        return "scalar"
    return "e_" + "".join(str(i) for i in blade)


# after
def blade_label(blade):
    return "scalar" if blade == () else "e_" + "".join(str(i) for i in blade)
```
```python
# before                                    # after
if label == "scalar":                       return () if label == "scalar" else tuple(
    return ()                                   int(c) for c in label[2:]
return tuple(int(c) for c in label[2:])     )
```
Both return a real value in each branch (`"scalar"` / `()`), so both are Rule-A cases, not
error-guards.

**Leave-alone (a guard whose fall-through does real multi-statement work):**
```python
member = getattr(MultiVectorBase, method_name, None)
doc = inspect.getdoc(member) if member is not None else None
if not doc:
    return []
body = "\n".join(f"{indent}{line}".rstrip() for line in doc.splitlines())
return [ast.Expr(value=constant(f"\n{body}\n{indent}"))]
```
The second outcome is a multi-statement build (`body = …` then a `return`), so Rule A's
"both are single expressions" fails. `if not doc: return []` is a clean guard — leave it.

**Leave-alone (NOT a two-outcome shape — the real reason to leave, now that length is a non-issue):**
- `ComposableFunction.at` — three outcomes (`interpolate` / `components` / fall-through), a guard
  *cascade*, not a 2-way; its fall-through is already a ternary. Rule A is exactly-two-outcomes.
- `astbuild.cast_coef` — three guards (`Name`/`Attribute`, negated field, `field**const`) that all
  `return value`, then a `cast` fallback. OR-ing three multi-part `isinstance` conditions into one
  ternary reads *worse* than the cascade, so it stays. (A dedup-style merge — "if it's already a
  `Coef` in any of these shapes, don't cast" — is the only refactor worth considering here, and it
  buries three distinct, separately-commented shape checks.)

## Rule B — dedup before you restructure

Before converting any conditional, check whether two or more branches produce *identical* code. If
so, **merge them** — the answer is neither `match` nor ternary. Watch for **vestigial** splits:
branches that used to differ (e.g. one carried a now-removed `cast`) and collapsed to identical
bodies, kept apart only by their comments. Merging deletes the dead discriminating test.

**Applied (`result_block_stmts`' three-way chain whose last two arms were identical):**
```python
# before
if via_var is not None:
    stmts.append(return_stmt(cast(construct_type_of(via_var, pairs))))
elif owner is not None and owner == result_spec.name and cast is cast_self:
    # Same-type result. Every value type is now @typing.final ...
    stmts.append(return_stmt(construct(result_spec.name, pairs)))
else:
    # grade-changing arm ... the old cast(Self, Rotor(...)) was unsound.
    stmts.append(return_stmt(construct(result_spec.name, pairs)))

# after
if via_var is not None:
    stmts.append(return_stmt(cast(construct_type_of(via_var, pairs))))
else:
    # Same-type OR grade-changing: both construct the concrete @typing.final result
    # type directly.  Same-type has no subclass to preserve via type(self);
    # grade-changing returns MultiVectorBase, so no cast (the old cast(Self, ...)
    # was unsound).  Every value type -- graded, scalar, and the full G_n -- is now
    # final, so the two arms coincide.
    stmts.append(return_stmt(construct(result_spec.name, pairs)))
```
The whole `owner is not None and owner == result_spec.name and cast is cast_self` test is now dead
weight — deleted. The two former comments are merged into one that explains *why* the arms coincide.

**Leave-alone (the deceptively-similar sibling in `unary_stmt`):**
```python
if owner is not None and owner == result_spec.name:
    # same-type result -> the concrete (now-final) class, no type(self) needed
    return return_stmt(construct(result_spec.name, pairs))
return return_stmt(cast(construct(result_spec.name, pairs)))
```
This looks like the same vestigial split but is a **live** distinction: the guard branch builds
*without* a cast, the fall-through *with* `cast(...)`. Rule B needs genuinely identical branches;
these differ. And it's a poor ternary too — the comment explains a non-obvious same-type
optimization that wants a home. Leave it. (The lesson: verify the branches are byte-identical
before merging; a `cast`/no-`cast` difference is exactly the kind of live distinction that hides
behind similar-looking code.)

## Rule C — `match` earns its keep by *structural work in the pattern*

Convert an `if`/`elif` chain to `match` + `case _` when the **pattern column does real work**, even
if a boolean guard then refines the arm: type dispatch (`case int() | float():`), destructuring
that binds names the body/guard uses (`case (a, c, *rest) if a == c:` — better than manual
`blade[0]`/`blade[1]`), or literal dispatch (`case "a":`, `case () | (_,):`).

**The anti-pattern is narrower than "has a guard":** it's only when the patterns do *no*
structural work — every arm is `case _ if <bool>` (a bare wildcard + guard), or binds a name it
never uses. Then the pattern column is dead and only the guards discriminate — that's `if`/`elif`
in `match` syntax. **The test:** strip the guards, keep only the patterns — do they still
meaningfully dispatch (by type / shape / literal / binding)? Yes → `match`. All `_` → `if`/`elif`.

The pilot needed no *pure* Rule-C conversion (its chain went through Rule D, which *produces* a
Rule-C-worthy `match`), but the project-wide sweep found two clean ones:

**Applied (literal dispatch — `transforms.to_matrix`):**
```python
# before: an open-ended if-chain + trailing raise    # after
if backend == "sympy":                                match backend:
    return sympy.Matrix.hstack(...)                       case "sympy":
if backend == "numpy":                                        return sympy.Matrix.hstack(...)
    return np.column_stack(...)                          case "numpy":
raise ValueError(f"unknown backend {backend!r}")             return np.column_stack(...)
                                                         case _:
                                                             raise ValueError(...)
```

**Applied (type dispatch — `base._coerce`):**
```python
# before                                     # after
if isinstance(x, MultiVectorBase):           match x:
    return cls.from_blade_dict(...)               case MultiVectorBase():
if isinstance(x, sympy.Expr):                         return cls.from_blade_dict(...)
    return cls.from_coef(x)                       case sympy.Expr():
return cls.from_scalar(x)                             return cls.from_coef(x)
                                                  case _:  # scalar
                                                      return cls.from_scalar(x)
```
Both replace a fall-through (a bare `raise`, a bare `return`) with an explicit `case _` that names
the default. The pilot already uses good structural `match`es too: `Gn._geometric_product`'s
`decrease_grade`, `base.reject`/`reflect`.

**Leave-alone (two-branch type dispatch — Rule C's own caveat):** `transforms.rotor_for`'s
`if isinstance(theta, sympy.Expr): … else: …` stays as an `if`/`else` — a *binary* type test is the
case "don't convert every two-branch conditional" covers, and its branches are multi-statement
(each assigns `cos_half`/`sin_half`/`plane_i`), so it's not a ternary either. `match` earns its keep
at ≥3 arms or where exhaustiveness genuinely matters. (Contrast `base.__truediv__`, also a binary
`isinstance`: its branches are single `return` expressions, so it became a Rule-A *ternary*, not a
`match` — the two-branch-leave-alone is about `match`, not about ternaries.)

## Rule D — make a boolean/prefix/attribute check matchable

`if name.startswith("a_"): … elif name.startswith("b_"):` is **not** structural as written (a
`case s if s.startswith("a_")` would be the Rule-C anti-pattern). But it *becomes* a clean `match`
after you extract a **literal-matchable discriminant** first (and usually hoist duplicated setup —
so Rule D often pairs with Rule B).

**Applied (`term_grade_key`'s operand-symbol dispatch; both arms recomputed `blade`):**
```python
# before
if sym.name.startswith("a_"):
    blade = blade_of_label(sym.name[2:])
    left = (len(blade), blade)
elif sym.name.startswith("b_"):
    blade = blade_of_label(sym.name[2:])
    right = (len(blade), blade)

# after
kind, _, label = sym.name.partition("_")
blade = blade_of_label(label)  # hoisted out of both arms (Rule B)
match kind:
    case "a":
        left = (len(blade), blade)
    case "b":
        right = (len(blade), blade)
    case _:
        raise ValueError(f"unexpected operand symbol {sym.name!r}")
```
The `case _: raise` documents the invariant ("only `a_`/`b_` operand symbols exist") even though it
can't fire today — the "always write the default branch" rule paying off. Note the behavior nuance:
the old chain *silently ignored* a non-`a_`/`b_` symbol; the new `case _` *raises*. That's a
deliberate tightening — the byte-identical generated output proves it never fires on real input,
and if the generator ever grows a `cse` temporary with a different prefix, the raise catches it
loudly instead of miscomputing a sort key.

## Rule E — extract *long* dispatch branch-bodies into named nested functions

The "don't extract a single-use block **only** to reshape control flow" rule targets **short**
gratuitous extractions. It does **not** forbid — and the "name a distinct phase" / "nest when it
closes over the enclosing parameters" clauses **positively favor** — extracting a **long** branch
body in a multi-way dispatch into a **named nested function**.

At length the extraction changes kind. A long `if`/`elif` ladder **interleaves the table of
contents (the conditions) with the chapters (the bodies)**, so you can't see the decision as a
unit. Extracting the bodies to named functions separates them — the dispatch becomes a clean table
of contents you can hold in your head, each chapter read by name only when needed.

- **Heuristic:** ≥3 arms AND bodies long enough that the conditions don't fit on one screen (or any
  single body past ~15–20 lines) → extract.
- **Nest, don't hoist** to module scope — the bodies close over enclosing locals; nested functions
  capture them, module-level would need a pile of params.
- **Return, don't mutate (decided 2026-09-05).** Each extracted phase **builds and returns its own
  list**; the dispatch appends the result (`body += bivector_extras()`). The inner function then
  **reads** the enclosing scope freely but **never writes** to it — the enclosing `body` list has a
  single owner. The maintainer's rule, in their words: *"I'm much more fine with the inner function
  reading variables outside of its scope than writing to them."* The mutate-via-closure alternative
  (each phase does `body.append(...)` on the outer list) was prototyped and **rejected** for exactly
  this reason — it reads as a tiny diff but gives every phase a hidden side effect on a shared list.

**Applied (`generate_graded_type`'s per-grade special-case injections):** a run of long, independent
blocks — `Bivector` (exp + `.i()`), `Rotor` (plane_of_rotation + sandwich + `.i()`), `Odd_3`
(to_vector/to_trivector casts), `Vector` (project/reject/reflect overrides + factory narrowings +
the 𝒢₃ cross) — each well past a screen, so the dispatch structure was invisible.
```python
# before (the shape, abbreviated) -- conditions and bodies interleaved:
if spec.name.startswith("Bivector"):
    body.append( ...exp... )              # ~30 lines
    body.append(i_extractor("normalize", "Bivector"))
if spec.name.startswith("Rotor"):
    body.append( ...plane_of_rotation... )   # ~40 lines
    ...
if spec.name == "Odd_3":
    for cast_name, ... : body.append( ...cast... )  # ~60 lines
if spec.name.startswith("Vector"):
    body.extend( ...project/reject/reflect/cross... )  # ~130 lines

# after -- each phase a named pure builder, the dispatch a table of contents:
def bivector_extras() -> list[ast.stmt]:
    extras: list[ast.stmt] = []
    extras.append( ...exp... )
    extras.append(i_extractor("normalize", "Bivector"))
    return extras

def rotor_extras() -> list[ast.stmt]: ...
def odd3_extras() -> list[ast.stmt]: ...
def vector_extras() -> list[ast.stmt]: ...

match spec.name:
    case "Bivector": body += bivector_extras()
    case "Rotor":    body += rotor_extras()
    case "Odd_3":    body += odd3_extras()
    case "Vector":   body += vector_extras()
    case _:
        # grade-pure types with no extras (Trivector, Scalar, higher KVectors)
        pass
```
The `startswith` was vestigial (names are exact) → literal `case`s. The `case _: pass` names the
"grade-pure, no extras" set explicitly. Generated output: byte-identical. Cost: +12 lines (the four
`extras = []` / `return extras` pairs) — paid to buy a dispatch you can read as one unit and four
phases you can read, call, or test in isolation.

## The shape to copy

Bulk-fix the clear cases, vary the mechanism (ternary / merge / match / extract — not one blunt
tool), protect what matters (the live `cast`/no-cast distinction, the multi-statement guard, the
genuine non-two-way shapes like `at` and `cast_coef`), and surface the judgment calls — the
**leave-alones** are the review-worthy part. And for a generator, the byte-identical gate is what lets you refactor
control flow fearlessly: an empty diff IS the proof nothing changed.
