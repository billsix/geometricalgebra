# Add `image-export` / `image-import` Makefile targets

**Created:** 2026-06-13 · **Completed:** 2026-06-16

## What was done

The OCI-image save/load targets that modelviewprojection already had were added, so the built image
can be archived to a tar (to move it to an offline machine, or snapshot a known-good build) and
reloaded without a rebuild:

```make
.PHONY: image-export
image-export: ## export the OCI image to a timestamped tar in the repo root
	$(CONTAINER_CMD) save $(CONTAINER_NAME) -o $(CONTAINER_NAME)-$(shell date +%m-%d-%Y_%H-%M-%S).tar

.PHONY: image-import
image-import: ## import an OCI image tar: make image-import FILE=foo.tar
	$(CONTAINER_CMD) load -i $(FILE)
```

## Decisions

- **Three improvements over mvp's copy** (github.com/billsix/modelviewprojection `Makefile`):
  `$(CONTAINER_CMD)` instead of a hardcoded `podman`, both targets `.PHONY`, and tighter help text.
- **The artifacts are gitignored** (`gacalc-*.tar` in `.gitignore`, commented "large, never commit");
  `podman save` writes a multi-hundred-MB tar to the repo root, and mvp's copy had lacked this.
- **No `image` prerequisite**, as in mvp: `make image-export` errors clearly when no image is built
  instead of silently starting a long rebuild.
- `podman save`/`load` start no container, so they need no `--cgroups=disabled` and run nested.
- `image-import` requires `FILE=` (`make image-import FILE=gacalc-06-13-2026_12-00-00.tar`); without it
  `podman load -i` errors, which was judged acceptable, and the optional empty-`FILE` guard was not
  added.
