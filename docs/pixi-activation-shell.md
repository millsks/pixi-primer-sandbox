---
type: Tutorial
title: Activation, Shells, and Environment Variables
description: How pixi activates an environment; [activation] scripts and env tables, pixi shell vs pixi shell-hook, the PIXI_* variables pixi exports, and clean-env isolation.
tags: [pixi, activation, shell, environment-variables, tutorial]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-shell-hook-help
    resource: cli:pixi/0.81.0/shell-hook --help
    title: pixi shell-hook --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-activation-help
    resource: cli:pixi/0.81.0/workspace activation --help
    title: pixi workspace activation --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-env-vars
    resource: https://pixi.prefix.dev/latest/workspace/environment/
    title: pixi — environment activation
---

# Activation, Shells, and Environment Variables

Verified against `pixi 0.81.0`. "Activation" is the set of environment-variable exports and
scripts pixi applies before running anything in an environment: prepend `.pixi/envs/<env>/bin`
to `PATH`, set `CONDA_PREFIX`, run each package's own activation scripts, then apply your
`[activation]` table.

## Setup

```sh
cp -r labs/act-lab sandbox/ && cd sandbox/act-lab
pixi init .
pixi add "python=3.14.*"
```

The lab ships `scripts/env.sh` for §3.

---

## 1. What pixi exports

```sh
pixi shell-hook -s zsh | grep -E '^export' | cut -d= -f1
```

Variables you can rely on inside any task or shell:

| Variable | Value |
|---|---|
| `PATH` | environment `bin/` prepended |
| `CONDA_PREFIX` | `.pixi/envs/<env>` |
| `CONDA_DEFAULT_ENV` | environment name, for tools that read the conda convention |
| `PIXI_PROJECT_ROOT` | directory containing the manifest |
| `PIXI_PROJECT_MANIFEST` | full path to `pixi.toml` |
| `PIXI_PROJECT_NAME` / `PIXI_PROJECT_VERSION` | from `[workspace]` |
| `PIXI_ENVIRONMENT_NAME` | `default`, `test`, ... |
| `PIXI_ENVIRONMENT_PLATFORMS` | comma-separated platform list |
| `PIXI_PROMPT` | the `(name)` prefix used by `pixi shell` |
| `PIXI_EXE` | path to the pixi binary |
| `PIXI_IN_SHELL` | set to `1` inside `pixi shell` |

```sh
pixi run 'echo root=$PIXI_PROJECT_ROOT env=$PIXI_ENVIRONMENT_NAME'
```

---

## 2. `[activation.env]`

Static variables applied on every activation. Manage with the CLI:

```sh
pixi workspace activation env set PYTHONUNBUFFERED=1 DATA_DIR='$PIXI_PROJECT_ROOT/data'
pixi workspace activation list
pixi run 'echo $DATA_DIR'
```

```toml
[activation.env]
PYTHONUNBUFFERED = "1"
DATA_DIR = "$PIXI_PROJECT_ROOT/data"
```

Values are expanded by pixi, so referencing `PIXI_*` variables works. Per-feature and
per-platform tables are supported (`[feature.gpu.activation.env]`,
`[target.win-64.activation.env]`). Remove with `pixi workspace activation env remove DATA_DIR`.

---

## 3. `[activation] scripts`

For anything dynamic — computed paths, `source`-ing a vendor SDK, tool init:

```sh
cat scripts/env.sh
pixi workspace activation script add scripts/env.sh
pixi run 'echo stamp=$BUILD_STAMP root=$TOOLCHAIN_ROOT'
```

```toml
[activation]
scripts = ["scripts/env.sh"]
```

Scripts must be `.sh` on unix and `.bat`/`.ps1` on Windows; supply both under
`[target.unix.activation]` / `[target.win-64.activation]` for cross-platform workspaces.
Pixi caches the resulting variables under `.pixi/` — `pixi clean --activation-cache` resets
it if a script change does not appear to take effect.

---

## 4. `pixi shell` vs `pixi shell-hook`

`pixi shell` starts a **new** subshell with everything activated:

```sh
pixi shell
echo $PIXI_IN_SHELL          # 1
which python
exit
```

`pixi shell-hook` prints the activation script so you can apply it to your **current** shell
(or a Dockerfile, or a CI step) without spawning a subshell:

```sh
eval "$(pixi shell-hook -s zsh)"
which python
pixi shell-hook -e test -s bash > activate-test.sh
pixi shell-hook --json | head       # variables as JSON, for tooling
```

Supported shells: `bash`, `zsh`, `fish`, `xonsh`, `nushell`, `powershell`, `cmd`.

There is no `pixi deactivate`; close the shell or open a fresh one.

---

## 5. Isolation with `--clean-env`

Your interactive shell leaks variables (`VIRTUAL_ENV`, `PYTHONPATH`, `CONDA_*` from another
tool) into pixi runs. Prove a task works without them:

```sh
export PYTHONPATH=/tmp/should-not-leak
pixi run 'echo PYTHONPATH=$PYTHONPATH'                # leaks
pixi run --clean-env 'echo PYTHONPATH=$PYTHONPATH'    # empty
unset PYTHONPATH
```

Make it permanent for a task with `clean-env = true` (see [pixi-tasks.md](pixi-tasks.md) §4).
`--clean-env` is a `pixi run` / task option only; `pixi shell` has no equivalent. Not supported
on Windows.

---

## 6. Prompt and shell config

The `(act-lab)` prompt prefix comes from `PIXI_PROMPT`. Disable it globally:

```sh
pixi config set --global shell.change-ps1 false
```

See [pixi-config.md](pixi-config.md) for the other `shell.*` keys.

---

## 7. Cleanup

```sh
cd .. && rm -rf act-lab
```

---

## Key takeaways

- Activation is deterministic: package scripts → `[activation] scripts` → `[activation.env]`, every time, for `pixi run`, `pixi shell`, and `pixi shell-hook` alike.
- Put static values in `[activation.env]`, dynamic ones in a script.
- `pixi shell-hook` is the bridge to Docker, CI, and editors that cannot spawn a subshell.
- `--clean-env` is the fastest way to tell "works on my machine" from "works".
