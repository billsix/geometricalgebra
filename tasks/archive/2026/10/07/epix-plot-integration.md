# Import epix-mirror at container build time for plot generation

**Status:** DONE (2026-10-07); archived 2026-10-07 on the maintainer's say-so ("looks great both in HTML and
PDF" … "6) yes"). The image integration (2026-10-06) and the Python front-end + all nine rotation figures
(2026-10-07) are in; the follow-on figure work is `tasks/book-epix-figures.md`. **Fully unblocked 2026-10-06:** the GitHub URL
(`https://github.com/billsix/epix-mirror`, 2026-10-04) *and* the pin — the maintainer wants the image to
pull **commit `ebf3ca607ae6c1d4fa307e8b0359960d875d219c`** (GitHub `master` as of 2026-10-06, the merge of
epix-mirror's `containerFileRework` branch).
**Priority:** 7
**Difficulty:** 5 (was 6 — by then the epix side shipped host-runnable install scripts and a Meson build, so
the "learn the build" step is done; see Notes)
**Created:** 2026-06-13
**Updated:** 2026-10-06 (William Emerison Six <billsix@gmail.com>, via agent) — pin recorded; plan made
concrete against the pushed epix-mirror layout. Earlier: 2026-10-04 URL recorded, local clone path corrected.

## Goal

At **container build time**, pull in the maintainer's **epix-mirror** code from GitHub and
build/install it into the gacalc image, so it's available as a plot-generation
tool. The plots are for the project's visual material — the **notebooks** and any
**book** — and the integration should work whether docs are built with **Sphinx**
or via a **LaTeX port** (gacalc's Sphinx book is described in
`tasks/reference/book-and-docs-pipeline.md`).

(epix-mirror is the maintainer's mirror of ePiX, a C++ library that produces precise
mathematical figures with LaTeX-quality output. A copy is also mounted locally at
`/mnt/sda1/epix-mirror` (a sandbox path; by 2026-10-04 it carried its own `Dockerfile`, `Makefile`,
and `CLAUDE.md`), usable to learn the build before the GitHub URL is given.)

## Plan

- [x] **Get the GitHub URL from the maintainer** — `https://github.com/billsix/epix-mirror`
      (2026-10-04). **Pin decided 2026-10-06:** commit `ebf3ca607ae6c1d4fa307e8b0359960d875d219c`.
- [x] **Learn the build** (2026-10-06, from the pushed tree — see Notes): Meson, `meson setup build
      --prefix=/usr/local && meson install -C build`; installs `epix`/`elaps`/`flix`/`laps` + `libepix.a` +
      headers + man pages + samples. Runtime: `g++` (the `epix` driver compiles each `.xp`), `bash`,
      `latex`, `ps2epsi`; `gs` for eps→png, ImageMagick for animations. The tree's own
      `entrypoint/01-install-base.sh` / `02-install-render.sh` are host-runnable dnf group scripts.
- [x] **Add it to gacalc's `Dockerfile`** (2026-10-06) behind `USE_EPIX` (`?= $(if $(filter
      1,$(MINIMAL_IMAGE)),0,1)` in the Makefile, `ARG USE_EPIX=0` + `ARG EPIX_COMMIT=ebf3ca6…` in the
      Dockerfile). **Fetched with git** (the maintainer's choice over a tarball): `entrypoint/install-epix.sh`
      does a shallow `git fetch --depth 1 origin $EPIX_COMMIT` + detached checkout, `meson setup`/`meson
      install` into `/usr/local`, removes the build dir and `.git`, keeps the source at `/opt/epix-src`.
      `entrypoint/06-install-epix.sh` installs git, meson/ninja/g++/binutils, ghostscript, ImageMagick and
      the TeX set epix's own `02-install-render.sh` names (overlap with `03-install-notebook-tex.sh` is a
      dnf no-op; listed in full so an epix-only image has `latex`). Placed before `COPY src` for cache
      ordering. Everything lands in committed layers at build time; the pin makes the layer
      reproducible; the installed tools run offline.
- [x] **Replace-vs-coexist decided (2026-10-06, maintainer): coexist.** `nbplotutils.py` (matplotlib)
      stays for the interactive notebooks; ePiX is the book's LaTeX-native figure source.
- [x] **Wire the first book figure (2026-10-07).** The maintainer wanted the figures written with the
      **Python** front-end, not `.xp`, so `install-epix.sh` from then on also builds the nanobind extension (via
      epix-mirror's own `build_py.sh`, which is why the tree is fetched to `/epix` — then moved to
      `/opt/epix-src` before the editable install: the maintainer's host build failed on `import epix` from the
      Dockerfile's cwd `/`, where the bare `/epix` directory shadowed the package as a namespace package) and installs the `epix`
      package editable into `/venv` (`python3-devel` added to `06-install-epix.sh` for `Python.h`).
      `book/figures/epix/rotate_goal.py` (jupytext percent, epix-notebook style) rebuilds the
      `rotate-goal` figure; `tools/render_epix_figures.py` (one fresh process per figure) writes
      `_static/epix/rotate-goal.{pdf,png}` from `docs.sh`; `rotate.rst` + `proof-rotate.rst` reference
      `_static/epix/rotate-goal.*`. Pipeline documented in `tasks/reference/book-and-docs-pipeline.md`.
- [x] **Port the remaining eight (2026-10-07, maintainer: "do that for the remaining svgs").**
      `rotate1.py`–`rotate8.py` share `_rotation_scene.py` (β, θ, r, disc + axes, `vector`/`wedge`/
      `right_angle_marker`/`leg` helpers) so the sequence agrees with the goal figure and the last step
      lands on `r(a;θ)`; `proof-rotate.rst` references `_static/epix/rotateN.*`. Dark mode (maintainer's
      report): the `pngalpha` PNGs were transparent, so each figure defines `BACKGROUND = "#f2f2f2"` (the
      disc fill) and the renderer flattens the HTML PNGs onto it with ImageMagick. Gotcha: `epix.label_angle`
      takes radians. The nine CC0 SVGs under `_static/cc0/williamesix/` were `git rm`'d (the maintainer's
      choice); the Stephan Kulla unit-circle SVG stays (not ours to redraw).
- [ ] **Keep both doc paths in mind.** Usable from a future Sphinx build *and* a
      LaTeX port (where epix's native LaTeX/eepic output is a natural fit) — don't
      hard-wire it to one.
- [x] **Document** the dependency: `CLAUDE.md` ("ePiX in the image" bullet + the lean-image flag list).
- [x] **Document** how to regenerate the book figures: `tasks/reference/book-and-docs-pipeline.md`
      ("ePiX figures") — `make docs` renders them; `python tools/render_epix_figures.py [NAME]` in the
      image renders one by hand.

## Chronology (harvested from the branch history before the squash)

1. 2026-06-13 filed (moved here from modelviewprojection); blocked on the GitHub URL until 2026-10-04.
2. 2026-10-06 the maintainer pushed epix-mirror and chose the pin (`ebf3ca6`, GitHub `master`) and
   `git` as the fetch method; "coexist" decided for the plotting question.
3. 2026-10-06 the image half: `USE_EPIX` flag, `06-install-epix.sh` + `install-epix.sh` (shallow fetch of
   the pin, Meson install), `install-lean.sh`'s no-git note widened. Verified nested: pin logged, `hello.xp`
   rendered, 696 tests, lean permutation without epix.
4. 2026-10-07 the maintainer asked for the figures in **Python**, not `.xp`: the nanobind extension built
   in the image, `epix` installed editable in `/venv`, the first figure (`rotate-goal`), the render tool,
   the `docs.sh` hook, the `.*` figure references. The maintainer's host build then failed on `import epix`
   from the Dockerfile's cwd `/` — the bare `/epix` tree shadowed the package as a namespace package —
   fixed by moving the tree to `/opt/epix-src` before the editable install; the README gained its
   container-build section with the flag table.
5. 2026-10-07 the remaining eight proof figures via `_rotation_scene.py`; the dark-mode fix (HTML PNGs
   flattened onto the disc fill); the nine CC0 SVGs removed; `epix.label_angle` found to take radians.
6. 2026-10-07 follow-on umbrella `book-epix-figures` filed with three steps; then the maintainer's two
   rules — every argument by keyword (`tools/check_epix_keywords.py`, a `make format` gate step) and every
   binding typed (`fig: PendingFigure`) — applied to all ten figure files, eepic oracle byte-identical.
7. 2026-10-07 archived on the maintainer's approval of the HTML and PDF.

## Verification (2026-10-06, nested in the runClaudeInContainer sandbox)

| Check | Result |
| --- | --- |
| `make image USE_LEAN=0 USE_EMACS=0` (ePiX on; Lean/Emacs trimmed — the diff touches neither) | built; the ePiX layer logged `epix-mirror at ebf3ca607ae6c1d4fa307e8b0359960d875d219c` and Meson installed 194 files under `/usr/local` |
| tools present | `epix`/`elaps`/`flix`/`laps` on PATH, `libepix.a` + `epix.h` installed, source at `/opt/epix-src` with `.git` removed |
| render `samples/hello.xp` in the image | `epix` → eepic; `elaps --pdf` → `hello.pdf` (4.6 KB) through latex → dvips → ps2epsi → epstopdf |
| gacalc gate (`make test`'s run line) | **696 passed** |
| `make image MINIMAL_IMAGE=1` (flag-off permutation) | built, 2.47 GB; `epix`, `git` and `meson` all absent — the `USE_EPIX` gate holds. The ePiX-enabled image (Lean/Emacs still off) is 3.96 GB |

## Follow-on

`tasks/book-epix-figures.md` (umbrella, 2026-10-07): the same figure pipeline applied to the
vector-addition, projection (2D, result + derivation) and 3D-projection sections, three step tasks.
Two rules landed at the end of this task and carry forward there: every argument by keyword
(`tools/check_epix_keywords.py`, a `make format` gate step) and every binding typed (`fig: PendingFigure`).

## Notes / decisions

- **What the 2026-10-06 push unlocked (epix-mirror `ebf3ca6`).** (a) The build is documented and
  scripted: `Dockerfile` + `entrypoint/01-install-base.sh`/`02-install-render.sh` + `meson.build` are the
  whole recipe, and the dnf lists are host-runnable, so gacalc's Dockerfile can reuse them rather than
  guess. (b) The Python front-end (`python/epix`, nanobind) is installable editable with `uv pip` and its
  `Figure` rasterizes **lazily** — building a figure needs only `libepix`; PNG needs TeX + `gs`. That
  makes an `import epix` from a gacalc notebook viable without dragging the render stack into every
  code path. (c) `MINIMAL_IMAGE` flags exist on the epix side, so what gacalc installs can mirror
  exactly the groups it wants (library + drivers; rendering stack only where the book/notebooks render).
  (d) The library builds warning-free at `-Wall -Wextra -Wpedantic` and a real `Complex::operator!=`
  recursion bug is fixed — the pinned commit is a better base than the June tree.
- **Recommendation for open question 3 (coexist, not replace):** keep `nbplotutils.py` (matplotlib) for
  the interactive notebooks; add epix as the **book's** figure source where LaTeX-native output pays —
  `.xp` sources under `book/figures/epix/`, rendered at `make docs` to PDF (`elaps --pdf`, for the
  LuaLaTeX build) and to SVG/PNG for HTML (`gs` from the eps). Whether to also expose the Python
  `epix` package in the gacalc venv can be a second step once a first figure is in the book.

- Moved here from modelviewprojection per the maintainer's decision (this is gacalc's epix
  import; mvp's plotting is a separate concern and got no epix task).
- A local copy of epix-mirror is at `/mnt/sda1/epix-mirror` — usable to study the
  build before the canonical GitHub URL arrives.
- This is a **permanent** build-file change (a real plot dependency the image
  should carry), so per the cross-project build-file conventions it needs the maintainer's
  go-ahead before it lands in the committed `Dockerfile` (this task records intent).
- gacalc has a Sphinx book ("Geometry 2") built with `make docs`; its pipeline is
  documented in `tasks/reference/book-and-docs-pipeline.md`.

## Open questions

1. ~~What's the epix-mirror GitHub URL?~~ **Answered 2026-10-04:** `https://github.com/billsix/epix-mirror`.
2. ~~Pin to a commit/tag, or track a branch?~~ **Answered 2026-10-06:** pin to commit
   `ebf3ca607ae6c1d4fa307e8b0359960d875d219c` (William Emerison Six <billsix@gmail.com>).
3. ~~epix output target / coexistence with `nbplotutils.py`?~~ **Answered 2026-10-06 (William Emerison
   Six <billsix@gmail.com>): coexist** — matplotlib for the notebooks, ePiX for the book's LaTeX-native
   figures (PDF for LuaLaTeX, SVG/PNG for HTML).
