# A second external source outline: Illustrative Mathematics' Geometry course

**Status:** ready — the three questions were answered 2026-11-27 (see "Decisions"); nothing entered yet
**Priority:** 5
**Difficulty:** 4
**Created:** 2026-11-27 (William Emerison Six <billsix@gmail.com>)

## BLUF

The book reads one geometry textbook today, a printed one the maintainer has to page through.
Illustrative Mathematics (IM) publishes a high-school Geometry course online under a Creative
Commons licence. This task enters the newest edition's outline as a second source,
`tasks/sources/im-geo.toml`, to cite from the book and to draw topics from, so that
`/source-coverage` shows which of its lessons the book covers. Done means the outline file exists
with the course's units and lessons, its licence and required attribution in the banner, and the
book pages that already cover a lesson tagged.

## Context

**Read first:**

- the external-source-outlines.md reference doc of github.com/billsix/runClaudeInContainer: the
  file format, the permanent entry IDs, what may be committed, the `covers:` tag, the report;
- `tasks/sources/pearson-geo.toml`, the first outline and the worked example (its banner says where
  each field came from);
- `tasks/reference/high-school-geometry-objects.md`, the vector construction of each textbook
  object;
- `tasks/archive/` → `external-source-outline-pearson-geometry.md` (in `tasks/` until archived),
  the record of how the first outline was made.

**Why a second source.** The maintainer decided on 2026-11-27 that Illustrative Mathematics
Geometry becomes a second source (decision 3 of github.com/billsix/runClaudeInContainer's task
`external-source-outlines-and-coverage-tracking.md`), for citing and for inspiration. Being online
makes it easier to use than the printed textbook: an agent can read it, and a citation is a link.
The Pearson textbook stays the one a student is likely to have had, cited by page.

**The two editions** (IM's terms of use, https://www.illustrativemathematics.org/terms-of-use,
"Effective as of May 21, 2026", read 2026-11-27):

- first edition, "IM K–12 Math" (© 2019–2021): **CC BY 4.0**. Suggested attribution: "Based on IM®
  K–12 Math authored by Illustrative Mathematics and licensed under CC BY 4.0." It is hosted at
  https://im.kendallhunt.com/ (found by search; the Geometry pages have not been opened);
- second edition, "IM TK–12 Math v.360" (© 2024): **CC BY-NC 4.0**; commercial use needs written
  permission.
- The IM name and marks are outside both licences.

**What is not known yet.** Nobody has opened the course's own pages. Its unit and lesson list, its
lesson numbering, whether each lesson names its Common Core standards, and whether the Geometry
course's pages state the same licence as the terms page are all to be read from the source when
this task starts. Do not fill any of it from memory.

**Related, and separate:** github.com/billsix/impo
`tasks/research-illustrative-mathematics-geometry-build.md` asks whether impo can *build* the
course as a book, and which edition's licence impo can live with. The maintainer deferred it
(2026-11-27) and left the licence question there. An outline needs only the course's table of
contents, so this task does not wait for that one.

## Decisions (William Emerison Six <billsix@gmail.com>, 2026-11-27)

1. **Edition: the newest, v.360, whatever its licence** ("using the newest version regardless of
   license"). This overrides the agent's recommendation of the first edition.
2. **Depth: units and lessons only** on the first pass (the agent's recommendation, accepted).
   Topics inside a lesson are added later, as the maintainer reads.
3. **Key: `im-geo`** (the agent's suggestion, accepted). The banner pins the edition, so the key
   does not name it.

**What the v.360 licence means here.** CC BY-NC 4.0 allows sharing and adapting for
non-commercial purposes with attribution. An outline (titles, numbers, links, own-words
summaries) and a citation do not depend on the licence at all. Quoting or adapting the course's
own text or figures in the book does: the book's prose is GFDL-1.3, which permits commercial use,
so non-commercial material cannot simply be folded into it. That is not decided by this task.
Until the maintainer decides it, treat v.360 like the Pearson textbook when writing book pages:
cite and link, write in the project's own words, and quote nothing at length. Record this in the
outline's banner.

## Plan

- [x] The maintainer answers the open questions (2026-11-27).
- [ ] Find and read the v.360 Geometry course online: confirm on the course's own pages that it
      is the newest edition and what licence it states, and record each URL opened. If the
      v.360 Geometry course turns out not to be readable online, stop and say so; do not fall
      back to the first edition without asking.
- [ ] Write `tasks/sources/im-geo.toml`: banner (edition, licence, attribution, the URL and date
      read), then units and lessons with their numbers and titles. An online course has no page
      numbers; record each lesson's URL in a field instead, if the format needs one (add it to the
      conventions doc first).
- [ ] If the lessons name their Common Core standards, enter them in `standards`, and add the same
      codes to the matching `pearson-geo` entries where the match is plain (decision 4 of the same
      runClaudeInContainer task).
- [ ] Tag the book pages that already cover a lesson, checking each against the page's text.
- [ ] Run `/source-coverage`; fix every problem line; stage.

## Open questions

None open. The three asked on 2026-11-27 are answered under "Decisions".
