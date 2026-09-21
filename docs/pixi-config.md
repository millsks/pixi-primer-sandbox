---
type: Reference
title: Pixi Configuration
description: Where pixi reads config.toml from and in what precedence, the keys worth setting (tls-root-certs, default-channels, pinning-strategy, mirrors, detached-environments, pypi-config, cache, shell), and the pixi config CLI for editing them at project, user, or system scope.
tags: [pixi, config, tls, mirrors, cache, reference]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: pixi-config-help
    resource: cli:pixi/0.81.0/config --help
    title: pixi config --help (pixi 0.81.0)
    author: process:pixi/0.81.0
  - id: pixi-docs-config
    resource: https://pixi.prefix.dev/latest/reference/pixi_configuration/
    title: pixi — configuration reference
---

# Pixi Configuration

Verified against `pixi 0.81.0`. Configuration is separate from the manifest: `pixi.toml` says
*what* an environment is; `config.toml` says *how* pixi behaves on this machine (certificates,
mirrors, cache location, prompt). Config never affects the lockfile contents.

---

## 1. Where config comes from

Highest priority first; later files fill in keys earlier ones did not set.

| Priority | Location | Scope | Edit with |
|---|---|---|---|
| 1 | CLI flags (`--tls-no-verify`, `--pinning-strategy`, ...) | one command | — |
| 2 | `<workspace>/.pixi/config.toml` | this workspace | `pixi config set --local` |
| 3 | `$PIXI_HOME/config.toml` (default `~/.pixi/config.toml`) | this user | `pixi config set --global` |
| 4 | `$XDG_CONFIG_HOME/pixi/config.toml` / platform config dir | this user | hand-edit |
| 5 | `/etc/pixi/config.toml` (and `/etc/rattler/config.toml`) | every user | `pixi config set --system` |

See what is actually loaded:

```sh
pixi info | grep -A3 'Config locations'
pixi config list                 # merged view
pixi config list --local         # only this workspace's file
```

`--no-config` on any command skips user and system files (the workspace-local file is still
read); `--config-file <path>` substitutes one file for the search.

---

## 2. The `pixi config` CLI

```sh
pixi config list [KEY]
pixi config set  [--local|--global|--system] KEY VALUE
pixi config unset [--local|--global|--system] KEY
pixi config append  KEY VALUE      # list keys
pixi config prepend KEY VALUE
pixi config edit [--local|--global|--system]
```

Values are TOML: strings need quotes in TOML but the CLI accepts bare words for strings and
`true`/`false` for booleans; arrays are passed as TOML literals.

```sh
pixi config set --global default-channels '["conda-forge", "bioconda"]'
pixi config append --global default-channels pytorch
pixi config set --local tls-root-certs system
pixi config set --global shell.change-ps1 false
```

Lab (safe — writes only to a sandbox workspace):

```sh
mkdir -p sandbox && cd sandbox && pixi init config-lab && cd config-lab
pixi config set --local tls-root-certs system
pixi config set --local pinning-strategy minor
cat .pixi/config.toml
pixi config list
pixi add rich && grep rich pixi.toml     # pinned with the minor strategy
cd .. && rm -rf config-lab
```

---

## 3. Keys worth knowing

### Networking and trust

```toml
tls-root-certs = "system"          # use the OS trust store (corporate CAs); default "webpki"
tls-no-verify = false              # never set true outside a throwaway VM
offline = false                    # true: fail instead of touching the network

[proxy-config]
https = "http://proxy.example:3128"
non-proxy-hosts = ["localhost", ".internal.example"]

[mirrors]
"https://conda.anaconda.org/conda-forge" = ["https://prefix.dev/conda-forge"]
```

This primer's projects ship `.pixi/config.toml` containing `tls-root-certs = "system"` so
machines behind TLS-inspecting proxies work without per-user setup.

### Solving

```toml
default-channels = ["conda-forge"]   # used by pixi exec / global / init when nothing else says
pinning-strategy = "semver"          # no-pin | semver | exact-version | major | minor | latest-up
run-post-link-scripts = "false"      # or "insecure"

[pypi-config]
index-url = "https://pypi.org/simple"
extra-index-urls = []
keyring-provider = "disabled"        # or "subprocess"
```

`pypi-config` keys cannot live in the global file — they belong in the workspace-local config
or the manifest's `[pypi-options]`.

### Cache and environment location

```toml
detached-environments = true         # or a path; keeps .pixi/envs out of the repo dir

[cache]
root = "/fast/disk/pixi-cache"
conda-packages = "/shared/pkgs"
netfs-redirect = "auto"              # auto | always | never — relocate cache off NFS
```

`detached-environments` is the fix for workspaces on network shares, Dropbox-style sync
folders, or filesystems that choke on hard links. Environments go to
`<cache root>/environments/<hash>/` and `.pixi/envs/<name>` becomes a symlink.

### Shell

```toml
[shell]
change-ps1 = true                    # "(name)" prompt prefix in pixi shell
force-activate = false
source-completion-scripts = true
```

### Concurrency

```toml
[concurrency]
downloads = 50
solves = 4
```

### Experimental

```toml
[experimental]
use-environment-activation-cache = false
conda-script = false                 # allow `/// conda-script` blocks without --experimental
```

---

## 4. Environment variables

| Variable | Effect |
|---|---|
| `PIXI_HOME` | root for global envs, bin dir, and user config (default `~/.pixi`) |
| `PIXI_CACHE_DIR` / `RATTLER_CACHE_DIR` | package/repodata cache location |
| `PIXI_NO_CONFIG`, `PIXI_CONFIG_FILE` | same as the CLI flags |
| `PIXI_FROZEN`, `PIXI_LOCKED`, `PIXI_NO_INSTALL` | lockfile behaviour (see [pixi-lockfile-updates.md](pixi-lockfile-updates.md)) |
| `PIXI_OFFLINE` | same as `offline` |
| `PIXI_COLOR`, `PIXI_NO_PROGRESS` | output control, useful in CI logs |

---

## Key takeaways

- Config is per-machine behaviour; manifest is per-project truth. Do not put channels a project needs into config — put them in `pixi.toml`.
- `--local` writes `.pixi/config.toml`, which is committed. `--global` writes `~/.pixi/config.toml`, which is not.
- `tls-root-certs = "system"` and `detached-environments` solve the two most common "pixi is broken on my corporate laptop" reports.
