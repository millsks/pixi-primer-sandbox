---
type: Reference
title: pixi.toml Manifest Reference
description: Annotated tour of every table pixi reads from pixi.toml — workspace, dependencies, pypi-dependencies, tasks, feature, environments, target, activation, system-requirements — with the minimal valid form of each.
tags: [pixi, manifest, toml, reference]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-docs-manifest
    resource: https://pixi.prefix.dev/latest/reference/pixi_manifest/
    title: pixi — manifest reference
  - id: pixi-init-output
    resource: cli:pixi/0.81.0/init
    title: pixi init generated manifest (pixi 0.81.0)
    author: process:pixi/0.81.0
---

# pixi.toml Manifest Reference

Verified against `pixi 0.81.0`. This is a reading document, not a lab — use it alongside the
tutorials. Every snippet below is a complete, valid fragment you can paste into a sandbox
manifest and check with `pixi lock --dry-run`.

Policy reminder for this primer: pixi configuration lives in `pixi.toml`. `pyproject.toml` is
for Python tool configuration (pytest, ruff, mypy). Do not use `pixi init --format pyproject`.

---

## `[workspace]`

```toml
[workspace]
name = "demo"
version = "0.1.0"
description = "One-line description"
authors = ["Kevin Mills <millsks@gmail.com>"]
channels = ["conda-forge"]
platforms = ["osx-arm64", "linux-64"]
license = "MIT"
readme = "README.md"
requires-pixi = ">=0.81"
preview = []
```

| Key | Notes |
|---|---|
| `channels` | Ordered; earlier channels win by default (strict channel priority). `pixi workspace channel add bioconda` appends; `--prepend` puts it first. |
| `platforms` | Every platform the lockfile must solve for. `pixi workspace platform add linux-64`. |
| `requires-pixi` | Fails fast when a teammate runs an older pixi. `pixi workspace requires-pixi set ">=0.81"`. |
| `preview` | Opt-in experimental features, e.g. `["pixi-build"]`. `pixi workspace preview add pixi-build`. |
| `conda-pypi-map` | Per-channel mapping of conda names to PyPI names; set with `pixi init --conda-pypi-map`. |

---

## `[dependencies]` (conda)

```toml
[dependencies]
python = "3.14.*"
numpy = ">=2.3,<3"
pytorch = { version = ">=2.5", channel = "pytorch" }
mylib = { path = "../mylib" }
```

Values are conda MatchSpecs. The table form supports `version`, `build`, `channel`, `path`,
`git` (+ `branch`/`tag`/`rev`), and `subdir`. Written by `pixi add`.

Related tables with the same syntax: `[host-dependencies]` and `[build-dependencies]`
(only meaningful with pixi-build, see [pixi-build-packages.md](pixi-build-packages.md)).

---

## `[pypi-dependencies]`

```toml
[pypi-dependencies]
requests = ">=2.32"
structlog = { version = ">=25", extras = ["dev"] }
mypkg = { path = ".", editable = true }
other = { git = "https://github.com/org/other.git", tag = "v1.2.0" }
```

PEP 508 version specifiers. Requires a `python` entry in `[dependencies]` — PyPI resolution needs
an interpreter. Written by `pixi add --pypi`. Prefer conda-forge when the package exists there.

`[pypi-options]` configures index URLs and `no-build` / `no-binary` behaviour:

```toml
[pypi-options]
index-url = "https://pypi.org/simple"
extra-index-urls = ["https://internal.example/simple"]
```

---

## `[tasks]`

```toml
[tasks]
fmt = "ruff format ."
lint = "ruff check ."
test = { cmd = "pytest tests/unit/", description = "Unit tests only" }
ci = { depends-on = ["fmt", "lint", "test"] }
greet = { cmd = "echo Hello {{ name }}", args = [{ arg = "name", default = "world" }] }
build = { cmd = "make", inputs = ["src/**/*.c"], outputs = ["out/app"], cwd = "native", env = { CC = "clang" } }
```

Full treatment in [pixi-tasks.md](pixi-tasks.md). Commands run in `deno_task_shell`, so
`&&`, `||`, `|`, `$VAR`, globs, and `cp`/`mv`/`rm`/`mkdir` work identically on every platform.

---

## `[feature.<name>.*]`

