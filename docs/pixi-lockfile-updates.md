---
type: Tutorial
title: The Lockfile and Reproducibility
description: What pixi.lock contains, how to verify it is current (pixi lock --check), the difference between --frozen and --locked, safe update workflows, and exporting to conda environment.yml or explicit-spec files.
tags: [pixi, lockfile, reproducibility, ci, export, tutorial]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-lock-help
    resource: cli:pixi/0.81.0/lock --help
    title: pixi lock --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-install-help
    resource: cli:pixi/0.81.0/install --help
    title: pixi install --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-export-help
    resource: cli:pixi/0.81.0/workspace export --help
    title: pixi workspace export --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-lockfile
    resource: https://pixi.prefix.dev/latest/workspace/lockfile/
    title: pixi — lockfile
---

# The Lockfile and Reproducibility

Verified against `pixi 0.81.0`. `pixi.lock` is the contract: given the same lockfile, every
machine on every listed platform installs byte-identical package sets. Commit it. Review it
in PRs like code.

## Setup

```sh
mkdir -p sandbox && cd sandbox
pixi init lock-lab && cd lock-lab
pixi add "python=3.14.*" rich
pixi add --pypi structlog
```

---

## 1. Read the lockfile

```sh
head -30 pixi.lock
grep -c '^- conda:' pixi.lock      # number of conda package records
grep -c '^- pypi:' pixi.lock       # number of PyPI package records
```

Structure (lock format `version: 7`):

```yaml
version: 7
platforms:
- name: osx-arm64
  virtual-packages:
  - __unix=0=0
  - __osx=13.0
  - __archspec=0=m1
environments:
  default:
    channels:
    - url: https://conda.anaconda.org/conda-forge/
    indexes:
    - https://pypi.org/simple
    packages:
      osx-arm64:
      - conda: https://conda.anaconda.org/conda-forge/osx-arm64/python-3.14.7-...conda
      - pypi: https://files.pythonhosted.org/.../structlog-26.1.0-py3-none-any.whl
packages:
- conda: https://conda.anaconda.org/conda-forge/osx-arm64/python-3.14.7-...conda
  sha256: ...
  md5: ...
  depends: [...]
```

Three sections: the `platforms` (with the `system-requirements` the solve assumed, expressed
as virtual packages), one `environments.<name>.packages.<platform>` list per environment ×
platform, and a deduplicated `packages` list with URLs and hashes. Nothing is resolved at
install time.

---

## 2. Is the lock current?

```sh
pixi lock --check ; echo "exit=$?"        # 0: up to date
pixi add attrs --no-install               # pixi add keeps the lock in sync even with --no-install
pixi lock --check ; echo "exit=$?"        # still 0
```

Only a **hand-edit** to the manifest can leave the lock stale. Open `pixi.toml` in an editor
and add `cowpy = "*"` under `[dependencies]`, then:

```sh
pixi lock --check ; echo "exit=$?"        # 1: "lock file not up-to-date with the workspace"
pixi lock                                 # re-solve and rewrite
pixi lock --check ; echo "exit=$?"        # 0 again
pixi remove cowpy
```

`pixi lock` (no flags) re-solves and rewrites the lock without installing — useful after a
hand-edit to the manifest. `--check` is the CI guard: it exits non-zero if the manifest and lock
disagree. `--dry-run` computes without writing.

---

## 3. `--frozen` vs `--locked`

Both flags exist on `pixi install`, `pixi run`, `pixi shell`, and friends.

| Flag | Behaviour when manifest and lock disagree |
|---|---|
| (none) | Re-solve, rewrite `pixi.lock`, install |
| `--locked` | **Error out.** Use in CI: the committed lock must already match. |
| `--frozen` | Install exactly what is in `pixi.lock`, ignore the manifest. Use in Docker builds or when you deliberately want the old lock. |

Hand-edit `pixi.toml` again to add `cowpy = "*"` under `[dependencies]`, then:

```sh
pixi install --locked ; echo "exit=$?"    # fails: "lock file not up-to-date with the workspace"
pixi install --frozen          # succeeds, cowpy ignored
pixi install                   # re-solves, adds cowpy
```

`pixi run --as-is` is shorthand for `--no-install --frozen` when you only want to run and
never write. All three flags also have `PIXI_FROZEN` / `PIXI_LOCKED` / `PIXI_NO_INSTALL`
environment variables, handy in CI.

Remove it before continuing:

```sh
pixi remove cowpy
```

---

## 4. Updating safely

```sh
pixi update --dry-run                 # what would move within current manifest ranges
pixi update --dry-run --json | jq .   # machine-readable
pixi update rich                      # just rich
pixi update -e default -p osx-arm64   # scope to one env / platform
pixi update                           # everything
```

`pixi update` never edits `pixi.toml`. To move a range, use `pixi upgrade` (see
[pixi-dependencies.md](pixi-dependencies.md) §6). Either way, review `git diff pixi.lock`
before committing — the diff shows exactly which package versions changed.

---

## 5. Reinstall from lock

When `.pixi/envs` looks broken (half-written files, a manually deleted package):

```sh
pixi reinstall                 # wipe and rebuild default env from the lock
pixi reinstall -e test         # one environment
pixi reinstall --all
```

Or nuke and let the next `pixi run` rebuild:

```sh
pixi clean
```

---

## 6. Exporting for tools that do not speak pixi

Conda `environment.yml` (manifest specs, not locked versions):

```sh
pixi workspace export conda-environment
pixi workspace export conda-environment --from-lock-file -e default -p linux-64 env-linux.yml
pixi workspace export conda-environment --no-pypi              # drop the pip: section
```

Conda explicit spec (`@EXPLICIT` URL lists — fully locked, `conda create --file`-compatible):

```sh
pixi workspace export conda-explicit-spec --ignore-pypi-errors ./explicit/
ls explicit/                                   # default_osx-arm64_conda_spec.txt, ...
head -5 explicit/default_osx-arm64_conda_spec.txt
```

Writes one file per environment × platform. Explicit specs cannot carry PyPI packages;
without `--ignore-pypi-errors` the export refuses if any are locked, with it they are dropped
with a warning. This is the right artifact to hand to an
air-gapped or conda-only consumer.

---

## 7. Cleanup

```sh
cd .. && rm -rf lock-lab
```

---

## Key takeaways

- Commit `pixi.lock`. Diff it in review.
- CI: `pixi install --locked` (or `pixi lock --check`) so a stale lock fails fast.
- Docker / air-gapped: `pixi install --frozen` or an explicit-spec export.
- `update` refreshes within ranges; `upgrade` moves ranges. Dry-run both.
