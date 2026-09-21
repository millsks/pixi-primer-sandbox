---
type: Reference
title: Troubleshooting and Maintenance
description: Diagnostic commands (pixi info, -vv, lock --check), cache and environment cleanup, and a symptom-to-fix table for the errors people hit most — solve failures, missing platforms, PyPI without Python, TLS on corporate networks, stale activation, and lockfile conflicts.
tags: [pixi, troubleshooting, cache, clean, reference]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-clean-help
    resource: cli:pixi/0.81.0/clean --help
    title: pixi clean --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-clean-cache-help
    resource: cli:pixi/0.81.0/clean cache --help
    title: pixi clean cache --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-info-help
    resource: cli:pixi/0.81.0/info --help
    title: pixi info --help (pixi 0.81.0)
    author: process:pixi/0.81.0
---

# Troubleshooting and Maintenance

Verified against `pixi 0.81.0`. Work top-down: gather facts, then reset the cheapest layer
that could be wrong, then reach for the symptom table.

---

## 1. Gather facts first

```sh
pixi --version
pixi info                 # platform, virtual packages, cache dir, config files, environments
pixi info --extended      # adds cache and environment sizes
pixi info --json | jq .
pixi lock --check         # is the lock in sync with the manifest?
pixi list -e <env>        # what is actually installed
pixi tree -i <pkg>        # why is <pkg> here?
pixi run -n <task>        # what command would run, without running it
```

Increase verbosity on the failing command:

```sh
pixi -v  install     # warnings
pixi -vv install     # info: solver decisions, channels queried
pixi -vvv install    # debug: HTTP requests, cache hits
```

Set `PIXI_NO_PROGRESS=1` and `PIXI_COLOR=never` when capturing logs to a file.

---

## 2. Reset layers, cheapest first

| Layer | Command | Removes | Keeps |
|---|---|---|---|
| Activation cache | `pixi clean --activation-cache` | cached env-var results of activation scripts | everything else |
| One environment | `pixi clean -e test` | `.pixi/envs/test` | other envs, lock |
| All environments | `pixi clean` | `.pixi/envs/*` | manifest, lock, package cache |
| Rebuild from lock | `pixi reinstall [-e env] [--all]` | and re-creates envs | lock |
| `pixi exec` envs | `pixi clean cache --exec` | temp envs | package cache |
| Repodata | `pixi clean cache --repodata` | channel index cache (forces refetch) | packages |
| PyPI cache | `pixi clean cache --pypi` | uv wheel/source cache | conda packages |
| Conda cache | `pixi clean cache --conda` | downloaded `.conda` files | repodata |
| Everything cached | `pixi clean cache` | all of the above | nothing (next install re-downloads) |
| pixi-build | `pixi clean --build` / `pixi clean cache --build --build-backends` | build outputs / backend envs | — |

Re-running `pixi install` (or any `pixi run`) after a clean rebuilds from `pixi.lock` without
re-solving, as long as the lock is current.

---

## 3. Symptom → cause → fix

| Symptom | Likely cause | Fix |
|---|---|---|
| `zsh: no matches found: python=3.14.*` | shell globbed the MatchSpec | quote it: `pixi add "python=3.14.*"` |
| `could not find pixi.toml or pyproject.toml with tool.pixi` | running outside a workspace, or a script without `--script` | `cd` to the workspace, use `-m <path>`, or `pixi run --script file.py` |
| `Cannot solve the request because of: ...` / `nothing provides` | version conflict, package absent for a listed platform, or wrong channel | `pixi search <pkg>` per platform; loosen the spec; add the channel; remove the platform you do not ship to |
| PyPI add fails with "no python interpreter" | `[dependencies]` has no `python` | `pixi add "python=3.14.*"` first |
| `--locked` fails / `pixi lock --check` non-zero | manifest edited, lock not re-solved | `pixi lock` locally, commit `pixi.lock` |
| Package installed but `import` fails | wrong environment, or conda and PyPI both provide it | `pixi list -e <env> <pkg>`; keep one source, prefer conda-forge |
| TLS / certificate errors behind a proxy | corporate CA not in bundled roots | `pixi config set --local tls-root-certs system`; set `[proxy-config]` if needed |
| Solve extremely slow | first repodata fetch, or a huge channel | wait once; `[concurrency]`; sharded repodata is on by default — do not disable it |
| Hard-link / cross-device errors on NFS or Dropbox | cache and env on different filesystems | `detached-environments = true` or `[cache] netfs-redirect = "always"` |
| Activation script change not taking effect | cached activation | `pixi clean --activation-cache` |
| Task not found | typo, hidden `_` task, or task lives in a feature not in this env | `pixi task list`; `pixi run -e <env> <task>` |
| Same name is both a task and a binary | task shadows executable | `pixi run -x <binary>` |
| `pixi run` "works on my machine" only | leaked env vars (`PYTHONPATH`, `VIRTUAL_ENV`) | `pixi run --clean-env <task>` to confirm, then fix the task |
| Wrong platform picked / `__cuda` missing | virtual packages differ from expectation | `pixi info` → Virtual packages; adjust `[system-requirements]` |
| Two lockfiles (`uv.lock`, `poetry.lock`) drifting | old tool left behind after import | delete them; see [pixi-import-guide.md](pixi-import-guide.md) |
| Environment directory is huge | many envs + Python matrix | `pixi info --extended`; `pixi clean -e <unused>`; `pixi list --sort-by size` |

---

## 4. Keeping a workspace healthy

Weekly or per-PR:

```sh
pixi update --dry-run                 # see what would move
pixi upgrade --dry-run                # see which ranges are stale
pixi lock --check
pixi run ci
```

Before handing a repo to someone else:

```sh
pixi workspace requires-pixi set ">=0.81"
pixi workspace platform list          # every platform they might use?
git status --porcelain pixi.toml pixi.lock   # both committed?
```

---

## 5. Getting help

```sh
pixi <cmd> --help          # every subcommand documents its flags
pixi help <cmd>
```

- Docs: <https://pixi.prefix.dev/latest/>
- Issues: <https://github.com/prefix-dev/pixi/issues>
- Discord: <https://discord.gg/kKV8ZxyzY4>

Attach `pixi info` output and the `-vv` log of the failing command to any report.
