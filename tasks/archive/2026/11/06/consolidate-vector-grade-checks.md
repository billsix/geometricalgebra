# Consolidate the "arguments must be vectors (grade 1)" check behind one procedure

**Created:** 2026-10-22 · **Completed:** 2026-11-06 (superseded; William Emerison Six <billsix@gmail.com>)

Merged into `tasks/archive/2026/11/06/reuse-existing-vector-check.md`. The task was created to promote
`measure._require_vectors` to a shared home and route the duplicated vector checks through it. A
second task asking for the same thing was written 2026-11-04 without a link to this one. The two were
merged into the newer doc, which carries this doc's site inventory (the convert / judgment /
leave-alone buckets), its one decision (the shared check lives in `base.py`, decided 2026-10-22), and
its three open questions (settled there). No code was changed under this task.
