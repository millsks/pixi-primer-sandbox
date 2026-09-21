---
type: Tutorial
title: Multi-Platform Workspaces
description: Lock and install for platforms other than the one you are on — adding platforms, [target.*] conditional dependencies and tasks, system-requirements, and cross-platform lock checks.
tags: [pixi, platforms, cross-platform, target, system-requirements, tutorial]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-platform-help
    resource: cli:pixi/0.81.0/workspace platform --help
    title: pixi workspace platform --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-multi-platform
    resource: https://pixi.prefix.dev/latest/workspace/multi_platform_configuration/
    title: pixi — multi-platform configuration
  - id: pixi-docs-sysreq
    resource: https://pixi.prefix.dev/latest/workspace/system_requirements/
    title: pixi — system requirements
---

# Multi-Platform Workspaces

Verified against `pixi 0.81.0`. `pixi.lock` is solved for **every** platform in
`[workspace].platforms`, on whatever machine runs the solve. A macOS laptop can therefore
produce the exact Linux lock that CI will install — and CI can verify the lock without
re-solving.

## Setup

```sh
mkdir -p sandbox && cd sandbox
pixi init platform-lab && cd platform-lab
pixi add "python=3.14.*" rich
```

---

## 1. Add platforms

```sh
pixi workspace platform list
pixi workspace platform add linux-64 win-64
pixi workspace platform list
```

Output lists each platform and which environments use it, plus a line describing your
current machine. Each add triggers a re-solve; the lock now carries three package lists.

```sh
grep -E '^\s+(osx-arm64|linux-64|win-64):' pixi.lock
```

Solve failures here are informative: a package that has no Windows build will fail the
`win-64` solve immediately rather than surprising a teammate later.

Common subdirs: `linux-64`, `linux-aarch64`, `osx-64`, `osx-arm64`, `win-64`, `noarch`
(implicit). `pixi workspace platform remove win-64` drops one.

---

## 2. Platform-conditional dependencies

```sh
pixi add --platform linux-64 patchelf
pixi add --platform osx-arm64 --platform osx-64 libcxx
```

```toml
[target.linux-64.dependencies]
patchelf = ">=0.19.1,<0.20"

[target.osx-arm64.dependencies]
libcxx = "..."

[target.osx-64.dependencies]
libcxx = "..."
```

Hand-edit to the family selector to collapse duplicates:

```toml
[target.osx.dependencies]
libcxx = "*"
```

Selector precedence, most specific wins: `linux-64` > `linux` > `unix`; `win-64` > `win`;
`osx-arm64` / `osx-64` > `osx` > `unix`. PyPI deps work the same way under
`[target.<sel>.pypi-dependencies]`.

Confirm per-platform contents without leaving your machine:

```sh
pixi list --platform linux-64 patchelf
pixi list --platform osx-arm64 patchelf    # not present
```

---

## 3. Platform-conditional tasks

```sh
pixi task add --platform win-64 open 'start .'      # platform variants first ...
pixi task add --platform linux-64 open 'xdg-open .'
pixi task add open 'open .'                          # ... then the default
```

`--platform` only accepts concrete subdirs; collapse to a family by hand if you want:

```toml
[tasks]
open = "open ."

[target.win-64.tasks]
open = "start ."

[target.linux.tasks]
open = "xdg-open ."
```

For small differences, a MiniJinja conditional in one task is often cleaner:

```toml
[tasks]
open = "{% if pixi.is_win %}start .{% elif pixi.is_linux %}xdg-open .{% else %}open .{% endif %}"
```

---

## 4. System requirements

The solver assumes minimum host capabilities via virtual packages. Compare:

```sh
pixi info | grep -A4 'Virtual packages'
```

with the defaults pixi assumes (`linux = "4.18"`, `libc = { family = "glibc", version = "2.28" }`,
`macos = "13.0"`, `cuda` unset). Raise them when you need packages built against newer
baselines, lower them when targeting old hosts:

```toml
[system-requirements]
macos = "14.0"
linux = "5.10"
libc = { family = "glibc", version = "2.31" }
```

Feature-scoped variants (`[feature.gpu.system-requirements] cuda = "12"`) only affect
environments that include the feature.

---

## 5. Installing and running for another platform

You cannot *execute* a linux-64 environment on macOS, but you can materialise it — useful for
building Docker layers or inspecting file layouts:

```sh
pixi install --platform linux-64        # warns, then installs into .pixi/envs/default
```

For real cross-platform verification, use CI (see [pixi-ci-github-actions.md](pixi-ci-github-actions.md))
with `pixi install --locked` on each runner.

---

## 6. Cleanup

```sh
cd .. && rm -rf platform-lab
```

---

## Key takeaways

- List every platform you ship to in `[workspace].platforms`; the lock is solved for all of them on every `pixi add`.
- `[target.<selector>.*]` is the only place platform differences belong — never fork the manifest.
- `pixi list --platform` and `pixi lock --check` let a single machine validate all platforms.
- `system-requirements` is the knob when the solver picks packages your hosts cannot run.
