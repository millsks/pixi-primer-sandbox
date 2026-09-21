---
type: Reference
title: Pixi Primer — Where to Look
description: Index for the docs/ guides — a recommended learning order, a lookup organised by what you are trying to do with deep links to the answering section, and the full list of guides with type and status.
tags: [pixi, index, navigation]
status: stable
generated: { by: claude-opus-5, at: 2026-09-21T01:00:00Z }
verified: { by: process:pixi/0.81.0, at: 2026-09-21T01:00:00Z }
stale_after: 2027-03-21T00:00:00Z
sources:
  - id: primer-docs
    resource: ./
    title: The guides in this directory
---

# Pixi Primer — Where to Look

Two ways in. **Learning order** if you want a course; **by need** if you have a question.
Every guide is a runnable lab that creates its workspace under `sandbox/` at the repo root and
ends with a cleanup step. Prerequisites, the OKF frontmatter format, and conventions are in
the [repository README](../README.md).

---

## Learning order

| # | Guide | Type | Status | What you will do |
|---|---|---|---|---|
| 1 | [Getting Started with Pixi](pixi-getting-started.md) | Tutorial | stable | Install pixi, `pixi init`, add Python and a library, run, shell, understand `pixi.toml` / `pixi.lock` / `.pixi/` |
| 2 | [pixi.toml Manifest Reference](pixi-manifest-reference.md) | Reference | stable | Every table pixi reads, with the CLI command that edits each one |
| 3 | [Managing Dependencies](pixi-dependencies.md) | Tutorial | stable | MatchSpecs, pinning strategies, conda vs PyPI, editable installs, `update` vs `upgrade`, `list` / `tree` |
| 4 | [Pixi Tasks](pixi-tasks.md) | Tutorial | stable | `task add`, `depends-on`, args and templating, `cwd` / `env` / `clean-env`, `inputs` / `outputs` caching, the standard task set |
| 5 | [Features and Environments](pixi-features-environments.md) | Tutorial | stable | Compose `test`, `docs`, and a Python 3.12/3.13/3.14 matrix from features; solve-groups; `no-default-feature` |
| 6 | [The Lockfile and Reproducibility](pixi-lockfile-updates.md) | Tutorial | stable | Read `pixi.lock`, `lock --check`, `--frozen` vs `--locked`, safe updates, export to `environment.yml` / explicit spec |
| 7 | [Multi-Platform Workspaces](pixi-multi-platform.md) | Tutorial | stable | Add platforms, `[target.*]` dependencies and tasks, `system-requirements`, validate other platforms from one machine |
| 8 | [Activation, Shells, and Environment Variables](pixi-activation-shell.md) | Tutorial | stable | `PIXI_*` variables, `[activation]` scripts and env, `pixi shell` vs `shell-hook`, `--clean-env` |
| 9 | [Single-File Scripts and pixi exec](pixi-scripts-exec.md) | Tutorial | stable | `pixi exec` temp environments, PEP 723 scripts with `init --script` / `run --script`, script lockfiles |
| 10 | [Global Tools with pixi global](pixi-global-tools.md) | Playbook | draft | User-wide CLI tools, exposed binaries, `pixi-global.toml`, `sync` — the pipx replacement |
| 11 | [Pixi Configuration](pixi-config.md) | Reference | stable | Config file precedence, `pixi config` CLI, `tls-root-certs`, mirrors, cache, `detached-environments` |
| 12 | [Importing Existing Environments into Pixi](pixi-import-guide.md) | Playbook | stable | Migrate conda `environment.yml`, `requirements.txt`, PEP 621, Poetry, uv, PDM, Pipenv into a workspace |
| 13 | [Pixi in CI with GitHub Actions](pixi-ci-github-actions.md) | Playbook | draft | `setup-pixi`, lock enforcement, matrix over pixi environments, `act`, a multi-stage Dockerfile |
| 14 | [Building Conda Packages with pixi-build](pixi-build-packages.md) | Tutorial | stable (preview feature) | `[package]` table, `pixi-build-python`, path dependencies on your own package, `pixi build` |
| 15 | [Troubleshooting and Maintenance](pixi-troubleshooting.md) | Reference | stable | Diagnostics, cache/env reset ladder, symptom → fix table |

