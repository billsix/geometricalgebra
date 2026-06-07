# Investigate rewriting the code generation to use the Python `ast` module

**Status:** complete — A/B/C all built and verified; **C chosen and committed** as the approach (the
generator builds via hand-built `ast` nodes). Post-pick cleanup done: `tools/_ast_parity.py` deleted,
CLAUDE.md "Code generation" refreshed. Structure follow-up tracked separately in
`tasks/gen-specialized-structure-refactor.md` (also done bar optional #6). Acceptance met:
AST-equivalent (`ast.dump` per file) + 161 tests + deterministic; run-to-run byte-stability guarded by
`make check-generated`.
**Started:** 2026-06-07
**Completed:** 2026-06-07

---

## TL;DR / summary so far (2026-06-07)

The question — *can the codegen use Python `ast` instead of string concatenation, still derived from
`gn.py`?* — is answered **yes**, and is delivered as three committed, individually-complete alternatives
for the author to choose between (each `git reset --hard`-able):

- **A (committed).** Minimal: regex rename → `SymbolToAttr` NodeTransformer; module assembly + emission
  → `ast.unparse`. Method bodies still `lines.append("...")` text, then parsed. Fragile regex gone;
  everything flows through `ast`.
- **B (committed).** Full template-splice: every emitter is a triple-quoted `$`-template (`fill` =
  `string.Template`), dynamic per-blade lists built as small snippets; **zero `lines.append`**. The
  "write code as code, splice the holes" / quasiquote feel. Recommended for the stated motivation.
- **C (next).** Hand-built `ast` nodes — no source text for bodies. Maximal purity; expected to be the
  most verbose / least readable (built as the honest comparison point).

Invariants that held across A and B and must hold for C: parity harness **ALL EQUIVALENT** (all 4 files
`ast.dump`-identical to the original string baseline), `make check-generated` deterministic, full suite
**161 passed**, `ruff`/`ty` clean. The file header (copyright + imports) stays **raw text** in every
level — comments cannot live in an AST.

Decisions locked: **full rewrite**; acceptance = **AST-equivalent + suite-green** (not byte-identical to
old); **readability loss of the generated files is accepted** (ruff formats the output anyway).

## Goal

Determine whether `tools/gen_specialized.py` can produce the specialized `g1/g2/g3.py` + `scalar.py`
via the Python **`ast`** module (build syntax-tree nodes → `ast.unparse`) instead of today's raw
string concatenation, while **still deriving everything from `gn.py`'s symbolic ops**. Author's
motivation: as a Lisp programmer, manipulating code as data (macros) is more natural than string
mashing, and `ast` looks like Python's closest analogue. Deliverable: feasibility + tradeoffs (this
doc); **on go**, implement it and prove the generated code is equivalent to the string-concat output.

## How the generator works today (studied 2026-06-07)

There are **two distinct layers**, and they're very different from an AST standpoint:

1. **The math expressions** (the actual closed forms). These are *already* generated, not hand-mashed:
   - Run the symbolic op in `Gn` (`a_mv * b_mv`, `.inner_product`, `.outer_product`) where the operands
     are `Gn` built from sympy `Symbol`s `a_e_1`, `b_e_12`, … (`generate_class`, lines ~548-563).
   - `sympy.cse(out_exprs)` factors common subexpressions.
   - `render(expr)` = `sympy.sstr(expr)` then a **regex** that rewrites `a_e_1 → self.e_1`,
     `b_e_12 → rhs.e_12` (lines ~551-560). So the expression *text* comes from sympy's printer; the
     only bespoke bit is the symbol→attribute rename, done with a word-boundary regex.
   - `format_assignment` re-orders additive terms by grade (`term_grade_key`) and hand-wraps long sums
     at 88 cols.

2. **The structural scaffolding** (the bulk, ~1100 lines). Raw `lines.append(f"...")`: the
   `@dataclass`, class/field defs, `from_blade_dict`/`to_blade_dict`, `__eq__`, the bilinear methods'
   isinstance-dispatch + cse temporaries + constructor, `emit_structural`'s linear/grade/compare
   methods, the graded-subtype `match` dispatch (`generate_graded_type`), `scalar.py`, the basis
   constants, and the file `header()`/`SCALAR_HEADER` (copyright + imports, as big raw strings).
   Docstrings are copied verbatim from `AbstractMultiVector` via `inspect.getdoc` (`emit_docstring`).

