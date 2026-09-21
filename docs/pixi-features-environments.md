---
type: Tutorial
title: Features and Environments
description: Compose multiple environments (default, test, docs, a Python version matrix) from reusable features; solve-groups, no-default-feature, running and installing per environment.
tags: [pixi, features, environments, solve-group, matrix, tutorial]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-env-add-help
    resource: cli:pixi/0.81.0/workspace environment add --help
    title: pixi workspace environment add --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-multi-env
    resource: https://pixi.prefix.dev/latest/workspace/multi_environment/
    title: pixi — multi environment
---

# Features and Environments

Verified against `pixi 0.81.0`. A **feature** is a named slice of manifest (dependencies,
tasks, channels, platforms, activation). An **environment** is a named set of features that
gets solved, locked, and installed as one unit under `.pixi/envs/<name>/`. The top-level
tables (`[dependencies]`, `[tasks]`, ...) form the implicit `default` feature.

This is how one manifest replaces `requirements-dev.txt`, `tox.ini` env lists, and separate
docs/lint virtualenvs.

## Setup

```sh
mkdir -p sandbox && cd sandbox
pixi init envs-lab && cd envs-lab
pixi add "python=3.14.*" rich
```

---

## 1. A `test` feature and environment

```sh
pixi add -f test pytest pytest-cov
```

Notice the message: the feature is not part of any environment yet, so pixi writes
`pytest = "*"` rather than solving and pinning. Now create the environment:

```sh
pixi workspace environment add test -f test --solve-group default
pixi upgrade -f test pytest pytest-cov      # pin now that the feature is solvable
pixi workspace environment list
pixi workspace feature list
```

Manifest result:

```toml
[feature.test.dependencies]
pytest = ">=9.1.1,<10"
pytest-cov = ">=7.0.0,<8"

[environments]
test = { features = ["test"], solve-group = "default" }
```

The `test` environment = `default` feature + `test` feature. Run in it with `-e`:

```sh
pixi run -e test pytest --version
pixi run pytest --version          # fails: pytest is not in the default environment
```

---

## 2. Solve groups

`solve-group = "default"` puts `test` and `default` into the same solve. Every package they
share (`python`, `rich`, ...) resolves to the **same version** in both, so what you test is what
you ship. Without a solve group each environment is solved independently and may drift.

Confirm:

```sh
pixi list -e default rich
pixi list -e test rich
```

The `default` environment is **not** in any solve group unless you say so — `pixi info` shows
`Solve group: default` under `test` only. Declare it explicitly so the two really are solved
together:

```sh
pixi workspace environment add default --solve-group default --force
```

```toml
[environments]
default = { solve-group = "default" }
test = { features = ["test"], solve-group = "default" }
```

---

## 3. `no-default-feature` for tool environments

A docs or lint environment does not need your runtime dependencies at all:

```sh
pixi add -f docs mkdocs mkdocs-material
pixi workspace environment add docs -f docs --no-default-feature
pixi task add -f docs docs-serve 'mkdocs serve'
pixi run -e docs mkdocs --version
```

```toml
[environments]
docs = { features = ["docs"], no-default-feature = true }
```

`docs` contains only `mkdocs` and its deps — no `rich`, and no Python pin from the default
feature, so add one to the feature if you care: `pixi add -f docs "python=3.14.*"`.

---

## 4. A Python version matrix

Feature specs **combine** with the default feature's specs — they do not override them. With
`python = "3.14.*"` in `[dependencies]`, an environment that adds a `python = "3.12.*"`
feature asks for both and fails to solve. So for a matrix, the Python pin must live *only* in
features, and the `default` environment must be told which one to use:

```sh
pixi remove python                              # take the pin out of the default feature
pixi add -f py312 "python=3.12.*"
pixi add -f py313 "python=3.13.*"
pixi add -f py314 "python=3.14.*"
pixi workspace environment add default -f py314 --solve-group default --force
pixi workspace environment add test -f py314 -f test --solve-group default --force
pixi workspace environment add py312 -f py312 -f test --solve-group py312
pixi workspace environment add py313 -f py313 -f test --solve-group py313
pixi workspace environment add py314 -f py314 -f test --solve-group py314
```

```toml
[environments]
default = { features = ["py314"], solve-group = "default" }
test = { features = ["py314", "test"], solve-group = "default" }
py312 = { features = ["py312", "test"], solve-group = "py312" }
py313 = { features = ["py313", "test"], solve-group = "py313" }
py314 = { features = ["py314", "test"], solve-group = "py314" }
```

`--force` is needed because `default` and `test` already exist. `default` and `test` still
share a solve group (3.14, what you develop on); each matrix environment gets its own group
so it can resolve a different interpreter. Now each is a full test setup on a different
interpreter:

```sh
for e in default test py312 py313 py314; do printf ": "; pixi run -e  python --version; done
pixi install --all            # materialise every environment (CI, pre-flight)
```

Run the same task across them with a dependency list:

```toml
[tasks]
test-matrix = { depends-on = [
  { task = "test", environment = "py312" },
  { task = "test", environment = "py313" },
  { task = "test", environment = "py314" },
] }
```

---

## 5. Feature-scoped channels, platforms, and system requirements

```toml
[feature.cuda]
channels = ["nvidia", "conda-forge"]
platforms = ["linux-64"]
system-requirements = { cuda = "12" }

[feature.cuda.dependencies]
pytorch-gpu = "*"

[environments]
gpu = { features = ["cuda"] }
```

The `gpu` environment only solves for `linux-64` and only when the machine reports
`__cuda >= 12`. Everything else in the workspace is unaffected.

---

## 6. Inspecting and removing

```sh
pixi info                                  # every environment, its features and channels
pixi workspace environment list
pixi workspace feature list
pixi workspace environment remove docs
pixi workspace feature remove docs          # removes [feature.docs.*] tables
pixi clean -e py312                        # delete just one installed env
```

---

## 7. Cleanup

```sh
cd .. && rm -rf envs-lab
```

---

## Key takeaways

- Feature = ingredients; environment = recipe. Features do nothing until an environment names them.
- Specs from all of an environment's features are intersected, never overridden — a pin that must vary (Python version) belongs only in the varying features.
- Use one solve group for anything that must agree on versions (default + test). Use separate groups for a version matrix.
- `no-default-feature = true` keeps tool environments lean and independent.
- `-e <env>` on `pixi run` / `pixi shell` / `pixi list` / `pixi install` selects the environment; omit it for `default`.