Suggested grouping:

1. **Core loop** — 1 → 3 → 4. After these you can replace `venv` + `pip` + a Makefile.
2. **Real projects** — 5 → 6 → 7 → 8. Multiple environments, a committed lock, other platforms, activation.
3. **Outside the workspace** — 9 → 10 → 11. Scripts, global tools, machine config.
4. **Adoption and delivery** — 12 → 13 → 14. Migrate existing projects, run in CI, ship packages.
5. Keep 2 and 15 open as references throughout.

---

## By need

Find the row that matches what you are trying to do; the link lands on the section that
answers it.

### I have never used pixi

| I want to... | Go to |
|---|---|
| Install pixi and make a first workspace | [Getting Started §1–2](pixi-getting-started.md#1-install-pixi) |
| Understand what `pixi.toml`, `pixi.lock`, and `.pixi/` are and which to commit | [Getting Started §6](pixi-getting-started.md#6-what-got-created) |
| See what every table in `pixi.toml` means | [Manifest Reference](pixi-manifest-reference.md) |
| Know which CLI command edits which manifest table | [Manifest Reference — CLI ↔ table map](pixi-manifest-reference.md#cli--table-map) |
| Replace `venv` + `pip` + a Makefile | Getting Started → [Dependencies](pixi-dependencies.md) → [Tasks](pixi-tasks.md) |

### I am adding or changing dependencies

| I want to... | Go to |
|---|---|
| Add a conda package with a version constraint | [Dependencies §1](pixi-dependencies.md#1-matchspec-basics-conda) |
| Control how `pixi add` pins versions | [Dependencies §2](pixi-dependencies.md#2-pinning-strategies) |
| Add a PyPI-only package, or an editable install of my own code | [Dependencies §3](pixi-dependencies.md#3-pypi-dependencies) |
| Decide between conda-forge and PyPI for a package | [Dependencies §3](pixi-dependencies.md#3-pypi-dependencies), [Manifest Reference — pypi-dependencies](pixi-manifest-reference.md#pypi-dependencies) |
| Add a package only on Linux (or only in a feature) | [Dependencies §4](pixi-dependencies.md#4-platform--feature--and-role-scoped-adds), [Multi-Platform §2](pixi-multi-platform.md#2-platform-conditional-dependencies) |
| Get newer versions — and know whether that means `update` or `upgrade` | [Dependencies §6](pixi-dependencies.md#6-upgrading-vs-updating) |
| See what is installed and why | [Dependencies §7](pixi-dependencies.md#7-inspecting-what-you-have) |
| Use a package from another channel (bioconda, nvidia, pytorch) | [Manifest Reference — workspace](pixi-manifest-reference.md#workspace), [Features §5](pixi-features-environments.md#5-feature-scoped-channels-platforms-and-system-requirements) |

### I am defining commands to run

| I want to... | Go to |
|---|---|
| Add a task and run it | [Tasks §1](pixi-tasks.md#1-add-and-run-a-task) |
| Chain tasks (`ci` runs fmt → lint → test) | [Tasks §2](pixi-tasks.md#2-chaining-with-depends-on) |
| Pass arguments to a task, with defaults | [Tasks §3](pixi-tasks.md#3-arguments) |
| Run a task in a subdirectory or with extra env vars | [Tasks §4](pixi-tasks.md#4-cwd-env-clean-env) |
| Skip a task when its inputs have not changed | [Tasks §5](pixi-tasks.md#5-caching-with-inputs--outputs) |
| Use a different command on Windows vs unix | [Tasks §7](pixi-tasks.md#7-platform-specific-tasks), [Multi-Platform §3](pixi-multi-platform.md#3-platform-conditional-tasks) |
| Write a multi-line task, or know what shell syntax works | [Tasks §8](pixi-tasks.md#8-multi-line-tasks-and-the-shell) |
| Set up the standard `fmt` / `lint` / `check` / `test` / `cov` / `ci` tasks for a Python project | [Tasks §9](pixi-tasks.md#9-the-standard-task-set-python-projects) |

### I need more than one environment

| I want to... | Go to |
|---|---|
| A `test` environment with pytest that the default environment does not carry | [Features §1](pixi-features-environments.md#1-a-test-feature-and-environment) |
| Guarantee `default` and `test` resolve the same package versions | [Features §2](pixi-features-environments.md#2-solve-groups) |
| A lean `docs` or `lint` environment without my runtime deps | [Features §3](pixi-features-environments.md#3-no-default-feature-for-tool-environments) |
| Test against Python 3.12, 3.13, and 3.14 | [Features §4](pixi-features-environments.md#4-a-python-version-matrix) |
| A GPU/CUDA environment that only exists on Linux | [Features §5](pixi-features-environments.md#5-feature-scoped-channels-platforms-and-system-requirements) |
| Run, install, or list a specific environment | `-e <env>` — [Features §1](pixi-features-environments.md#1-a-test-feature-and-environment), [§6](pixi-features-environments.md#6-inspecting-and-removing) |

### I care about reproducibility

| I want to... | Go to |
|---|---|
| Understand what is in `pixi.lock` | [Lockfile §1](pixi-lockfile-updates.md#1-read-the-lockfile) |
| Check the lock matches the manifest (locally or in CI) | [Lockfile §2](pixi-lockfile-updates.md#2-is-the-lock-current) |
| Know when to use `--frozen` vs `--locked` | [Lockfile §3](pixi-lockfile-updates.md#3---frozen-vs---locked) |
| Refresh locked versions without changing the manifest | [Lockfile §4](pixi-lockfile-updates.md#4-updating-safely) |
| Rebuild a broken `.pixi/envs` from the lock | [Lockfile §5](pixi-lockfile-updates.md#5-reinstall-from-lock), [Troubleshooting §2](pixi-troubleshooting.md#2-reset-layers-cheapest-first) |
| Hand an `environment.yml` or explicit spec to a conda-only consumer | [Lockfile §6](pixi-lockfile-updates.md#6-exporting-for-tools-that-do-not-speak-pixi) |
| Lock for Linux/Windows from my Mac | [Multi-Platform §1](pixi-multi-platform.md#1-add-platforms) |
| Tell the solver my hosts have an old glibc / newer macOS / CUDA | [Multi-Platform §4](pixi-multi-platform.md#4-system-requirements) |

### I am working with the shell or environment variables

| I want to... | Go to |
|---|---|
| Know which `PIXI_*` / `CONDA_*` variables are set inside tasks | [Activation §1](pixi-activation-shell.md#1-what-pixi-exports) |
| Export a static variable on every activation | [Activation §2](pixi-activation-shell.md#2-activationenv) |
| Run a script (source an SDK, compute paths) on activation | [Activation §3](pixi-activation-shell.md#3-activation-scripts) |
| Activate in my current shell, a Dockerfile, or an editor — no subshell | [Activation §4](pixi-activation-shell.md#4-pixi-shell-vs-pixi-shell-hook) |
| Prove a task works without variables leaking from my shell | [Activation §5](pixi-activation-shell.md#5-isolation-with---clean-env) |
| Turn off the `(name)` prompt prefix | [Activation §6](pixi-activation-shell.md#6-prompt-and-shell-config) |

### I want to run something without a workspace

| I want to... | Go to |
|---|---|
| Run a tool once, like `uvx` / `npx` | [Scripts & exec §1](pixi-scripts-exec.md#1-pixi-exec) |
| A single Python file that declares its own dependencies (PEP 723) | [Scripts & exec §2](pixi-scripts-exec.md#2-pep-723-scripts) |
| Install a CLI tool user-wide, like `pipx` / `uv tool` | [Global Tools](pixi-global-tools.md) (draft) |
| Several Python versions on my `PATH` as `python3.12`, `python3.14`, ... | [Global Tools §3](pixi-global-tools.md#3-exposing-and-renaming-binaries) |
| Reproduce my global tool set on a new machine | [Global Tools §4](pixi-global-tools.md#4-the-global-manifest) |

### I am configuring pixi itself

| I want to... | Go to |
|---|---|
| Know which config file wins and where they live | [Config §1](pixi-config.md#1-where-config-comes-from) |
| Set a value for this workspace only vs for my user | [Config §2](pixi-config.md#2-the-pixi-config-cli) |
| Fix TLS errors behind a corporate proxy | [Config §3](pixi-config.md#3-keys-worth-knowing), [Troubleshooting §3](pixi-troubleshooting.md#3-symptom--cause--fix) |
| Use a channel mirror or an internal PyPI index | [Config §3](pixi-config.md#3-keys-worth-knowing) |
| Move environments or the cache off a network share | [Config §3](pixi-config.md#3-keys-worth-knowing) |
| Change the default pinning strategy | [Config §3](pixi-config.md#3-keys-worth-knowing), [Dependencies §2](pixi-dependencies.md#2-pinning-strategies) |

### I am migrating an existing project

| I want to... | Go to |
|---|---|
| Import a conda `environment.yml` | [Import Guide §1](pixi-import-guide.md#1-conda-environmentyml---format-conda-env) |
| Import a `requirements.txt` | [Import Guide §2](pixi-import-guide.md#2-pip-requirementstxt---format-pypi-txt) |
| Move from a PEP 621 `pyproject.toml` | [Import Guide §3](pixi-import-guide.md#3-pep-621-pyprojecttoml-projectdependencies) |
| Move from Poetry | [Import Guide §4](pixi-import-guide.md#4-poetry-toolpoetrydependencies-poetrylock) |
| Move from uv | [Import Guide §5](pixi-import-guide.md#5-uv-uvlock-dependency-groups-tooluv) |
| Move from PDM | [Import Guide §6](pixi-import-guide.md#6-pdm-pdmlock-toolpdm) |
| Move from Pipenv | [Import Guide §7](pixi-import-guide.md#7-pipenv-pipfile-pipfilelock) |
| Check I finished the migration properly | [Import Guide — post-import checklist](pixi-import-guide.md#post-import-checklist-all-formats) |

### I am shipping: CI, containers, packages

| I want to... | Go to |
|---|---|
| A GitHub Actions workflow that runs `pixi run ci` | [CI §1](pixi-ci-github-actions.md#1-minimal-workflow) (draft) |
| Fast unit job on every push, full gate before merge, across a Python matrix | [CI §2](pixi-ci-github-actions.md#2-two-tier-layout-fast-unit-job-full-gate) |
| Test on Linux, macOS, and Windows runners | [CI §3](pixi-ci-github-actions.md#3-cross-platform-runners) |
| Fail a PR whose lock is stale | [CI §4](pixi-ci-github-actions.md#4-lockfile-drift-guard-as-a-standalone-job) |
| Run the workflow locally with `act` | [CI §5](pixi-ci-github-actions.md#5-local-ci-with-act) |
| Build a Docker image from a pixi environment | [CI §6](pixi-ci-github-actions.md#6-docker-image-pattern) |
| Build my project into a `.conda` package | [Build Packages](pixi-build-packages.md) (preview feature) |
| Depend on my own package from another workspace in a monorepo | [Build Packages §4](pixi-build-packages.md#4-consuming-the-package-from-another-workspace) |

### Something is wrong

| I want to... | Go to |
|---|---|
| Gather the facts before asking for help | [Troubleshooting §1](pixi-troubleshooting.md#1-gather-facts-first) |
| Clear a cache or environment without nuking everything | [Troubleshooting §2](pixi-troubleshooting.md#2-reset-layers-cheapest-first) |
| Match an error message to a fix | [Troubleshooting §3](pixi-troubleshooting.md#3-symptom--cause--fix) |
| A solve fails with "cannot be installed" for a Python version I added in a feature | [Features §4](pixi-features-environments.md#4-a-python-version-matrix) — feature specs intersect with the default feature |
| `zsh: no matches found: python=3.14.*` | quote the spec — [Troubleshooting §3](pixi-troubleshooting.md#3-symptom--cause--fix) |
| Keep a workspace healthy over time | [Troubleshooting §4](pixi-troubleshooting.md#4-keeping-a-workspace-healthy) |
