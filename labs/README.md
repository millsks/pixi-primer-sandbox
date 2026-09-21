---
type: Reference
title: Lab Starter Files
description: One directory per hands-on lab in the primer — starter files (scripts, fixtures, pyproject.toml) that a guide expects to find, ready to copy into sandbox/ before following the guide.
tags: [pixi, labs, fixtures]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T02:30:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T02:30:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: primer-docs
    resource: ../docs/
    title: The guides these labs belong to
---

# Lab Starter Files

Each directory here is the starting state of one lab. Nothing in `labs/` is ever run in
place — you copy it into `sandbox/` (gitignored) and work there, so `labs/` stays pristine
and a lab can be restarted from scratch at any time:

```sh
cp -r labs/<lab> sandbox/ && cd sandbox/<lab>
# then follow the matching guide from its "Setup" section
```

Restart a lab:

```sh
rm -rf sandbox/<lab> && cp -r labs/<lab> sandbox/
```

| Lab | Guide | Starter files |
|---|---|---|
| [`hello-pixi/`](hello-pixi/README.md) | [Getting Started](../docs/pixi-getting-started.md) | — |
| [`manifest-lab/`](manifest-lab/README.md) | [Manifest Reference](../docs/pixi-manifest-reference.md) | `pixi.toml` exercising every table |
| [`deps-lab/`](deps-lab/README.md) | [Managing Dependencies](../docs/pixi-dependencies.md) | `pyproject.toml` + `src/deps_lab/` for the editable-install step |
| [`tasks-lab/`](tasks-lab/README.md) | [Pixi Tasks](../docs/pixi-tasks.md) | `scripts/where.py`, `in.txt` |
| [`envs-lab/`](envs-lab/README.md) | [Features and Environments](../docs/pixi-features-environments.md) | `tests/test_smoke.py` |
| [`lock-lab/`](lock-lab/README.md) | [Lockfile and Reproducibility](../docs/pixi-lockfile-updates.md) | — |
| [`platform-lab/`](platform-lab/README.md) | [Multi-Platform Workspaces](../docs/pixi-multi-platform.md) | — |
| [`act-lab/`](act-lab/README.md) | [Activation, Shells, Env Vars](../docs/pixi-activation-shell.md) | `scripts/env.sh` |
| [`scripts-lab/`](scripts-lab/README.md) | [Scripts and pixi exec](../docs/pixi-scripts-exec.md) | — |
| [`config-lab/`](config-lab/README.md) | [Pixi Configuration](../docs/pixi-config.md) | — |
| [`import-lab/`](import-lab/README.md) | [Importing Existing Environments](../docs/pixi-import-guide.md) | one fixture per source format |
| [`ci-lab/`](ci-lab/README.md) | [CI with GitHub Actions](../docs/pixi-ci-github-actions.md) | `.github/workflows/ci.yml`, `Dockerfile` |
| [`build-lab/`](build-lab/README.md) | [Building Conda Packages](../docs/pixi-build-packages.md) | `pyproject.toml`, `src/build_lab/`, `package.toml` |

[Global Tools](../docs/pixi-global-tools.md) and [Troubleshooting](../docs/pixi-troubleshooting.md)
have no lab directory: the first operates on `~/.pixi`, the second is a reference.

Labs whose starter column is "—" still have a directory so every guide starts the same way;
their `README.md` is the only file.
