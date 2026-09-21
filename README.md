# pixi-primer-sandbox

A hands-on primer for [pixi](https://pixi.prefix.dev/): one markdown guide per topic, each
written as a lab you run locally against a throwaway workspace. The guides live in
[`docs/`](docs/); the index that tells you which one to open is
[**`docs/README.md`**](docs/README.md).

## Prerequisites

- pixi ≥ 0.81 — `curl -fsSL https://pixi.sh/install.sh | sh`, then `pixi --version`
- A POSIX shell; examples use zsh/bash syntax and quote MatchSpecs such as `"python=3.14.*"`
- Network access to conda-forge and PyPI the first time each lab runs

## Using the sandbox

```sh
git clone <this repo> && cd pixi-primer-sandbox
cp -r labs/<lab> sandbox/ && cd sandbox/<lab>     # each guide's Setup section names its lab
```

`labs/` holds the pristine starting state of every lab (starter scripts, fixtures,
`pyproject.toml` files); `sandbox/` is where you actually work and is gitignored apart from
its `.gitkeep`. Each guide ends with a cleanup step that removes its sandbox workspace, and
`rm -rf sandbox/<lab> && cp -r labs/<lab> sandbox/` restarts one from scratch. Labs are independent of one another; `docs/README.md` gives a recommended
order for readers who want a course and a by-question lookup for readers who want an answer.

## Repository layout

```
README.md          this file: what the repo is, how to use it, document conventions
docs/README.md     the index: learning order, "I want to..." lookup, list of all guides
docs/pixi-*.md     the guides
labs/README.md     index of lab directories and what each ships
labs/<lab>/        pristine starter files for one lab — copy, never edit in place
sandbox/           where copied labs are worked on (gitignored except .gitkeep)
LICENSE
```

## Document format

Every guide starts with Open Knowledge Format (OKF) YAML frontmatter:

```yaml
---
type: Tutorial | Reference | Playbook
title: ...
description: ...
tags: [...]
status: draft | stable
generated: { by: <agent>, at: <ISO-8601> }
verified:  { by: <human:name | process:tool/version>, at: <ISO-8601> }   # absent on drafts
stale_after: <ISO-8601>
sources:
  - id: ...
    resource: <url | cli:tool/version/subcommand>
    title: ...
---
```

- `status: stable` with `verified.by: process:pixi/<version>` means every command in the
  guide was executed against that pixi binary when the guide was written.
- `status: draft` means the guide was written from `--help` output and upstream docs but its
  lab has not been run. To promote it: run the lab, fix what differs, add a `verified` line,
  flip `status`.
- When `stale_after` passes, re-run the lab against the current pixi before relying on it.

## Conventions used in every guide

- `pixi init` creates manifests; `pixi add`, `pixi task add`, `pixi workspace ...` edit them.
  Hand-edits are called out explicitly.
- `pixi.toml` holds pixi configuration; `pyproject.toml` holds Python tool configuration.
  `pixi init --format pyproject` is not used.
- conda-forge first; `--pypi` only for packages absent from conda-forge.
- Python is always invoked as `pixi run python ...`, never bare.

## License

[MIT](LICENSE)
