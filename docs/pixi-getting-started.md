---
type: Tutorial
title: Getting Started with Pixi
description: Install pixi, create a first workspace with pixi init, add Python and a library, run commands, and understand what pixi.toml, pixi.lock, and .pixi/ each contain.
tags: [pixi, conda, getting-started, tutorial]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-help
    resource: cli:pixi/0.81.0/--help
    title: pixi --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-init-help
    resource: cli:pixi/0.81.0/init --help
    title: pixi init --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-basic
    resource: https://pixi.prefix.dev/latest/tutorials/python/
    title: pixi — Python tutorial
---

# Getting Started with Pixi

Verified against `pixi 0.81.0`. Pixi is a package manager and task runner built on
the conda ecosystem (rattler) with first-class PyPI support (uv). One manifest
(`pixi.toml`), one lockfile (`pixi.lock`), one environment directory (`.pixi/`).

Lab conventions used across this primer:

- Every lab creates its workspace under `sandbox/` at the repo root. `sandbox/` is gitignored.
- `pixi init` always creates the manifest — never hand-write `pixi.toml` from scratch.
- Commands are shown for zsh/bash. Quote MatchSpecs containing `*` (`"python=3.14.*"`) so the shell does not glob them.

---

## 1. Install pixi

```sh
curl -fsSL https://pixi.sh/install.sh | sh
# or, on macOS:
brew install pixi
```

Open a new shell, then confirm:

```sh
pixi --version
pixi info
```

`pixi info` shows the detected platform, virtual packages (`__osx`, `__glibc`, `__cuda`, ...),
the cache directory, and the config file locations. Keep it in mind — it is the first thing to
check when something behaves unexpectedly.

---

## 2. Create a workspace

```sh
cp -r labs/hello-pixi sandbox/ && cd sandbox/hello-pixi
pixi init .
cat pixi.toml
```

Generated manifest (your `authors` and `platforms` will differ):

```toml
[workspace]
authors = ["Kevin Mills <millsks@gmail.com>"]
channels = ["conda-forge"]
name = "hello-pixi"
platforms = ["osx-arm64"]
version = "0.1.0"

[tasks]

[dependencies]
```

Three things to notice:

- `[workspace]` is the current top-level table (older docs show `[project]`; pixi still reads it but writes `[workspace]`).
- `channels` defaults to `conda-forge` only. Conda-forge first is the rule; add other channels deliberately.
- `platforms` defaults to the machine you ran `pixi init` on. Add others explicitly (see [pixi-multi-platform.md](pixi-multi-platform.md)).

---

## 3. Add dependencies

```sh
pixi add "python=3.14.*"
pixi add rich
```

`pixi add` solves the environment, updates `pixi.toml`, writes `pixi.lock`, and installs into
`.pixi/envs/default`. Look at the manifest again:

```toml
[dependencies]
python = "3.14.*"
rich = ">=14.3.2,<15"
```

`python` was pinned to the minor version you asked for; `rich` was pinned with the default
`semver` strategy (`>=<solved>,<next-major>`). Pinning strategies are covered in
[pixi-dependencies.md](pixi-dependencies.md).

---

## 4. Run something

`pixi run <cmd>` activates the environment and runs `<cmd>` inside it. If the environment is
out of date it is installed first, so `pixi install` is rarely needed as a separate step.

```sh
pixi run python -c 'import rich, sys; print(sys.version); rich.print("[bold green]pixi works[/]")'
```

Now turn that into a named task (tasks are covered fully in [pixi-tasks.md](pixi-tasks.md)):

```sh
pixi task add hello 'python -c "import rich; rich.print(\"[bold green]hello from a task[/]\")"'
pixi run hello
pixi task list
```

---

## 5. Drop into a shell

```sh
pixi shell
which python        # -> .../hello-pixi/.pixi/envs/default/bin/python
echo $PIXI_PROJECT_NAME
exit
```

`pixi shell` starts a subshell with the environment activated. `exit` leaves it. Nothing is
written to your shell rc files.

---

## 6. What got created

```sh
ls -a
tree -L 2 .pixi 2>/dev/null || find .pixi -maxdepth 2
```

| Path | Purpose | Commit it? |
|---|---|---|
| `pixi.toml` | Manifest: channels, platforms, dependencies, tasks, features, environments | Yes |
| `pixi.lock` | Fully resolved lockfile for every environment × platform | Yes |
| `.pixi/envs/<env>/` | The installed conda environment(s) | No (gitignored) |
| `.pixi/config.toml` | Optional workspace-local pixi config (see [pixi-config.md](pixi-config.md)) | Yes, if present |
| `.gitignore` | `pixi init` adds `.pixi/` for you | Yes |

Inspect what is installed:

```sh
pixi list            # every package in the default environment; explicit deps highlighted
pixi list rich       # regex filter
pixi tree            # dependency tree
pixi tree -i python  # inverted: what depends on python
```

---

## 7. Cleanup

```sh
pixi clean           # removes .pixi/envs/* for this workspace; manifest and lock untouched
cd .. && rm -rf hello-pixi
```

---

## Key takeaways

- `pixi init` → `pixi add` → `pixi run` is the whole loop for a single-environment project.
- `pixi run` installs on demand; `pixi install` is only needed when you want the install without running anything (CI, Docker layers).
- `pixi.toml` and `pixi.lock` are source; `.pixi/` is a build artifact.
- Everything in this primer that says "run Python" means `pixi run python ...` — never a bare `python` or `pip`.

## Next

- [pixi-manifest-reference.md](pixi-manifest-reference.md) — every table in `pixi.toml`
- [pixi-dependencies.md](pixi-dependencies.md) — conda vs PyPI, pinning, upgrading
- [pixi-tasks.md](pixi-tasks.md) — the task runner
