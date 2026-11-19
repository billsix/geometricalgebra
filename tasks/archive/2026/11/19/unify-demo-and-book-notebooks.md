# Why the demo and book notebooks differ, and a plan to unify them (both able to sit in the book)

**Created:** 2026-11-18, spun off by decision 1 of
`tasks/archive/2026/11/18/notebooks-like-displaymv.md`. The maintainer said not to start it until
told to.
**Done:** 2026-11-19.

The maintainer started it on 2026-11-19 (William Emerison Six <billsix@gmail.com>): "this is a book
to learn from, but I also want the students to be able to run the notebooks themselves, like a
graphic calculator. So I see no reason for two directories". They also asked how the notebooks'
import paths should work, and noted that not every notebook has to be in the book.

- **The finding** measured every difference between the two directories and why each existed. It
  showed that nothing needed two directories: every essential difference follows from a notebook's
  role. It also covered the cwd-relative `sys.path` imports, and why package data was not the fix
  for them. It is now `tasks/reference/demo-and-book-notebooks.md`, rewritten to the merged state.
- **The plan** became `tasks/archive/2026/11/19/notebooks-one-directory.md`. The maintainer
  answered its four questions the same day, and it was carried out the same day.