Idempotent + deterministic (guarded by `make check-generated`); ruff-formatted as the last step.

## What I learned about `ast` (research 2026-06-07)

- **`ast.unparse(tree)`** (Python 3.9+; we require ≥3.13, so always available) turns an AST back into
  *valid* source — "code that would parse to an equivalent AST." You build nodes
  (`ast.ClassDef`, `ast.FunctionDef`, `ast.Assign`, `ast.Return`, `ast.BinOp`, `ast.Attribute`,
  `ast.Call`, `ast.Constant`, …), then `ast.unparse(ast.fix_missing_locations(tree))`.
  `fix_missing_locations` fills the `lineno`/`col_offset` every node needs.
- **AST is intentionally lossy — it has no comment nodes and discards formatting.** `ast.unparse`
  emits canonical formatting and **drops all comments**; it does *not* wrap at 88 cols or preserve
  blank lines. Docstrings *survive* (they're ordinary string-`Expr` statements). (Confirmed across the
  Python docs and multiple write-ups below.)
- **Building nodes by hand is verbose** — `ast` has no quasiquote/backquote. The ergonomic
  middle-ground is **template-splice**: `ast.parse("self.X")` a snippet, then an `ast.NodeTransformer`
  to fill the holes — the nearest thing to Lisp `(backquote … ,hole)` in the stdlib.
- **3.13** tightened node-construction validation, so malformed trees fail fast.
- **`libcst`** (Instagram) is the format/comment-preserving *concrete* syntax tree — the right tool for
  *codemods* (transforming existing files losslessly), but a heavier third-party dep and overkill for
  *greenfield* generation like ours (we emit from scratch, not edit existing source).

## Feasibility: yes, with one important caveat about "the same output"

**Technically feasible — both layers map onto `ast`:**

- *Scaffolding* → build `ClassDef`/`FunctionDef`/`Assign`/`Return`/`If`/`Match` nodes. The trailing-comma /
  indentation / line-wrapping bookkeeping that the string version does by hand disappears (unparse +
  ruff handle it).
- *Math* → two clean options: (a) keep sympy's printer but feed its output through
  `ast.parse(sympy.sstr(expr), mode="eval")`, **then replace the regex rename with an
  `ast.NodeTransformer`** that turns `Name('a_e_1')` into `Attribute(Name('self'), 'e_1')` — strictly
  more correct than a regex on text; or (b) sympy `pycode`→`ast.parse`. The cse temporaries become
  `Assign` nodes.

**The caveat (this is the crux of the "ensure the generated code is the same" requirement):**
`ast.unparse` produces **canonical** source — no comments, its own parenthesization/wrapping, and it
will not reproduce the current hand-tuned, grade-ordered, 88-col-wrapped, commented layout. After a
ruff pass the two still won't be **byte-identical**. So "the generated output is the same" cannot mean
*textually* identical. It must be redefined as **equivalent**, verified two ways:

1. **AST-equivalence:** for each file, `ast.dump(ast.parse(old)) == ast.dump(ast.parse(new))`
   (optionally normalize both via `ast.unparse(ast.parse(x))` first). This proves *same statements,
   same expressions* — formatting and comments aside. **Caveat:** additive-term order is part of the
   AST (operand order in `BinOp`), so the AST builder must reproduce `term_grade_key` ordering, else
   the dumps differ. Non-docstring comments (there are essentially none in method bodies today; the
   commentful parts are the raw `header()`/`SCALAR_HEADER`, which we'd keep as raw text prepended to
   the unparsed body) won't appear in the AST and so won't block equivalence.
2. **Behavioural parity:** full `pytest` (incl. `--doctest-modules` + the conformance suite that runs
   `[Gn, G1, G2, G3]` through the same operations) stays green, and `make check-generated`
   (regenerate-twice determinism) holds.

If the author truly wants **byte-identical**, the only honest path is to accept a **one-time
re-baseline**: regenerate the committed files with the AST generator and treat *that* (ruff-formatted)
as the new canonical output; `make check-generated` then guards it going forward. (We can't have both
"byte-identical to the current hand-tuned text" *and* "produced by `ast.unparse`.")

