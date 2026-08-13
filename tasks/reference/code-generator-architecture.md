# The gacalc code generator

**Reference document** — the deep contributor map for how the specialized (`G`) and
graded (`Vector_n`/`Bivector_n`/`Trivector`/`Rotor_n`/`Scalar`) modules are produced from the `Gn`
reference. Not a task; update in place if the generator changes. Last updated 2026-07-21.

Read this alongside — do not duplicate — the **"Code generation"** and **"doc-region markers"**
sections of the repo `CLAUDE.md` (the *what* and the golden rules) and the sibling reference
`tasks/reference/generated-product-typing.md` (the deep *rationale* for the `@typing.overload`
precise-typing feature). This doc is the *how the machinery is wired* map.

**New to the generator? Start with the narrative overview in the module docstring of
`tools/gen_specialized.py`** — the flow of ideas (`Gn` run on symbols → the captured formula →
compiled code), an ASCII pipeline diagram, and a live, doctest'd worked trace. That is the
human-readable front door; this doc is the dense, random-access map you graduate to.

The whole generator is three files under `tools/`:

- `tools/gen_specialized.py` — the domain layer: GA knowledge, the type registry, the symbolic→AST
  bridge, and one builder per emitted construct. ~2300 lines.
- `tools/astbuild.py` — the domain-agnostic node-builder DSL + the doc-region machinery. Knows
  nothing about geometric algebra; only the conventions of the code this generator emits
  (`cast_self`/`cast_coef`, marker sentinels). ~470 lines.
- `tools/check_doc_regions.py` — a standalone verifier (`make check-regions`) over the emitted
  markers.

The golden rule from `CLAUDE.md`, restated because it dominates everything below: **a correct
generator change appears in `git diff` as a `tools/` diff and *nothing* under `src/gacalc/`.** The
three outputs — `src/gacalc/g1.py`, `g2.py`, `g3.py` — are gitignored build artifacts (each
self-contained: its own `ScalarN` + graded types + full `G_n`; there is no shared `scalar.py`).
Never hand-edit them; regenerate and read them on disk.

---

## 1. The pipeline — `main()` → three `.py` files

`main()` (`gen_specialized.py:2256`) is the driver. Each module is a **list of `ast` statement
nodes** built directly by the per-construct generators, then rendered to source text with
`ast.unparse` inside `astbuild.module_source`. There is no template/string layer — the AST *is* the
intermediate representation (an earlier string generator was replaced; the parity docstrings on many
builders, e.g. "= result_block, as nodes", are vestiges of that migration).

**The raw-header / AST-body split.** A Python AST cannot hold comments, so every file is assembled as:

```
raw text header  +  "\n\n"  +  module_source(inject_region_markers(nodes))  +  "\n"
```

