# Document the code-generation flow (sympy → AST), starting from Gn (done)

**Started:** 2026-08-27 (William Emerison Six <billsix@gmail.com>). **Done:** 2026-11-25.

The maintainer, who knows Lisp macros, asked for reference docs that explain the whole generation flow starting from the sympy code for `Gn`, and said it was unclear whether the generator reads existing code and processes it Lisp-style or generates everything from sympy.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-25)

The audience is contributors: extend `tasks/reference/code-generator-architecture.md` (the module docstring of `tools/gen_specialized.py` already carried the narrative, a pipeline diagram and a doctest). A reader-facing book chapter is written only if the maintainer asks for one.

## Result

- **The answer to the confusion:** the generator **runs** the reference `Gn` once on sympy symbols and keeps the formulas that come out; it never reads or rewrites gacalc source. Sympy defines, the AST emits. `tools/gen_specialized.py`'s module docstring already said so; the contributor map did not.
- **Added to `tasks/reference/code-generator-architecture.md`,** up front: "The one idea: the generator runs `Gn`, it does not read it", with the three places to see each step as running code: the module docstring's doctest, the named tests in `tests/test_generator.py` (one per step: run `Gn`, blades → type, formula → code, nodes → text), and the generated `Vector._geometric_product` in `src/gacalc/g2.py` (its `doc-region-begin Vector _geometric_product method` region). The header date was updated.
- **Not done, by decision:** a book-facing explainer.

No source changed, so no gate beyond reading the cited names back from the tree (they exist).