## Tradeoffs

**Gains**
- **Correct-by-construction:** no fragile regex rename; `unparse` can't emit syntactically invalid code;
  3.13 validates nodes. Adding/changing a method becomes a tree edit, not comma/indent string
  bookkeeping.
- **Macro-like ergonomics** (the author's actual want): code-as-data; template-splice ≈ quasiquote.
- **Less incidental string logic:** `format_assignment`'s manual 88-col wrapping and trailing-comma
  handling go away (ruff owns formatting).

**Costs**
- **Byte-identical output is lost** (see caveat) — the carefully hand-wrapped, grade-ordered, lightly
  annotated current output is replaced by `unparse`+ruff canonical form. Acceptance must shift to
  AST-equivalence + suite parity (or a one-time re-baseline).
- **`ast` is verbose** — no quasiquote in the stdlib; hand-built `Call(func=Attribute(...), args=[...],
  keywords=[...])` trees are wordier than f-strings (and than Lisp macros). Template-splice mitigates
  but adds its own indirection.
- **The math layer barely benefits** — it's *already* sympy-generated; the only real win there is
  swapping the regex for a NodeTransformer. The big rewrite is the scaffolding, whose payoff is mostly
  conceptual cleanliness.
- **Effort + risk:** ~1300 lines reworked. The conformance suite de-risks behaviour, but it's real
  work, and `ast.unparse` quirks (e.g. parenthesization of nested `BinOp`, `Constant` for negative
  numbers) need shaking out.
- **Docstrings/headers** still handled specially (string-`Expr` injection; raw header prepend).

## Options (pick one if "go")

1. **Hybrid / minimal (recommended first step).** Keep the string scaffolding; replace *only* the
   regex rename in the math layer with `ast.parse` + a `NodeTransformer` (symbol→attribute) +
   `ast.unparse` of each expression. Kills the one genuinely fragile, regex-on-source part; tiny
   surface; output stays essentially the same (just the expression text, which sympy already
   controls). Highest robustness-per-effort. Could also adopt template-splice for a few method bodies.
2. **Full `ast` rewrite.** Build every module as an AST and `unparse` it. Maximes the macro feel and
   removes all string bookkeeping, at the cost of the byte-identical output and a large rewrite.
   Acceptance = AST-equivalence + suite parity (or re-baseline).
3. **`libcst`.** Not recommended here — its strength is lossless *transformation* of existing files;
   for greenfield generation it's a heavier dep without a matching payoff. Note it only if format/comment
   preservation becomes a hard requirement.

## Plan if "go" (proposed — adjust per chosen option)

- [ ] Confirm the option (1 hybrid / 2 full) and the acceptance definition (AST-equivalence + suite, vs
      byte-identical re-baseline).
- [ ] Build a **parity harness** first: a script that runs the *current* generator and the *new* one
      into temp dirs and asserts per-file `ast.dump(ast.parse(...))` equality (normalized), plus runs
      `pytest -q`. This is the safety net the whole rewrite leans on.
- [ ] Implement incrementally, smallest scope first (the rename transform), re-running the harness at
      each step; for the full rewrite, convert one emitter at a time (`emit_bilinear`, then
      `emit_structural`, then `generate_graded_type`, then `scalar`, then constants/header).
- [ ] Reproduce `term_grade_key` ordering in `BinOp` construction so AST dumps match.
- [ ] Keep `header()`/`SCALAR_HEADER` (copyright + imports + comments) as raw prepended text — comments
      can't live in the AST.
- [ ] Final gates: `make check-generated` (determinism), full `pytest` (incl. conformance + doctests),
      `ruff`/`ty` clean. Update CLAUDE.md "Code generation" to describe the AST approach.

## Pre-go questions (RESOLVED at go, 2026-06-07)

- **Acceptance:** AST-equivalent + suite-green — **accepted** (not byte-identical to old).
- **Scope:** **full** `ast` rewrite (not the hybrid).
- **Readability of generated files:** loss **accepted** (ruff formats the output regardless).

## Progress (2026-06-07) — emission + rename layers converted, verified

**Done and fully verified (all 4 files AST-equivalent, 161 tests, deterministic, ruff/ty clean):**
- **Parity harness** `tools/_ast_parity.py` (dev-only): per-file `ast.dump(ast.parse(ref)) ==
  ast.dump(ast.parse(new))` vs a snapshot of the string-generator output (`/tmp/ast-ref`), with a
  normalized-unparse diff on mismatch. Sanity-checked against itself first.
- **The marquee piece — expression rename is now AST-native.** The old regex-on-source rename
  (`a_e_1 -> self.e_1`) is replaced by a `SymbolToAttr(ast.NodeTransformer)`. Proven identical to the
  old regex on **all 42** product expressions (geometric/inner/outer × G1/G2/G3, incl. cse temporaries)
  by `ast.dump` comparison. Both regex sites (`_renamer`, `generate_class`) now route through it; `re`
  import removed.
- **Emission + module assembly via `ast`.** `main()` no longer string-joins file parts: each
  per-construct generator's source is parsed into nodes (`parse_stmts`), the module body is assembled
  as a list of `ast` statement nodes, and rendered with `ast.unparse` (`module_source`). The file
  header (copyright comment + imports) stays raw text (comments can't live in an AST) and is prepended.
- Helpers added: `parse_stmts`/`parse_expr` (template-splice), `module_source`, `SymbolToAttr`,
  `expr_to_ast`.

**Not yet done — the depth decision.** The *structural method bodies* are still built as text via
`lines.append("...")` and then parsed (template-splice at the file level). The genuinely fragile string
hack (the regex) is gone and all output now flows through `ast.unparse`, but the line-by-line text
building of method bodies remains.

## The three depth levels (A / B / C)

All three produce **identical generated output** (AST-equivalent + 161 tests + deterministic); they
differ only in *how the generator is written*. This is purely about the generator's own readability /
"macro feel".

- **A — current state (done, verified).** Expression rename via `SymbolToAttr` NodeTransformer;
  emission + module assembly via `ast.unparse`. Method bodies still built line-by-line as text
  (`lines.append("    def foo...")`), then parsed. The fragile regex is gone; output flows through the
  `ast` module. Pragmatic; least churn.
- **B — code-template bodies (the macro/quasiquote feel).** Rewrite the body builders so each method is
  a readable **triple-quoted source template** with `{}` holes, parsed via `parse_stmts`, instead of
  many `lines.append` calls. Dynamic, per-blade statement lists (fields, `grades()`, `reverse` signs,
  the graded `match` arms, …) are still generated programmatically, but as small parsed snippets rather
  than hand-assembled text lines. This is what truly removes the line-by-line string concatenation and
  reads most like writing code with holes. **Recommended for the stated motivation.**
- **C — hand-built `ast` nodes.** Build every statement/expression as explicit `ast` nodes
  (`ast.FunctionDef`, `ast.Assign`, `ast.Call`, `ast.Attribute`, …) — no source text at all for the
  bodies. Maximal AST purity, but **more verbose and less readable** than B (the stdlib has no
  quasiquote), which works against the "macros are nice/readable" motivation. Built for comparison so
  the trade-off can be judged on real code.

## B progress (2026-06-07) — core converted to templates, verified

Converting the body-builders to triple-quoted `$`-templates (`string.Template` via the `fill` helper,
plus `construct_return`/`docstring_block`/`EQ_METHOD` helpers). **Done + verified AST-equivalent
(harness ALL EQUIVALENT, 161 tests, deterministic, ruff/ty clean) at each step:**
- `generate_scalar` (was ~140 `append`s of static text → one readable class template)
- `emit_bilinear`, `emit_structural`, `emit_construct_return`→`construct_return` (the G_n method bodies)
- `generate_class` (header / fields / `from`/`to_blade_dict` / shared `__eq__` / trailing
  dimension-fixed methods)
- `generate_constants`

**B complete (2026-06-07).** The graded-subtype emitter was also converted: helpers `_emit_scaled`/
`_emit_result_block`/`_emit_dispatch`/`_emit_unary_return` → source-returning `scaled_return`/
`result_block`/`dispatch_method`/`unary_return` (+ shared `cast_construct`), and `generate_graded_type`
rewritten as templates. Dead helpers removed (`emit_docstring`, `_emit_eq`, the unused `indented`).
**Zero `lines.append("...")` calls remain** — every module is now built from triple-quoted `$`-templates
(template-splice) + the `SymbolToAttr` transform for expressions, emitted via `ast.unparse`.

One gotcha found + fixed: `fill` runs `textwrap.dedent`, which strips a template's indent when **no
col-0 `$hole` line** anchors the baseline (the static `plane_of_rotation` method dropped to module
level). Static, hole-less method blocks are emitted as raw indented strings, not via `fill`.

**Verified:** harness ALL EQUIVALENT (all 4 files), `make check-generated` deterministic, `ty` src+tests
clean, `ruff` clean, full suite **161 passed**. Ready for the author to commit as the B alternative.

## C — implementation plan (next)

Goal: build every class/method/statement/expression as explicit `ast` nodes (no source text for
bodies), `ast.unparse` the assembled module. Start from committed B and **replace** the template bodies
with node builders, so C's tree is a clean node-based alternative. Same acceptance invariants.

**What carries over unchanged from A/B (do NOT rebuild):**
- The file header (`header()` / `SCALAR_HEADER`) stays raw text, prepended (comments can't be AST).
- `main()` already assembles modules from nodes via `parse_stmts` + `module_source`; for C the
  per-construct generators return **nodes directly** (or a small list of nodes), so `main()` can call
  `module_source(...)` on them without the `parse_stmts` round-trip. (Either keep returning source and
  `parse_stmts` it, or return nodes — returning nodes is the more honest C; decide at start.)
- **`expr_to_ast(expr, rename)` already returns an `ast.expr` node** — C's math layer is *already*
  node-native. This is the one place C is arguably cleaner than B (B unparses these nodes to text and
  re-parses them; C embeds the node straight into the constructor `ast.keyword`).

**The real subtleties (these are where C will fight us):**
1. **Term ordering must be reproduced in node form.** B's `format_assignment` sorts additive terms by
   `term_grade_key` before rendering, so the reference output's `BinOp` operands are grade-ordered.
   `ast.dump` compares operand order, so C must sort the sympy terms by `term_grade_key`, build each
   term via `expr_to_ast`, and fold them left-assoc into `BinOp(Add/Sub)` in that order (Sub when the
   term is negative, mirroring the `- x` vs `+ x` text logic). A plain `expr_to_ast(whole_sum)` would
   use sympy's order and fail parity.
2. **The `numbers.Real` cast logic** in `format_assignment`/`result_block`/`unary_return` (wrap bare
   `-self.x` / constants / non-symbol Muls in `typing.cast(numbers.Real, …)`, leave bare symbols and
   sums uncast) must be replicated as node decisions, identically, or `ast.dump` diverges.
3. **`typing.cast(typing.Self, …)`** and `typing.cast(numbers.Real, …)` wrappers everywhere →
   `ast.Call(ast.Attribute(ast.Name('typing'),'cast'), [<type>, <value>], [])`.
4. **Verbose node types to get right** (have references handy):
   - `match rhs:` dispatch → `ast.Match(subject, cases=[ast.match_case(pattern, body)])`; class patterns
     `Scalar()` → `ast.MatchClass(ast.Name('Scalar'), [], [], [])`; the number case
     `int() | float() | sympy.Expr()` → `ast.MatchOr([...])` with `sympy.Expr` as
     `MatchClass(ast.Attribute(ast.Name('sympy'),'Expr'))`; default `case _:` → `MatchAs(None,None)`.
   - `to_blade_dict` dict-comprehension → `ast.DictComp` with a `comprehension` + an `if` (`coef != 0`).
   - `__eq__`’s `all(... for blade in ...)` → `ast.Call(ast.Name('all'), [ast.GeneratorExp(...)])`.
   - `__iter__` → `FunctionDef` whose body is `If`+`Expr(Yield(...))` per blade (a generator function).
   - dataclass decorator → `ast.Call(ast.Attribute(ast.Name('dataclasses'),'dataclass'),
     keywords=[ast.keyword('eq', ast.Constant(False)), ast.keyword('slots', ast.Constant(True))])`.
   - fields → `ast.AnnAssign`; `DIMENSION: typing.ClassVar[int] = n` → `AnnAssign` with a subscripted
     annotation; `@classmethod` → `decorator_list=[ast.Name('classmethod')]`; method args →
     `ast.arguments(args=[ast.arg('self'), ast.arg('rhs')], ...)` (all the empty arg fields needed).
5. **Parenthesization is NOT a concern for parity** — `ast.dump` compares node structure, not parens or
   whitespace; `ast.unparse` re-parenthesizes by precedence and ruff reformats. Only node *shape*
   (incl. operand order) matters.

**Tactics:**
- Build a small node-builder helper set to keep it sane (`name()`, `attr(obj, *parts)`,
  `call(fn, args, kwargs)`, `cast_self(x)`, `cast_real(x)`, `method(name, body, args=('self','rhs'),
  decorators=(), returns=...)`, `ret(x)`). Note: a good helper set starts to resemble a quasiquote —
  which is exactly B; that tension is the finding to surface in the comparison.
- **Per-construct `ast.dump` debugging:** because C builds nodes, you can compare a single method's
  `ast.dump(built_node)` against `ast.dump(ast.parse(reference_method_source).body[0])` to localize a
  mismatch, instead of diffing whole files. Faster than B's text diffs.
- Convert one emitter at a time (`generate_scalar` first — fully static, easiest node build; then the
  G_n class; then graded), re-running the harness each step.

**Expected outcome (the comparison the author wants):** correct + verified, but materially more code and
less readable than B for the same output — the empirical evidence for choosing B (or A) over C. Capture
a rough line-count / readability note when done.

## C progress (2026-06-07) — foundation built + Scalar fully node-built, verified

**Built and verified (ALL EQUIVALENT, 161 tests, deterministic, ruff/ty clean):**
- **Full C node-builder foundation:** `nm`/`dot`/`lit`/`call`/`cast`/`cast_self`/`cast_real`/`ret`/
  `subscript`/`opt_int`/`arg`/`fn`/`cls`/`dataclass_decorator`/`ann_assign`/`assign`/`isinstance_`/
  `not_`/`ne_zero`/`construct`/`method_doc`/`class_doc`/`coerce_pair_gn`/`eq_method`, plus the three
  value-policy builders that mirror B's casting/term-order logic exactly — `summed_value` (=
  format_assignment), `result_value` (= result_block), `unary_value` (= unary_return). `expr_to_ast`
  (from A) supplies the math nodes; `as_nodes()` in `main()` lets node-returning (C) and
  source-returning (B) emitters coexist during the migration.
- **`generate_scalar` fully hand-built as `ast` nodes** (returns `list[ast.stmt]`), AST-equivalent.
  Required reproducing exact docstring `Constant` whitespace, the `__eq__` `GeneratorExp`, the
  `to_blade_dict` `IfExp`/`Dict`, the `is_close` `super()` call, `__iter__`'s `Yield`, and `dual`'s
  `Raise` — all as nodes.

**Gotcha fixed:** the new node `generate_scalar` was initially **shadowed** by the leftover B template
`generate_scalar` defined later in the file (F811) — so parity was passing via the *old* one. Deleted
the B version; the node version is now live and verified.

**Verbosity data point (the comparison the author wanted):** the Scalar class is **~260 lines of
hand-built node code in C vs ~140 lines as one B template** — and far less readable (every `cast`,
`BinOp`, `If`, keyword is spelled out). This is the empirical evidence C exists to provide.

**C complete (2026-06-07).** All four generators — `generate_scalar`, `generate_class`,
`generate_graded_type`, `generate_constants` — are now hand-built `ast` nodes (each returns
`list[ast.stmt]`); `main()` assembles + `ast.unparse`s them. The graded dispatch is hand-built
`ast.Match`/`match_case`/`MatchClass`/`MatchOr`; the math uses `summed_value`/`result_value`/
`unary_value` (which reproduce B's casting + grade-order policy as nodes). All the dead B template
helpers were removed (`fill`, `EQ_METHOD`, `construct_return`, `docstring_block`, `cast_construct`,
`scaled_return`, `result_block`, `dispatch_method`, `unary_return`, `emit_bilinear`, `emit_structural`,
`format_assignment`, `_renamer`, `blade_literal`, `as_nodes`); `product_result`/`unary_result` no
longer return a `render`.

**Verified:** harness ALL EQUIVALENT (all 4 files), `make check-generated` deterministic, `ty` src+tests
clean, `ruff` clean, full suite **161 passed**. Ready for the author to commit as the C alternative.

**Readability reassessment (author's challenge — line count doesn't matter, understandability does):**
the earlier "less readable" was a conventional-dev bias (verbosity + having to mentally unparse). On
the *understandability* axis, for a metaprogramming/Lisp mindset C is a wash-to-win: it's explicit
code-as-data, eliminates B's two-language + manual-whitespace fragility (we hit a real `fill`/dedent
bug in B that is *impossible* in C — nodes carry structure, not indentation; 3.13 validates them), and
composes into named, testable builders. Genuine C costs that are *not* taste: a few opaque node types
(chiefly `Match`/`MatchClass`/`MatchOr`, and `GeneratorExp`/`comprehension`) read worse than their
surface syntax, plus an `ast`-API learning curve. Net: C is a legitimate choice; "less readable" retracted.

## Execution plan (author's review workflow)

Each level is delivered as its **own complete, working, tested commit**, so the author can `git reset`/
rebase to whichever tree they prefer and discard the rest:

1. **A** — current state. *Author commits it outside the container.* (baseline)
2. **B** — Claude rewrites the body builders as triple-quoted templates (starting from the committed A).
   Verify (harness AST-equivalent + 161 tests + `make check-generated` + ruff/ty). *Author commits.*
3. **C** — Claude rewrites the body builders as hand-built `ast` nodes, **replacing B's template
   approach** (starting from the committed B), so C's *tree* is a clean node-based alternative (not
   templates + nodes). Verify (same gates). *Author commits.*
4. **Author reviews A / B / C** as three final products and rewrites git history (reset / rebase /
   cherry-pick) to keep the chosen style; the others are dropped.

Because each commit's *working tree* is a complete generator, picking = `git reset --hard <commit>` (or
rebase-drop the unwanted commits). C's diff being against B is irrelevant to picking — selection is by
tree state, not by stacking diffs.