- The **header** is a raw f-string (`header(name, n)`): the LGPL copyright block, the
  `AUTO-GENERATED … do not edit` banner, `from __future__`, and the imports — including
  `_coerce`, which since 2026-07-29 is defined once in `base.py` and imported (it used to be
  pasted into each module). (There is no longer a separate `SCALAR_HEADER` — `ScalarN` is emitted into each
  `gN.py`, not its own module.) `header()` conditionally appends `, _OperandT` to the
  `gacalc.base` import only for `n >= 2` (the sandwich TypeVar is used only by `Rotor_n`, which
  doesn't exist in 𝒢₁ — importing it there would be an unused-import `F401`).
- The **body** is the node list, `ast.unparse`'d.

**Emission order** — everything for one algebra goes into its one self-contained module. For each
`(n, name, filename)` in `ALGEBRAS` (currently `[(1,"G","g1.py"), (2,"G","g2.py"),
(3,"G","g3.py")]`), `main()` concatenates, in order (later types reference earlier ones by name, but
`from __future__ import annotations` makes return annotations lazy, so the order is for readability,
not correctness):

1. `generate_scalar(n, f"Scalar{n}", name)` — the per-algebra grade-0 `ScalarN`. Its `dual` names the
   same-module pseudoscalar (`Scalar.dual -> Trivector`), which is *why* it lives here and not in a
   shared module (a shared `scalar.py` importing `Trivector` from `g3` would be a circular import).
2. `generate_class(n, name)` — the full all-blades `G_n` class + its post-class basis-constant
   assignments.
3. `generate_graded_type(spec, n, name)` for each `spec in graded_specs(n)` — the graded subtypes.
4. `generate_constants(n, name)` — the module-level `zero`/`one`/`e_1…` constants and `__all__`
   (which includes `ScalarN`).

**Where ruff runs.** After all files are written, `main()` calls `ruff_format(written)` (`:2230`),
which runs `ruff check --fix --quiet` then `ruff format --quiet --line-length=88` on the freshly
written files. So a regen needs **no** separate `format.sh` pass — the committed-shape output is
already formatted. It's best-effort: `FileNotFoundError` (no ruff) prints a warning and leaves the
files raw rather than failing generation. Note the `--line-length=88` here is the generator's own
call; the repo's `format.sh`/linter config governs everything hand-written.

Each per-construct generator returns `list[ast.stmt]`; `main()` concatenates them, wraps the whole
list once through `inject_region_markers` (§6), and renders. The four "level C" generators are
`generate_scalar` (`:1119`), `generate_class` (`:1506`), `generate_graded_type` (`:1742`), and
`generate_constants` (`:2107`).

---

## 2. `tools/astbuild.py` — the node-builder DSL

A thin, correct-by-construction wrapper over the `ast` module. Everything returns `ast` nodes; the
GA layer never touches `ast.*` constructors for the common cases.

**Core builders (a representative map, not exhaustive):**

- `name_ref(id)` → `ast.Name` load; `constant(v)` → `ast.Constant` (casts the value to `Any` at the
  boundary so blade-tuple dict keys like `()` are accepted past typeshed's narrower type).
- `attribute(value, *parts)` → chained `ast.Attribute` (`attribute("self", "coeff_e_1")`,
  `attribute("typing", "Self")`); accepts a str (wrapped in `name_ref`) or an existing node.
- `call(func, args=(), **kwargs)` → `ast.Call`; kwargs become keyword arguments.
- `subscript`, `isinstance_`, `not_`, `ne_zero` (`x != 0`), `bool_and`/`bool_or` (a single test is
  returned bare, matching the old string generator), `opt_int` (`int | None`).
- `function_def(name, body, params=None, defaults, decorators, returns)` — params default to
  `[self]`; `type_params=[]`. `class_def(name, body, bases=("MultiVectorBase",), decorators)`.
  `argument(name, annotation)` → `ast.arg`.
- `annotated_assign(target, annotation, value)` → `ast.AnnAssign` (used for typed fields and typed
  locals); `assign(target, value)` → plain `ast.Assign`.
- `dataclass_decorator(**flags)` → `@dataclasses.dataclass(eq=False, slots=True)` (the flags passed
  by the callers).

**Construction helpers** (the subclass story lives here — see the finality note below):

- `construct(name, pairs)` → `Name(field=value, …)` — construct a *named* class. Used for the
  same-type results of **every** value type — all are `@typing.final` (not subclassable), so they emit
  the concrete class directly (e.g. `return Vector(…)`, `return G(…)`).
- `construct_type_of(var, pairs)` → `type(var)(field=value, …)` — build via an operand's runtime
  type; used only by the rotor `sandwich`, which is polymorphic over its operand.
- `construct_type_self(pairs)` → `type(self)(…)` — a general astbuild primitive (via
  `return_construct(..., final=False)`), **no longer used by the generator** since every value type is
  final; kept as a DSL capability should a non-final generated type ever be added.
- `return_construct(name, pairs, owner, final)` → `return cast(Self, Name(…))`, **but** if
  `owner == name` (a same-type op) it emits the class directly: `return Name(…)` when `final=True`
  (every current caller), else `return type(self)(…)`.

**Finality (graded 2026-07-21, full `G_n` 2026-07-23):** *every* generated value type is
`@typing.final` — the graded value types (`Vector*`/`Bivector*`/`Trivector`/`Rotor*`), `ScalarN`,
**and the full classes `G`**. So same-type constructions always emit the concrete class;
the old `result_spec.kind != "full"` branch (final → concrete, full → `type(self)`) was **collapsed**,
and the generated full class carries **no `type(self)`** at all. Nothing subclasses `G_n` (the graded
types are the value types; the dimension-agnostic `Gn` in `gn.py` is the general representation), so
the former "extension point" was unused. See `tasks/reference/design-decisions.md` (the "Same-type
generated ops" entry) and `tasks/archive/2026/07/23/investigate-final-full-classes.md`.

**The three casts** — this is *the* convention `astbuild` encodes about the emitted code:

- `cast_self(v)` → `typing.cast(typing.Self, v)`.
- `cast_operand(v)` → `typing.cast(_OperandT, v)` — for the rotor sandwich, which returns the
  *operand's* type, not `Self`.
- `cast_coef(v)` → `typing.cast(Coef, v)`, **except** it returns `v` unwrapped when `v` is a bare
  field (`ast.Name`/`ast.Attribute`, e.g. `self.coeff_x`) or a negated field (`-self.coeff_x`) —
  those are already `Coef`, and casting them makes ty warn about a redundant cast. Only
  compound expressions (sums, products, `d.get(...)`, literals) get wrapped. This is why the
  generated code has `typing.cast(Coef, …)` on some fields but bare `self.coeff_e_1` on others.

**`SymbolToAttr(ast.NodeTransformer)`** — the sympy→AST bridge's rewriter. Given a `rename` map
`{sympy-symbol-name: (obj, attr)}`, it visits `Name` nodes and rewrites each operand symbol to
attribute access: `a_e_1` → `self.coeff_e_1`. A structural, correct-by-construction replacement for
the old word-boundary regex on rendered source. **Empty `attr` special case:** `("rhs", "")` binds
the symbol to the bare name `rhs` (not `rhs.attr`) — used by the number-operand fast path, where a
bare scalar `rhs` stands in for what would be `rhs.coeff_scalar`.

### The doc-region machinery (in `astbuild.py`)

A comment cannot live in an AST, so markers are emitted as **sentinel string-literal statements** and
rewritten to `# comments` in the rendered text.

- `_MARKER_OPEN`/`_MARKER_CLOSE` = `@@doc-region@@` / `@@/doc-region@@`; delimiters chosen never to
  occur in real code. `marker(text)` → `ast.Expr(ast.Constant("@@doc-region@@" + text +
  "@@/doc-region@@"))`. `_MARKER_RE` matches the sentinel *however `ast.unparse` quoted it* (bare
  `'…'` or triple-quoted in docstring position).
- `inject_region_markers(body)` (`:126`) is the one entry point `main()` calls. For each top-level
  `ClassDef` it wraps the class and, inside it, its declaration, its instance variables, and each
  method:
  - `<Class> class` around the whole class; `<Class> declaration` around the `class` line;
    `<Class> cls variables` around the `ClassVar` declarations (`DIMENSION` + the `e_*` basis
    constants — the `AnnAssign`s that **are** `ClassVar`, `classvar_indices`); `<Class> instance
    variables` around the dataclass fields (the `AnnAssign`s that are **not** `ClassVar` —
    `field_indices`, filtered by `_is_classvar`); `<Class> <method> method` around each method.
  - **Why `cls variables`, not `class variables`:** `<Class> class` is already a region, and
    `check-regions` forbids a name that string-prefixes another (`"G class variables"` starts with
    `"G class"`). `cls variables` reads as "class variables" (`cls` = the class), parallels
    `instance variables`, and doesn't prefix `<Class> class`. For the region to be one contiguous
    block, `class_header_stmts` emits `basis_classvar_decls` **right after `DIMENSION`** (before the
    `coeff_*` fields) — the `e_*` are annotation-only ClassVars, so this reorder is cosmetic
    (`Scalar` has no ClassVars, so no `cls variables` region).
  - Most markers are AST **siblings** placed around a node, so a copied docstring (which must stay
    first in its block or `ast.unparse` renders it as an ugly escaped one-liner) is untouched.
  - `_method_label(class_name, method, seen)` builds a **unique, prefix-free** label. A property
    setter/deleter shares the getter's name, so it takes a `<method> setter`/`deleter` qualifier
    placed *before* the trailing `method` keyword (so `x setter method` doesn't contain
    `x method`); any remaining duplicate gets a numeric suffix. `seen` is mutated across the class.
  - `_is_overload(node)` returns True for a `@typing.overload`/`@overload` stub; those are emitted
    **without** a region (they share the impl's method name — marking them would duplicate the
    `<Class> <method> method` region). Only the implementation carries the method region.
- **The one exception — `declaration` *end*:** it must land *after* the `class` line but *before*
  the docstring. Emitting it as an AST node there would displace the docstring, so
  `inject_region_markers` emits only the declaration *begin*; the end is inserted at the **text**
  level by `_insert_declaration_ends(src)` (`:188`), which scans rendered lines for the
  `# doc-region-begin <C> declaration` comment, waits for the matching `class <C> …:` line, and
  inserts `# doc-region-end <C> declaration` right after it at the right indent.
- `module_source(body)` (`:219`) ties it together: `ast.unparse` the module, `_MARKER_RE.sub` the
  sentinels to `# comments`, then `_insert_declaration_ends`. All no-ops when there are no markers.

See §6 for what these markers are *for* and what `check-regions` verifies. The trailing keyword
(`class`/`declaration`/`method`/`setter`) is load-bearing for Sphinx prefix-matching — do not drop it.

---

## 3. The type system inside the generator

The generator resolves every result type **at generation time from the symbolic result's grade
support** — never from runtime float values. This is what makes `Vector * Vector : Rotor` a
*compile-time* fact.

**`TypeSpec`** (`:341`) — a `NamedTuple(name, blades, dim, kind)`. `blades` is a tuple of blades
(each a tuple of basis-vector indices); `kind` is `"scalar"` / `"graded"` / `"full"`.

**The registry** — every type a result can resolve to, for a given dimension:

- `SCALAR = TypeSpec("Scalar", ((),), 0, "scalar")` (`:351`) — the shared grade-0 type.
- `graded_specs(n)` (`:354`) — `Vector{n}`, then `Bivector{n}` (n≥2), `Trivector{n}` (n≥3), and the
  even-subalgebra `Rotor{n}` (n≥2; for n==1 the even part is just the scalar, so no Rotor).
- `full_spec(n, full_name)` (`:372`) — the all-blades `G_n`.
- `registry_for_dim(n, full_name)` = `[SCALAR, *graded_specs(n), full_spec(...)]`.

**`resolve(support, n, full_name)`** (`:381`) — the core rule: the **smallest registered type whose
blades cover `support`, else widen to `G_n`** (the full type always covers). "Smallest" is
`min` keyed on `(len(blades), 0 if scalar else 1, name)`, so among equal-size candidates the scalar
wins and ties break by name. The full `G_n` is always a candidate, guaranteeing a result.

**`product_result(lhs_spec, rhs_spec, gn_product, n, full_name)`** (`:393`) — the workhorse. It:

1. Builds symbolic operands: a `Gn` from `{blade: Symbol("a_"+label)}` for the lhs, `b_…` for the
   rhs.
2. Runs the *actual `Gn` symbolic op* (`gn_product`, a lambda like `lambda a, b: a * b`) — so the
   closed form is provably the reference product.
3. Computes `support` = blades whose result coefficient is symbolically nonzero, `resolve`s it to a
   `result_spec`, and returns `(result_spec, out_exprs)` — the output sympy expressions **over the
   result type's blades**, in that type's blade order.

**`unary_result`** (`:421`) — the same for a single-operand op (`dual`, grade projection): symbolic
operand, run `gn_unary`, resolve the support.

**Symbolic → closed-form AST.** Given the `out_exprs` from `product_result`, several helpers turn
each into a constructor field value:

- `expr_to_ast(expr, rename)` (`:90`) — `parse_expr(sympy.sstr(expr))` then `SymbolToAttr(rename)`
  → the sympy expression as an AST with operand symbols rewritten to `self.coeff_*` / `rhs.coeff_*`.
- `rename_map(blades_self, blades_rhs, rhs_name)` (`:547`) — builds that rename dict: `a_<f>` →
  `(self, coeff_<f>)`, `b_<f>` → `(rhs_name, coeff_<f>)`.
- `summed_value(expr, rename)` (`:447`) — a constructor field value as a **grade-ordered** sum:
  constant-free expressions fold their terms left-assoc as `BinOp`s in `term_grade_key` order,
  subtracting negative terms (so the node tree matches the historical operand order); a
  symbol-free constant is `cast_coef`'d. `term_grade_key` (`:143`) orders each `a_L * b_R` term by
  `(grade(L), indices(L), grade(R), indices(R))` so sums read scalar → vector → bivector → …
  instead of sympy's roughly-lexicographic order (where `e_12` sorts before `e_2`).
- `result_value` / `unary_value` — thin wrappers picking the right form for a bare symbol vs a
  compound expression (avoiding redundant `cast_coef`).
- **`sympy.cse`** — common-subexpression elimination. `result_block_stmts` (`:866`) runs
  `sympy.cse(out_exprs)`, emits the `x0: Coef = …`, `x1: Coef = …` temporaries as typed locals, then
  the `return … (field=reduced_expr, …)`. This is why generated products carry `x0`/`x1`/`x2`
  temps (visible in the sandwich output).

`result_block_stmts` also decides *how to construct* the result, via `owner`/`via_var`/`cast`:
for a same-type result (result type equals the owner, cast is `cast_self`) it emits the concrete
class `RType(…)` — every value type is `@typing.final`, so there is no `type(self)` branch;
`type(<via_var>)(…)` for the grade-preserving sandwich (build via the operand's type); otherwise
`cast(<T>, RType(…))`.

**Dimension-known methods (`dimension_known_methods` in `generate_class`).** Five methods whose
result is *entirely* fixed once the dimension is chosen are emitted as the closed form / constant
rather than delegating to base's general `n`-parametrized runtime algorithm: `dual`,
`unit_pseudoscalar`, `unit_pseudoscalar_squared`, `bases`, `symbolic_multivector`. Each is computed
at generation time from `Gn` (`unit_pseudoscalar_squared`'s `±1` sign by actually squaring the
pseudoscalar; `dual` via the `unary_result`/`summed_value` machinery) and emitted **only on the
full class `G_n`** — the graded subtypes don't carry them (`dual` excepted, which they had already,
guarded the same way), since the pseudoscalar/basis span the whole algebra and don't fit one graded
type. **The `n` parameter is kept** (`n: int | None = None`): dropping it would be an invalid
Liskov override of the `n`-required base (`Gn` is dimension-agnostic), which `ty` rejects. So each
body is guarded `if n is None or n == <DIMENSION>: <known>` with a `super()` fallback for a
non-default `n` (the rare, off-dimension call like `G.bases(1)`), preserving prior semantics
exactly. Constructs via `cls(…)` (subclass-preserving, fresh instance — not the shared basis
constant). This retired the `dim_or_n` helper.

---

## 4. `dispatch_method` — the match-on-rhs table

`dispatch_method` (`:929`) builds the bilinear products (`_geometric_product`, `inner_product`,
`outer_product`), the linear ops (`__add__`/`__sub__`), and the rotor `sandwich` on the graded
types. It emits a method that `match`es on the operand's runtime type — one `case` per registered
type — each case's body produced by `result_block_stmts` with the `product_result`-resolved type.

Structure of the emitted method:

1. **Exact-type early-out** (only when `cast is cast_self`, i.e. the `Self`-returning ops — *not* the
   sandwich): a leading `if type(rhs) is <SelfType>:` returning the same-type closed form directly,
   skipping the `match` ladder. The dominant operand across the Code-the-Classics + mvp workloads is
   the *same concrete type* as `self`, so this identity check is the hot path. Since 2026-07-29 it
   **fully replaces** the same-type `case T()` arm (the loop skips emitting it): the classes are
   `@typing.final`, so nothing legal is isinstance-T without being exactly T — the arm was dead code
   repeating the closed form. A finality-violating runtime subclass falls to `case _:` and widens
   via `_coerce` (correct, just not narrow). Skipped for the sandwich because a same-type operand is
   rare there — so the sandwich's `match` DOES keep its same-type arm.
2. **`number_case`** (optional): a leading `case int() | float() | sympy.Expr():` treating a bare
   number as the grade-0 operand. It emits the *same* result as the `Scalar` arm but reads `rhs`
   directly (the empty-`attr` rename trick) rather than `rhs.coeff_scalar` — no intermediate
   `Scalar` object, no re-dispatch. Used by `__add__`/`__sub__` (and `__mul__` scales separately).
3. **One `case <T>():` per `[SCALAR, *graded_specs(n)]`** (minus the same-type arm for the
   `Self`-returning ops — the early-out in 1 covers it) — the graded product/sum table. Each arm's
   body is `result_block_stmts(result_spec, out_exprs, rename_map(...), cast, owner=self.name,
   via_var=param_name if cast is cast_operand else None)`.
4. **The fallback `case _:`** — coerce both operands to the full `G_n` via the module-level
   `_coerce(x, G_n)` helper and delegate to `G_n`'s op: `return cast(<T>, fallback_node)`. This is
   how a `Gn`, the full class, or any foreign operand is handled. `fallback_node` is passed in by the
   caller (e.g. `left * right`, `left.inner_product(right)`).

**Parameters** (the knobs the sandwich and overload work turn):

- `cast` (default `cast_self`) — `cast_operand` for the sandwich (return typed `_OperandT`).
- `return_type` (default `typing.Self`) — `MultiVectorBase` for the impl of overloaded ops,
  `_OperandT` for the sandwich.
- `param_name` (default `rhs`) — `x` for the sandwich (matching `MultiVectorBase.sandwich`'s param).
- `param_annotation` — `_OperandT` for the sandwich param.
- `number_case` — adds arm #2.

**The sandwich** (`generate_graded_type`, `:2085`, Rotor types only): `dispatch_method(spec,
"sandwich", lambda r, x: r * x * r.inverse(), …, param_name="x", return_type=_OperandT,
cast=cast_operand, param_annotation=_OperandT)`. It's a Liskov-compatible override of
`MultiVectorBase.sandwich(self, x: _OperandT) -> _OperandT`. Grade-preserving: the derived closed
form's support is exactly `x`'s grades (the would-be higher grades cancel symbolically), so each arm
builds via `type(x)(…)` and an operand subclass keeps its own type. The generated output shows
`case Vector(): … return typing.cast(_OperandT, type(x)(coeff_e_1=…, coeff_e_2=…))` with `x0/x1/x2`
cse temps.

The full `G_n` class (`generate_class`) does **not** use `dispatch_method` — it's dense over all
blades, so its `bilinear`/`linear` inner builders (`:1522`, `:1543`) emit a single closed form with
an `isinstance` guard that coerces a foreign rhs to `Gn` and delegates. `dispatch_method` is
specifically the *graded* dispatch table.

---

## 5. `product_overload_stubs` — the precise-typing feature

`product_overload_stubs` (`:1068`) emits the `@typing.overload` signatures placed *just before* an
overloaded product/sum method. Each overload returns the **resolved concrete type** so a known-type
call site types precisely (`Vector * Vector -> Rotor`) instead of the imprecise, unsound
`-> Self`. One stub per rhs type:

- `number_case` (optional): an `int | float | sympy.Expr` overload → `product_result(self,
  SCALAR)`'s type (for `*` this scales to `Self`'s type; for `+`/`-` a scalar can narrow, e.g.
  `Bivector + scalar -> Rotor`).
- one per `[SCALAR, *graded_specs(n)]` → each's `product_result`-resolved return type.
- a final `MultiVectorBase` catch-all → the full `G_n` (covers `Gn` / the full class / any other
  operand, which the impl coerces).

Each stub is a `def <method>(self, <param>) -> <ret>: ...` with `@typing.overload` and a body of
just `...` (`ast.Expr(constant(...))`).

**The impl returns `-> MultiVectorBase`, not `-> Self`.** The overloads return sibling types
(`Rotor`, `Bivector`, …) that are **not** subtypes of one another nor of `G_n` — all are siblings
under `MultiVectorBase` — so the implementation's own return annotation must be their one common
supertype, `MultiVectorBase`, to be consistent with (and honest about) its overloads. The old
blanket `-> Self` *claimed* `Vector` while returning a `Rotor`; that was the unsound cast this
feature fixed. In `generate_graded_type` you can see the pairing: `*product_overload_stubs("__mul__",
…)` immediately followed by the `__mul__` impl (`returns=mvb_ann`) and the `dispatch_method(…,
"_geometric_product", …)` it delegates to. The `@overload` stubs are skipped by the doc-region
marker walk (`_is_overload`, §2/§6). **The full rationale and the operator-by-operator return table
live in the sibling reference `tasks/reference/generated-product-typing.md`** — this section is the
mechanical *how it's emitted*; go there for the *why* and the design history.

---

## 6. Doc-region markers — end to end

**Purpose** (from `CLAUDE.md`): the author's *modelviewprojection* Sphinx book `literalinclude`s
slices of gacalc, selecting by `:start-after:` / `:end-before:` anchor comments. Hand-written modules
(`functions.py`, `transforms.py`) carry the `# doc-region-begin/end` markers as ordinary comments;
**generated** modules get them from the generator (§2's machinery).

**Emission recap:** markers are sentinel string-literal statements (`marker()`), injected by
`inject_region_markers` around each class / declaration / instance-variables / method, then rewritten
to `# doc-region-…` comments by `module_source` (with the `declaration` end placed by the
`_insert_declaration_ends` text pass). `@overload` stubs are deliberately **unmarked** (`_is_overload`)
so they don't duplicate the implementation's `<Class> <method> method` region. Basis-constant
assignments (`Cls.e_1 = …`, post-class) are also unmarked. Names are **descriptive and prefix-free
by construction** — NOT SHA1 — with the trailing keyword required (Sphinx matches the first line
*containing* the anchor, so `Vector magnitude` would otherwise also match `magnitude_squared`).

**`check_doc_regions.py` / `make check-regions`** — regenerates first (the outputs are gitignored),
then over every `src/gacalc/*.py` asserts three failure modes, **loud (exit 1), per file**, checked
for begin- and end-markers **separately** (each directive selects on its own marker kind):

1. **Exact duplicate** — a name appearing >1 time (raw `Counter`, not a set — a set-based check
   nearly missed the `x` getter/setter collision); a query always selects the first, orphaning the
   rest.
2. **Prefix collision** — one name is a prefix of another (Sphinx matches the first *containing*
   line, so the shorter pulls the longer's region).
3. **Unbalanced** — a `begin` with no matching `end` or vice versa.

It only counts genuine marker *comments* (`#\s*doc-region-…`), so the bare string `doc-region-begin`
inside this generator's own code or a docstring doesn't false-positive. Run it after touching markers
or the generator.

---

## 7. How to change it

**Add a new algebra (𝒢₄).** One-line edit: append to `ALGEBRAS` (`gen_specialized.py:2227`):

```python
ALGEBRAS = [
    (1, "G", "g1.py"),
    (2, "G", "g2.py"),
    (3, "G", "g3.py"),
    (4, "G4", "g4.py"),
]
```

Then `make generate`. Everything else is derived: `blades_for_dim(4)` yields the 2⁴=16 blades,
`graded_specs(4)` yields `Vector4`/`Bivector4`/`Trivector4`/`Rotor4` (plus a grade-4 quadvector if
you extend `graded_specs` — it currently stops at trivector), the products/overloads/markers all fall
out. The worked `G4` example is in `README.md`. Downstream, code that enumerates the specialized
algebras must add `G4` to keep it covered — notably `tests/test_conformance.py` (its
`SPECIALIZED = {1: G, 2: G, 3: G}` map and the `CASES` parametrization, which import
`from gacalc.g4 import G4` directly). `gn.py` does **not** import the specialized modules, so nothing
is needed there.

**Any other change goes in `tools/`** — never in `src/gacalc/`. The recipe (also in `CLAUDE.md`):

1. `make generate` to materialize the current `src/gacalc/{scalar,g1,g2,g3}.py`.
2. Read the *actual* generated source (and a REPL repro) to understand the behavior — the outputs
   may be absent or stale in a fresh checkout because they're gitignored.
3. Make the change in `tools/gen_specialized.py` (domain/GA logic) or `tools/astbuild.py` (node DSL /
   markers), regenerate, and re-run the suite. **A correct change shows up as a `tools/` diff with
   nothing under `src/gacalc/`** — that thin diff is the healthy shape, not a sign work was skipped.
4. `make check-generated` (regenerates twice, asserts byte-identical — catches a non-deterministic
   generator) and `make check-regions` if you touched markers. `make test` runs the conformance
   suite that guards the generated code against `Gn`.

**Generation cost grows fast** (it runs `Gn`'s eager-`simplify` symbolic ops): sub-second for
𝒢₁/𝒢₂, tens of seconds for 𝒢₃, **minutes for 𝒢₄**. `make check-generated` is ~30s, dominated by 𝒢₃,
which is why it's a make/CI target and *not* part of the default `pytest` run. If you add 𝒢₄, expect
`make generate`/`check-generated`/CI to slow substantially.

**Determinism is a hard requirement.** `sympy.cse` and dict iteration must produce byte-identical
output across runs, or `check-generated` fails. `main()` writes files in a fixed order and the
builders iterate blades in canonical `blades_for_dim` order precisely to keep it deterministic.
