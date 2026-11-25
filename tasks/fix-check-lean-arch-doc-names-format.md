# Make `tools/check_lean_arch_doc_names.py` pass `make format`

**Status:** proposed — needs go-ahead **Priority:** 4 **Difficulty:** 1
**Created:** 2026-11-25 (William Emerison Six <billsix@gmail.com>)

## BLUF

`make format` exits nonzero on `master` because of one file, `tools/check_lean_arch_doc_names.py`: ten `E501` (line too long, 90 to 108 columns, mostly in its module docstring and comments) and one `T201` (`print` at line 82). CI's `check-format` job is `make format` followed by `git diff --exit-code`, so it fails the same way, and ruff also reformats the file each run (a 6-line diff). Done = `make format` exits 0 with no change to a tracked file.

## Context

- Found 2026-11-25 while running `make format` for the lit-grapher work in `src/gacalc/gl/grapher3d.py`; nothing in that work touches the file. It came in with the Lean fit cleanup (`git log -- tools/check_lean_arch_doc_names.py`: `c3d9ba7`, then `52b504b`, "formatted").
- Read first: `CLAUDE.md` ("Coding standard (Python)": line length is the formatter's job for code; prose in a docstring is reflowed by hand, paragraph-wise, never one orphaned word).
- Fix shape: wrap the docstring and comments paragraph-wise to 88 columns, and write output with `sys.stdout.write` as the other tools do (or `# noqa: T201` with the reason, if a `print` is the point of a command-line report; `tools/` has examples of both). Then run `make format` twice: the second run must change nothing.