A feature is a named bundle of any of the tables above plus its own channels, platforms,
system requirements, and activation. Features are inert until an environment includes them.

```toml
[feature.test.dependencies]
pytest = "*"
pytest-cov = "*"

[feature.test.tasks]
cov = "pytest tests/ --cov=src --cov-fail-under=90"

[feature.py312.dependencies]
python = "3.12.*"      # only valid if the default feature does NOT also pin python — specs intersect

[feature.cuda]
channels = ["nvidia", "conda-forge"]
platforms = ["linux-64"]
system-requirements = { cuda = "12" }
```

Written by `pixi add -f test pytest`, `pixi task add -f test cov '...'`, etc.

---

## `[environments]`

```toml
[environments]
default = { solve-group = "default" }
test = { features = ["test"], solve-group = "default" }
py312 = { features = ["py312", "test"] }
docs = { features = ["docs"], no-default-feature = true }
```

| Key | Meaning |
|---|---|
| `features` | Which features compose the environment. The `default` feature (top-level tables) is included unless `no-default-feature = true`. |
| `solve-group` | Environments in the same group are solved together so shared packages resolve to identical versions. |
| `no-default-feature` | Exclude the top-level `[dependencies]`/`[tasks]` — for tool-only environments like `docs` or `lint`. |

Written by `pixi workspace environment add test -f test --solve-group default`.
Full treatment in [pixi-features-environments.md](pixi-features-environments.md).

---

## `[target.<selector>.*]`

Platform-conditional overrides. Any of `dependencies`, `pypi-dependencies`, `tasks`,
`activation`, `host-dependencies`, `build-dependencies` can be nested here.

```toml
[target.linux-64.dependencies]
patchelf = "*"

[target.osx.dependencies]
libcxx = "*"

[target.win-64.tasks]
open = "start ."

[target.unix.tasks]
open = "open ."
```

Selectors: exact subdirs (`linux-64`, `osx-arm64`, `win-64`, ...) or families (`linux`, `osx`,
`win`, `unix`). More specific selectors override less specific ones. Written by
`pixi add --platform linux-64 patchelf`. See [pixi-multi-platform.md](pixi-multi-platform.md).

---

## `[activation]`

```toml
[activation]
scripts = ["scripts/env.sh"]

[activation.env]
PYTHONUNBUFFERED = "1"
DATA_DIR = "$PIXI_PROJECT_ROOT/data"
```

Scripts are sourced and env vars exported whenever the environment is activated
(`pixi run`, `pixi shell`, `pixi shell-hook`). Per-platform scripts go under
`[target.win-64.activation]`. See [pixi-activation-shell.md](pixi-activation-shell.md).

---

## `[system-requirements]`

Minimum virtual-package versions the environment assumes on the host. Affects which packages
the solver will pick.

```toml
[system-requirements]
linux = "4.18"
libc = { family = "glibc", version = "2.28" }
macos = "13.0"
cuda = "12"
```

Compare with `pixi info` → "Virtual packages" to see what your machine actually provides.

---

## `[package]` (pixi-build, preview)

Only present when the workspace also *is* a buildable conda package. Requires
`preview = ["pixi-build"]`. See [pixi-build-packages.md](pixi-build-packages.md).

---

## CLI ↔ table map

| You want to change | Command that edits the manifest for you |
|---|---|
| `[dependencies]` | `pixi add` / `pixi remove` / `pixi upgrade` |
| `[pypi-dependencies]` | `pixi add --pypi` / `pixi remove --pypi` |
| `[tasks]` | `pixi task add` / `remove` / `alias` |
| `[feature.X.*]` | any of the above with `-f X` |
| `[environments]` | `pixi workspace environment add/remove/list` |
| `[workspace].channels` | `pixi workspace channel add/remove/list` |
| `[workspace].platforms` | `pixi workspace platform add/remove/list` |
| `[activation]` | `pixi workspace activation script/env` |
| `[workspace].preview` | `pixi workspace preview add/remove/list` |
| `[workspace].requires-pixi` | `pixi workspace requires-pixi set/get` |

Prefer the command — it validates and re-solves. Hand-edit only for keys without a command
(`args`, `inputs`/`outputs`, `system-requirements`, `pypi-options`), then run `pixi lock` to
confirm the manifest still parses and solves.
