---
type: Playbook
title: Global Tools with pixi global
description: Install command-line tools user-wide with pixi global — isolated environments, exposed binaries, the pixi-global.toml manifest, sync, update, and uninstall — as the replacement for pipx, brew-for-CLIs, and uv tool.
tags: [pixi, global, cli-tools, pipx-replacement, playbook]
status: draft
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-global-help
    resource: cli:pixi/0.81.0/global --help
    title: pixi global --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-global-install-help
    resource: cli:pixi/0.81.0/global install --help
    title: pixi global install --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-global
    resource: https://pixi.prefix.dev/latest/global_tools/introduction/
    title: pixi — global tools
---

# Global Tools with pixi global

Written against `pixi 0.81.0` help output; the install steps below modify `~/.pixi` on your
machine, so they were **not** executed as part of generating this document (`status: draft`).
Run them, then flip `status` to `stable` and add a `verified` line.

`pixi global` installs each tool into its own environment under `~/.pixi/envs/<name>/` and
symlinks chosen executables into `~/.pixi/bin/` (already on `PATH` from the pixi installer).
Tools never see each other's dependencies. This is the pixi answer to `pipx`, `uv tool`, and
`brew install` for developer CLIs.

Everything is recorded in a manifest, `~/.pixi/manifests/pixi-global.toml`, so the whole tool
set is reproducible on a new machine.

---

## 1. Install a tool

```sh
pixi global install ripgrep
rg --version
pixi global list
```

`pixi global list` shows environments, their packages, and which binaries are exposed.
Pin versions with a MatchSpec exactly as in `pixi add`:

```sh
pixi global install "pre-commit>=4"
pixi global install "python=3.14"          # a global python3.14 / python binary
```

---

## 2. One environment, several packages

Some tools need plugins or companions in the same environment (a Jupyter kernel and its
extensions; pytest and its plugins). Use `--environment` to group, `--expose` to pick binaries:

```sh
pixi global install --environment jupyter --expose jupyter --expose jupyter-lab jupyter jupyterlab polars
pixi global install jupyter --with polars       # shorthand: extra deps, only jupyter exposed
```

Add to an existing environment later:

```sh
pixi global add --environment jupyter ipywidgets
pixi global remove --environment jupyter polars
```

---

## 3. Exposing and renaming binaries

```sh
pixi global install --environment py312 --expose python3.12=python "python=3.12"
pixi global expose add py312=python --environment py312
pixi global expose remove py312
```

`--expose NAME=BINARY` maps a name on your `PATH` to an executable inside the environment,
so several Python versions can coexist as `python3.12`, `python3.13`, `python3.14`.

---

## 4. The global manifest

```sh
pixi global edit           # opens ~/.pixi/manifests/pixi-global.toml in $EDITOR
cat ~/.pixi/manifests/pixi-global.toml
```

```toml
version = 1

[envs.ripgrep]
channels = ["conda-forge"]
dependencies = { ripgrep = "*" }
exposed = { rg = "rg" }

[envs.jupyter]
channels = ["conda-forge"]
dependencies = { jupyter = "*", jupyterlab = "*", polars = "*" }
exposed = { jupyter = "jupyter", jupyter-lab = "jupyter-lab" }
```

Edit it by hand, then reconcile installed state with the manifest:

```sh
pixi global sync
```

Commit this file to your dotfiles; `pixi global sync` on a fresh machine rebuilds every tool.

---

## 5. Updating and removing

```sh
pixi global update                 # all environments
pixi global update ripgrep         # one
pixi global tree jupyter           # dependency tree of one env
pixi global uninstall ripgrep      # remove the environment and its exposed binaries
```

---

## 6. Cleanup (undo this lab)

```sh
pixi global uninstall ripgrep jupyter py312
pixi global list
```

---

## Key takeaways

- One tool, one environment, only the binaries you expose on `PATH`.
- `~/.pixi/manifests/pixi-global.toml` + `pixi global sync` = reproducible tool set.
- `pixi global` is for tools you use across projects. Project tooling (ruff, mypy, pytest) belongs in the project's `pixi.toml` so its version is locked with the code.
