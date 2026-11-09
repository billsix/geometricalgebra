# Investigate rewriting the code generation to use the Python `ast` module

**Created:** 2026-06-07 · **Completed:** 2026-06-07

## Outcome

`tools/gen_specialized.py` was rewritten to build the specialized `g1/g2/g3.py` + `scalar.py` with the
Python **`ast`** module instead of string concatenation, still deriving every closed form from `gn.py`'s
symbolic ops. The author's motivation: as a Lisp programmer, manipulating code as data (macros) is more
natural than string mashing. Three depth levels (A / B / C) were each built as a complete, verified
commit so the author could pick by tree state (`git reset --hard`); **C (hand-built `ast` nodes) was
chosen and committed.** After the pick, the dev-only parity harness `tools/_ast_parity.py` was deleted
and CLAUDE.md "Code generation" was refreshed. The structure follow-up was done in
`tasks/archive/2026/06/07/gen-specialized-structure-refactor.md`.

## How the generator worked before

- **Math layer** (already generated): run the symbolic op in `Gn` over sympy `Symbol` operands
  (`a_e_1`, `b_e_12`, …), `sympy.cse` the outputs, print with `sympy.sstr`, then a word-boundary
  **regex** renamed `a_e_1 → self.e_1`, `b_e_12 → rhs.e_12`. `format_assignment` ordered additive
  terms by grade (`term_grade_key`) and hand-wrapped at 88 cols.
- **Scaffolding** (~1100 lines): raw `lines.append(f"...")` for the dataclass, fields,
  `from_blade_dict`/`to_blade_dict`, `__eq__`, the bilinear isinstance dispatch, the structural methods,
  the graded-subtype `match` dispatch, `scalar.py`, the basis constants, and the copyright/import
  header. Docstrings were copied from `AbstractMultiVector` via `inspect.getdoc`.

## What was learned about `ast`

- `ast.unparse` (3.9+) turns a tree back into valid source; `fix_missing_locations` fills positions;
  3.13 validates node construction, so malformed trees fail fast.
- The AST is lossy: no comment nodes, canonical formatting, no 88-col wrapping. Docstrings survive (they
  are string `Expr` statements). So the copyright/import header stayed **raw text prepended** to the
  unparsed body in every level.
- The stdlib has no quasiquote; the nearest is **template-splice** (`ast.parse` a snippet with holes,
  fill via a `NodeTransformer` or a template).
- `libcst` was rejected: its strength is lossless transformation of existing files, a heavier dependency
  with no payoff for greenfield generation.

## Decisions (resolved at go, 2026-06-07)

- **Full rewrite**, not the hybrid "replace only the regex" option.
- **Acceptance = equivalence, not byte-identity.** `ast.unparse` + ruff cannot reproduce the hand-tuned
  layout, so "same output" was defined as per-file `ast.dump(ast.parse(old)) == ast.dump(ast.parse(new))`
  plus behavioural parity (full pytest incl. doctests and the `[Gn, G1, G2, G3]` conformance suite)
  plus `make check-generated` determinism.
- **Readability loss of the generated files was accepted** (ruff formats them anyway).
- Dynamic per-blade statement lists in B were built as small per-item snippets in a loop, not forced
  into one template.

## The three levels

- **A — minimal.** The regex rename became a `SymbolToAttr(ast.NodeTransformer)` (proven identical to
  the regex on all 42 product expressions, incl. cse temporaries); module assembly and emission went
  through `ast.unparse` (`parse_stmts`, `module_source`, `expr_to_ast`); the `re` import was dropped.
  Method bodies were still `lines.append` text, then parsed.
- **B — template-splice.** Every emitter became a triple-quoted `$`-template (`fill` =
  `string.Template`); zero `lines.append` remained. Gotcha found: `fill` runs `textwrap.dedent`, which
  strips a template's indent when no col-0 `$hole` line anchors it (the static `plane_of_rotation`
  method dropped to module level), so hole-less method blocks were emitted as raw indented strings.
- **C — hand-built nodes.** All four generators (`generate_scalar`, `generate_class`,
  `generate_graded_type`, `generate_constants`) return `list[ast.stmt]`, built with a small helper set
  (`nm`/`dot`/`lit`/`call`/`cast_self`/`cast_real`/`fn`/`cls`/`ann_assign`/…). Three value-policy
  builders (`summed_value`, `result_value`, `unary_value`) reproduce B's `typing.cast(numbers.Real, …)`
  policy and the `term_grade_key` operand order exactly, since `ast.dump` compares operand order.
  The graded dispatch is hand-built `ast.Match`/`match_case`/`MatchClass`/`MatchOr`; all dead B helpers
  were removed. Gotcha found: the new node `generate_scalar` was at first shadowed (F811) by the
  leftover B version later in the file, so parity passed via the old one; the B version was deleted.

**Comparison.** The Scalar class was ~260 lines of node code in C vs ~140 lines as one B template. The
initial "C is less readable" verdict was retracted after the author's challenge (line count doesn't
matter, understandability does): for a code-as-data mindset C removes B's two-language,
manual-whitespace fragility (the `fill`/dedent bug cannot happen with nodes) and composes into named,
testable builders. C's real costs are a few opaque node types (`Match`/`MatchClass`/`MatchOr`,
`GeneratorExp`/`comprehension`) and an `ast`-API learning curve.

## Verification

At every step of A, B and C: the parity harness reported all four files AST-equivalent to the original
string generator's output (snapshot regenerated from a saved copy of the string generator, since the
generated files are gitignored — see `tasks/archive/2026/06/07/build-time-codegen-dist.md`), `make
check-generated` was deterministic, `ruff` and `ty` (src + tests) were clean, and the full suite passed
(161 tests).

## Sources

- Python docs — [`ast`](https://docs.python.org/3/library/ast.html)
- [Green Tree Snakes — getting to/from ASTs](https://greentreesnakes.readthedocs.io/en/latest/tofrom.html)
- [Jelle Zijlstra — improving `ast` in 3.13+](https://jellezijlstra.github.io/ast313.html)
- [`ast.unparse` limitations (comments/formatting lost)](https://runebook.dev/en/docs/python/library/ast/ast.unparse)
- [LibCST — why a lossless CST](https://libcst.readthedocs.io/en/latest/why_libcst.html)
