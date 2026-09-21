---
type: Playbook
title: Pixi in CI with GitHub Actions
description: Wire a pixi workspace into GitHub Actions with prefix-dev/setup-pixi — lockfile enforcement, caching, running a task per environment across a Python matrix, and a Dockerfile pattern using pixi shell-hook.
tags: [pixi, ci, github-actions, docker, playbook]
status: draft
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: setup-pixi
    resource: https://github.com/prefix-dev/setup-pixi
    title: prefix-dev/setup-pixi — GitHub Action
  - id: pixi-docs-ci
    resource: https://pixi.prefix.dev/latest/integration/ci/github_actions/
    title: pixi — GitHub Actions integration
  - id: pixi-docs-docker
    resource: https://pixi.prefix.dev/latest/deployment/container/
    title: pixi — containers
---

# Pixi in CI with GitHub Actions

Written against `pixi 0.81.0` and `prefix-dev/setup-pixi@v0.8.1`. The workflow below is a
template, not something that was executed while generating this document (`status: draft`);
push it to a branch, watch it go green, then mark this file `stable`. The `pixi lock --check`
and `--locked` behaviour it relies on is verified in [pixi-lockfile-updates.md](pixi-lockfile-updates.md).

The principle: CI runs **the same tasks you run locally** (`pixi run ci`), against **the same
lock**, with no re-solve allowed.

---

## 1. Minimal workflow

```yaml
name: CI

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Pixi
        uses: prefix-dev/setup-pixi@v0.8.1
        with:
          pixi-version: latest
          cache: true
          locked: true

      - name: Run full CI
        run: pixi run ci
```

What each input does:

| Input | Effect |
|---|---|
| `pixi-version` | `latest`, or pin (`v0.81.0`) to match `requires-pixi` in the manifest |
| `cache: true` | caches `.pixi/envs` keyed on `pixi.lock`; a lock change invalidates it |
| `locked: true` | runs `pixi install --locked` — a stale lock fails the job instead of silently re-solving |
| `environments` | space-separated list to install up front (`"default test"`); default is only `default` |
| `manifest-path` | for monorepos where `pixi.toml` is not at the root |

The action installs the environment(s) and adds `.pixi/envs/default/bin` to `PATH` for
subsequent steps, but always prefer `pixi run <task>` so the run matches local behaviour.

---

## 2. Two-tier layout: fast unit job, full gate

```yaml
jobs:
  unit:
    name: Unit Tests (${{ matrix.env }})
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        env: [py312, py313, py314]
    steps:
      - uses: actions/checkout@v4
      - uses: prefix-dev/setup-pixi@v0.8.1
        with:
          pixi-version: latest
          cache: true
          locked: true
          environments: ${{ matrix.env }}
      - run: pixi run -e ${{ matrix.env }} test

  full:
    name: Full CI (${{ matrix.env }})
    runs-on: ubuntu-latest
    needs: unit
    strategy:
      fail-fast: false
      matrix:
        env: [py312, py313, py314]
    steps:
      - uses: actions/checkout@v4
      - uses: prefix-dev/setup-pixi@v0.8.1
        with:
          pixi-version: latest
          cache: true
          locked: true
          environments: ${{ matrix.env }}
      - run: pixi run -e ${{ matrix.env }} ci
```

The matrix iterates over **pixi environments** (`py312`, `py313`, `py314` from
[pixi-features-environments.md](pixi-features-environments.md) §4), not `setup-python`
versions. The interpreter comes from the lock, so CI and local are identical.

---

## 3. Cross-platform runners

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
runs-on: ${{ matrix.os }}
```

Requires `linux-64`, `osx-arm64`, and `win-64` in `[workspace].platforms` — otherwise
`--locked` fails on the missing platform. Solve them locally first
([pixi-multi-platform.md](pixi-multi-platform.md)).

---

## 4. Lockfile drift guard as a standalone job

Catches a PR that edited `pixi.toml` without committing the re-solved lock:

```yaml
  lock:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: prefix-dev/setup-pixi@v0.8.1
        with:
          run-install: false
      - run: pixi lock --check
```

`run-install: false` skips the environment install; `pixi lock --check` only needs repodata.

---

## 5. Local CI with `act`

The standard `act` task runs the workflow in Docker:

```toml
[tasks]
act = "act --container-architecture linux/amd64"
```

`act` needs `linux-64` in `platforms`. Expect the first run to be slow (repodata + packages);
subsequent runs reuse the container cache.

---

## 6. Docker image pattern

Multi-stage: solve and install with pixi, then copy only the environment into a slim runtime
image and activate it with `pixi shell-hook`.

```dockerfile
FROM ghcr.io/prefix-dev/pixi:0.81.0 AS build
WORKDIR /app
COPY pixi.toml pixi.lock ./
RUN pixi install --locked -e prod
COPY . .
RUN pixi shell-hook -e prod -s bash > /shell-hook.sh \
 && echo 'exec "$@"' >> /shell-hook.sh

FROM ubuntu:24.04 AS runtime
WORKDIR /app
COPY --from=build /app/.pixi/envs/prod /app/.pixi/envs/prod
COPY --from=build /shell-hook.sh /shell-hook.sh
COPY --from=build /app/src /app/src
ENTRYPOINT ["/bin/bash", "/shell-hook.sh"]
CMD ["python", "-m", "myapp"]
```

Copying only `pixi.toml` + `pixi.lock` first keeps the expensive install layer cached until
dependencies actually change. The runtime image has no pixi binary at all.

---

## Key takeaways

- `locked: true` (or `pixi install --locked`) in every job; a stale lock must fail loudly.
- Matrix over pixi environments, not `setup-python` versions — the lock owns the interpreter.
- CI runs `pixi run ci`, the same aggregator task you run before every commit.
- Containers: install with pixi, ship the env, activate with `shell-hook`.
