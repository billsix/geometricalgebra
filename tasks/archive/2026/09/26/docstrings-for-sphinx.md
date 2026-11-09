# Add docstrings everywhere, rendered well by the book's autodoc

**Created:** 2026-06-13 · **Completed:** 2026-09-26 (branch `sphinxDocstringUpdates`, squashed into
`85f4bdf`, merged in `760ab6c`; William Emerison Six <billsix@gmail.com>)

Every symbol the book's autodoc renders, and every generated grade-specialized method, got a
Google-style (`sphinx.ext.napoleon`) docstring that renders cleanly. Durable build-pipeline facts
were harvested into `tasks/reference/book-and-docs-pipeline.md`; this file is the lean work record.

## What was done (chronological)

1. **Coverage sweep, docutils rendering and config fixes:** `functions.py` / `nbplotutils.py`
   docstring coverage; the bare `|` / `` ` `` tokens that drove substitution warnings were wrapped;
   the ₙ-glyph luaotfload fallback; `autodoc_typehints = "none"` and the full `api.rst` `automodule`
   set. `make test` 649 passed, `make docs` exit 0.
2. **Full napoleon-Google rewrite of `base.py` + `gn.py`** — the maintainer's "full Google" decision:
   `Args:` / `Returns:` / `Raises:` / `Yields:` on every method including trivial ones, existing
   doctests moved under `Example:`, and real summary lines written where there were none (`is_scalar`
   was `""" """`; several were citation-only). Also the public module-level functions.
3. **Grade-specialized generated docstrings:** the ~185 `CUSTOM_METHOD_DOCS` entries and 7 `_*_doc`
   callables in `tools/gen_specialized.py` were converted to the same style (base docstrings copied
   into generated methods were already Google; the hand-written per-grade ones were not). `Args:`
   names match the generated signatures; type tokens appear in `Returns:` only where grade-preserving
   and certain, prose elsewhere, since grade-changing ops resolve to different types per dimension
   (`tasks/reference/generated-docstrings.md`).
4. **`book/docs/conf.py` E501:** the 89-column `\directlua{...}` preamble line inside an `r"""..."""`
   string was exempted via `pyproject.toml` `per-file-ignores`; an inline `# noqa` was impossible
   there and restructuring the preamble was rejected.
5. **Ambiguous cross-references:** the first `make docs` after the rewrite emitted 8 "more than one
   target found" warnings for `ComposableFunction` / `InvertibleFunction`, which are re-exported by
   both `functions` and `transforms`. The 4 `base.py` `Returns:` tokens (project / reject / reflect /
   identity) were qualified to the canonical `gacalc.functions.*`, bringing it to 0.

## Verification

- `make docs` (`BUILD_DOCS` image, nested): exit 0, 102-page `geometry2.pdf`, 0 substitution /
  missing-glyph / undefined-hyperref / ambiguous-cross-ref warnings; the ~14 remaining warnings were
  benign (scit font shape, Jupyter-kernel TCP, rounded-box packages).
- `make test` / full `pytest`: 649 passed, including 170 doctests (core + g1/g2/g3).
- g2 and g3 byte-identical across two generations; `ruff check .` clean repo-wide.

Related: `tasks/reference/symbolic-equality.md` (the "a multivector never `==` a bare number"
gotcha), `tasks/reference/code-generator-architecture.md` (the base → generated docstring copy path),
and the coverage sibling `tasks/archive/2026/09/26/generate-missing-docstrings.md`.