**Verification invariant for B and C (non-negotiable, every step):**
- `python tools/_ast_parity.py` → ALL EQUIVALENT (output AST-identical to the original string baseline;
  reference snapshot in `/tmp/ast-ref`, regenerable by running the saved
  `/tmp/ast-ref/gen_specialized_STRING.py`, or from any prior A/B state since all are equivalent).
- `make check-generated` deterministic; full `pytest -q` green (161); `ruff`/`ty` clean.
- The file header (`header()`/`SCALAR_HEADER`) stays raw text in all levels (comments can't be AST).

## Open questions / live reminders

- **Workflow** — confirmed; A and B committed, C next. ✅
- **B template depth** — resolved: dynamic per-blade lists are built as small per-item snippets in a
  loop (not forced into one template). ✅
- **After you pick the winner (A/B/C):** (1) delete the dev-only `tools/_ast_parity.py` — its job
  (proving the migration) is done; `make check-generated` is the permanent guard; (2) update CLAUDE.md's
  "Code generation" section to describe the chosen approach. Do these as part of the final pick, or
  separately? **Pending.**
- **Parity reference durability:** the harness compares against `/tmp/ast-ref` (ephemeral). If the
  session restarts before C is done, regenerate it from the saved `/tmp/ast-ref/gen_specialized_STRING.py`
  (the original string generator) — or from the committed A state (`git show A:…` is moot since g*.py
  are gitignored, so use the saved string generator). Worth noting since C still needs it.

## Notes / cross-refs

- The generated files are no longer in git (see `tasks/archive/2026/06/07/build-time-codegen-dist.md`),
  so the parity harness generates *both* old and new into temp dirs and compares — nothing to diff
  against in the tree.
- Sources consulted:
  - Python docs — [`ast`](https://docs.python.org/3/library/ast.html)
  - [Green Tree Snakes — getting to/from ASTs](https://greentreesnakes.readthedocs.io/en/latest/tofrom.html)
  - [Jelle Zijlstra — improving `ast` in 3.13+](https://jellezijlstra.github.io/ast313.html)
  - [`ast.unparse` limitations (comments/formatting lost)](https://runebook.dev/en/docs/python/library/ast/ast.unparse)
  - [LibCST — why a lossless CST](https://libcst.readthedocs.io/en/latest/why_libcst.html)
