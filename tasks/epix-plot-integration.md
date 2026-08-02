# Import epix-mirror at container build time for plot generation

**Status:** proposed — not started (blocked on the repo URL — see Open questions)
**Priority:** 7
**Difficulty:** 6
**Created:** 2026-06-13

## Goal

At **container build time**, pull in Bill's **epix-mirror** code from GitHub and
build/install it into the gacalc image, so it's available as a plot-generation
tool. The plots are for the project's visual material — the **notebooks** and any
**book** — and the integration should work whether docs are built with **Sphinx**
or via a **LaTeX port** (gacalc has no Sphinx setup yet; see
`tasks/docstrings-for-sphinx.md`).

(epix-mirror is Bill's mirror of ePiX, a C++ library that produces precise
mathematical figures with LaTeX-quality output. A copy is also mounted locally at
`/billopt/epix-mirror`, usable to learn the build before the GitHub URL is given.)

## Plan

- [ ] **Get the GitHub URL from Bill** (pending — see Open questions). Decide
      whether to pin to a commit/tag for reproducible image builds.
- [ ] **Learn the build.** Inspect `/billopt/epix-mirror` (and the upstream repo
      once the URL lands): build system, dependencies (a TeX toolchain + a C++
      compiler at minimum), and what it installs (the `epix` driver/scripts and any
      libraries).
- [ ] **Add it to gacalc's `Dockerfile`.** `git clone <url>` (pinned) at build
      time, build, and install into the image, in the family-template style
      alongside the existing installs. Account for its TeX dependencies.
- [ ] **Wire it into the plot flow.** Work out how epix output fits with gacalc's
      existing plotting: `src/gacalc/nbplotutils.py` and the `notebooks/`
      (`displayg2.py`, `displayg3.py`, `displaymv.py`, `displaygraded.py`,
      `displayrotations.py`), plus the `jupyter.sh` / `percentToIpynb.sh` workflow.
      Decide replace-vs-coexist with the current plotting and where generated
      figures land.
- [ ] **Keep both doc paths in mind.** Usable from a future Sphinx build *and* a
      LaTeX port (where epix's native LaTeX/eepic output is a natural fit) — don't
      hard-wire it to one.
- [ ] **Document.** Update this task as it progresses; once landed, note the new
      dependency in `CLAUDE.md` / `README` and how to regenerate plots.

## Notes / decisions

- Moved here from modelviewprojection per Bill's decision (this is gacalc's epix
  import; mvp's plotting is a separate concern and got no epix task).
- A local copy of epix-mirror is at `/billopt/epix-mirror` — usable to study the
  build before the canonical GitHub URL arrives.
- This is a **permanent** build-file change (a real plot dependency the image
  should carry), so per the cross-project build-file conventions it needs Bill's
  go-ahead before it lands in the committed `Dockerfile` (this task records intent).
- gacalc has no Sphinx docs build yet (docs live in `README.md`); a LaTeX port /
  Sphinx setup is contemplated in `tasks/docstrings-for-sphinx.md`.

## Open questions

- **What's the epix-mirror GitHub URL?** (Blocking — Bill to provide.)
- Pin to a commit/tag, or track a branch?
- epix output target: pre-rendered PNG/SVG for notebooks, native LaTeX/eepic for a
  book/LaTeX port, or both? How should it coexist with `nbplotutils.py`?
